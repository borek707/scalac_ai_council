from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import time
from collections.abc import AsyncIterator
from pathlib import Path

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff

logger = logging.getLogger(__name__)


class ProviderTimeoutError(RuntimeError):
    """Raised when a local CLI provider call exceeds its configured timeout."""


def _anthropic_non_retryable() -> tuple[type[Exception], ...]:
    """Return non-retryable Anthropic exception types when the SDK is available."""
    types: list[type[Exception]] = [
        ValueError,
        FileNotFoundError,
        PermissionError,
        ProviderTimeoutError,
    ]
    try:
        import anthropic as _anthropic

        types.append(_anthropic.AuthenticationError)
        types.append(_anthropic.PermissionDeniedError)
        types.append(_anthropic.NotFoundError)
        types.append(_anthropic.BadRequestError)
    except ImportError:
        pass
    return tuple(types)


class ClaudeCodeProvider(LLMProvider):
    """LLM provider backed by Claude Code IDE / CLI.

    This provider has two strategies, tried in order:

    1. **Subprocess** — if the ``claude`` CLI is installed, it runs
       ``claude -p "<prompt>"`` in non-interactive print mode.

    2. **HTTP fallback** — if the CLI is not available, it reads the OAuth
       token from Claude Code's credential store
       (``~/.claude/.credentials.json``) and calls the Anthropic API
       directly via the ``anthropic`` SDK.

    Because Claude Code is an *agent* (not a raw LLM endpoint) the subprocess
    mode may internally read files or run commands.  Use ``--allowedTools``
    if you need read-only behaviour.
    """

    def __init__(
        self,
        executable_path: str | None = None,
        model: str | None = None,
        work_dir: str | None = None,
        call_timeout: float = 120.0,
    ) -> None:
        self.model = model or "claude-sonnet-4-6"
        self.work_dir = work_dir
        self.call_timeout = call_timeout
        self._http_client: object | None = None

        # Try subprocess first
        self.executable_path = executable_path or self._detect_executable()
        if self.executable_path and os.path.isfile(self.executable_path):
            logger.info("ClaudeCodeProvider using subprocess mode (%s)", self.executable_path)
            # Also initialise HTTP client so long-prompt fallback works across all rounds
            token = self._read_oauth_token()
            if token:
                self._init_http_client(token)
                logger.info(
                    "ClaudeCodeProvider: HTTP fallback initialised for prompts exceeding subprocess limit"
                )
            return

        # Fallback: try to read OAuth token and use Anthropic SDK
        token = self._read_oauth_token()
        if token:
            self._init_http_client(token)
            logger.info("ClaudeCodeProvider using HTTP fallback (OAuth token from ~/.claude)")
            return

        raise RuntimeError(
            "Claude Code provider could not find a working strategy.\n"
            "Either install the Claude CLI (npm install -g @anthropic-ai/claude-code) "
            "or ensure Claude Code IDE has stored OAuth credentials in ~/.claude/.credentials.json"
        )

    @staticmethod
    def _detect_executable() -> str | None:
        """Try to locate the ``claude`` binary."""
        env_path = os.environ.get("CLAUDE_CLI_PATH")
        if env_path and os.path.isfile(env_path):
            return env_path

        path_claude = shutil.which("claude")
        if path_claude:
            return path_claude

        return None

    @staticmethod
    def _read_oauth_token() -> str | None:
        """Read the OAuth access token from Claude Code's credential store."""
        creds_path = Path.home() / ".claude" / ".credentials.json"
        if not creds_path.is_file():
            return None

        try:
            data = json.loads(creds_path.read_text(encoding="utf-8"))
            token = data.get("claudeAiOauth", {}).get("accessToken")
            return str(token) if token is not None else None
        except (json.JSONDecodeError, OSError, KeyError) as exc:
            logger.debug("Could not read Claude OAuth token: %s", exc)
            return None

    def _init_http_client(self, token: str) -> None:
        """Initialise the Anthropic SDK client with the OAuth token."""
        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:
            raise ImportError(
                "Claude Code HTTP fallback requires the 'anthropic' package. "
                "Install with: pip install anthropic"
            ) from exc

        self._http_client = AsyncAnthropic(api_key=token)

    def _build_cmd(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        streaming: bool = False,
    ) -> list[str]:
        """Build the subprocess command for Claude CLI."""
        assert self.executable_path
        cmd = [self.executable_path, "-p"]

        if self.work_dir:
            cmd += ["--work-dir", self.work_dir]

        explicit_model = model or self.model
        if explicit_model:
            cmd += ["--model", explicit_model]

        if streaming:
            # stream-json emits one JSON line per token so we can show live output
            cmd += ["--output-format", "stream-json", "--include-partial-messages", "--verbose"]

        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"

        cmd.append(full_prompt)
        return cmd

    # ── Subprocess generation ───────────────────────────────────────────

    @retry_with_backoff(
        max_retries=2,
        exceptions=(Exception,),
        non_retryable_exceptions=(
            ValueError,
            FileNotFoundError,
            PermissionError,
            ProviderTimeoutError,
        ),
    )
    async def _generate_subprocess(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
    ) -> LLMResponse:
        cmd = self._build_cmd(prompt, model=model, system=system)
        start = time.time()

        # Redact the prompt argument to avoid exposing full prompt text in logs
        safe_cmd = cmd[:-1] + [f"<prompt:{len(cmd[-1])}chars>"]
        logger.debug("ClaudeCodeProvider executing: %s", " ".join(safe_cmd))

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.call_timeout,
            )
        except TimeoutError as exc:
            proc.kill()
            raise ProviderTimeoutError(
                f"Claude Code provider timed out after {self.call_timeout:g}s "
                "while waiting for the Claude CLI response. "
                "Increase --timeout or use fewer rounds / a faster provider."
            ) from exc
        latency = (time.time() - start) * 1000

        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")

        if proc.returncode != 0:
            logger.error(
                "Claude CLI exited with code %d. stderr: %s",
                proc.returncode,
                stderr[:500],
            )
            raise RuntimeError(f"Claude CLI failed (exit {proc.returncode}): {stderr[:500]}")

        tokens_prompt = len(prompt) // 4
        tokens_completion = len(stdout) // 4

        return LLMResponse(
            content=stdout.strip(),
            model=model or self.model,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            cost_usd=0.0,
            latency_ms=latency,
        )

    # ── HTTP fallback generation ────────────────────────────────────────

    @retry_with_backoff(
        max_retries=2,
        exceptions=(Exception,),
        non_retryable_exceptions=_anthropic_non_retryable(),
    )
    async def _generate_http(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        if self._http_client is None:
            raise RuntimeError("HTTP client not initialised")

        start = time.time()
        msg = await self._http_client.messages.create(  # type: ignore[attr-defined]
            model=model or self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        latency = (time.time() - start) * 1000

        content = ""
        if msg.content:
            content = (
                msg.content[0].text if hasattr(msg.content[0], "text") else str(msg.content[0])
            )

        return LLMResponse(
            content=content,
            model=msg.model,
            tokens_prompt=msg.usage.input_tokens if msg.usage else 0,
            tokens_completion=msg.usage.output_tokens if msg.usage else 0,
            cost_usd=0.0,
            latency_ms=latency,
        )

    # ── Public API ──────────────────────────────────────────────────────

    # Prompts longer than this are routed to HTTP instead of subprocess
    # to avoid ARG_MAX / CLI parsing issues.
    _SUBPROCESS_PROMPT_LIMIT: int = 50_000

    @retry_with_backoff(
        max_retries=2,
        exceptions=(Exception,),
        non_retryable_exceptions=_anthropic_non_retryable(),
    )
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        if self.executable_path and len(prompt) < self._SUBPROCESS_PROMPT_LIMIT:
            return await self._generate_subprocess(prompt, model=model, system=system)

        if len(prompt) >= self._SUBPROCESS_PROMPT_LIMIT and self.executable_path:
            logger.warning(
                "Prompt %d chars exceeds subprocess limit (%d); " "falling back to HTTP",
                len(prompt),
                self._SUBPROCESS_PROMPT_LIMIT,
            )

        return await self._generate_http(
            prompt, model=model, temperature=temperature, max_tokens=max_tokens, system=system
        )

    async def _stream_subprocess(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        cmd = self._build_cmd(prompt, model=model, system=system, streaming=True)
        safe_cmd = cmd[:-1] + [f"<prompt:{len(cmd[-1])}chars>"]
        logger.debug("ClaudeCodeProvider streaming subprocess: %s", " ".join(safe_cmd))

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert proc.stdout is not None

        try:
            while True:
                line_bytes = await asyncio.wait_for(
                    proc.stdout.readline(),
                    timeout=self.call_timeout,
                )
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if (
                    event.get("type") == "stream_event"
                    and event.get("event", {}).get("type") == "content_block_delta"
                    and event.get("event", {}).get("delta", {}).get("type") == "text_delta"
                ):
                    text = event["event"]["delta"].get("text", "")
                    if text:
                        yield text
        except TimeoutError:
            proc.kill()
            raise ProviderTimeoutError(
                f"Claude Code provider streaming timed out after {self.call_timeout:g}s. "
                "Increase --timeout or use fewer rounds / a faster provider."
            )

        await proc.wait()
        if proc.returncode != 0:
            assert proc.stderr is not None
            stderr_bytes = await proc.stderr.read()
            stderr = stderr_bytes.decode("utf-8", errors="replace")
            raise RuntimeError(f"Claude CLI failed (exit {proc.returncode}): {stderr[:500]}")

    async def _stream_http(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        if self._http_client is None:
            raise RuntimeError("HTTP client not initialised")

        async with self._http_client.messages.stream(  # type: ignore[attr-defined]
            model=model or self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        if self.executable_path and len(prompt) < self._SUBPROCESS_PROMPT_LIMIT:
            async for chunk in self._stream_subprocess(prompt, model=model, system=system):
                yield chunk
            return

        async for chunk in self._stream_http(
            prompt, model=model, temperature=temperature, max_tokens=max_tokens, system=system
        ):
            yield chunk
