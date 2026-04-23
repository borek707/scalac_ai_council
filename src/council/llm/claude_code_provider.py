from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import AsyncGenerator, Optional

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff

logger = logging.getLogger(__name__)


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
        executable_path: Optional[str] = None,
        model: Optional[str] = None,
        work_dir: Optional[str] = None,
    ) -> None:
        self.model = model or "claude-sonnet-4-6"
        self.work_dir = work_dir
        self._http_client: Optional[object] = None

        # Try subprocess first
        self.executable_path = executable_path or self._detect_executable()
        if self.executable_path and os.path.isfile(self.executable_path):
            logger.info("ClaudeCodeProvider using subprocess mode (%s)", self.executable_path)
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
    def _detect_executable() -> Optional[str]:
        """Try to locate the ``claude`` binary."""
        env_path = os.environ.get("CLAUDE_CLI_PATH")
        if env_path and os.path.isfile(env_path):
            return env_path

        path_claude = shutil.which("claude")
        if path_claude:
            return path_claude

        return None

    @staticmethod
    def _read_oauth_token() -> Optional[str]:
        """Read the OAuth access token from Claude Code's credential store."""
        creds_path = Path.home() / ".claude" / ".credentials.json"
        if not creds_path.is_file():
            return None

        try:
            data = json.loads(creds_path.read_text(encoding="utf-8"))
            return data.get("claudeAiOauth", {}).get("accessToken")
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
        model: Optional[str] = None,
        system: Optional[str] = None,
    ) -> list[str]:
        """Build the subprocess command for Claude CLI."""
        assert self.executable_path
        cmd = [self.executable_path, "-p"]

        if self.work_dir:
            cmd += ["--work-dir", self.work_dir]

        explicit_model = model or self.model
        if explicit_model:
            cmd += ["--model", explicit_model]

        # Claude CLI -p accepts the prompt as a positional arg
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"

        cmd.append(full_prompt)
        return cmd

    # ── Subprocess generation ───────────────────────────────────────────

    @retry_with_backoff(max_retries=2, exceptions=(Exception,))
    async def _generate_subprocess(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
    ) -> LLMResponse:
        cmd = self._build_cmd(prompt, model=model, system=system)
        start = time.time()

        logger.debug("ClaudeCodeProvider executing: %s", " ".join(cmd))

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_bytes, stderr_bytes = await proc.communicate()
        latency = (time.time() - start) * 1000

        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")

        if proc.returncode != 0:
            logger.error(
                "Claude CLI exited with code %d. stderr: %s",
                proc.returncode,
                stderr[:500],
            )
            raise RuntimeError(
                f"Claude CLI failed (exit {proc.returncode}): {stderr[:500]}"
            )

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

    @retry_with_backoff(max_retries=2, exceptions=(Exception,))
    async def _generate_http(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> LLMResponse:
        if self._http_client is None:
            raise RuntimeError("HTTP client not initialised")

        start = time.time()
        msg = await self._http_client.messages.create(
            model=model or self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        latency = (time.time() - start) * 1000

        content = ""
        if msg.content:
            content = msg.content[0].text if hasattr(msg.content[0], "text") else str(msg.content[0])

        return LLMResponse(
            content=content,
            model=msg.model,
            tokens_prompt=msg.usage.input_tokens if msg.usage else 0,
            tokens_completion=msg.usage.output_tokens if msg.usage else 0,
            cost_usd=0.0,
            latency_ms=latency,
        )

    # ── Public API ──────────────────────────────────────────────────────

    @retry_with_backoff(max_retries=2, exceptions=(Exception,))
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> LLMResponse:
        if self.executable_path:
            return await self._generate_subprocess(prompt, model=model, system=system)
        return await self._generate_http(
            prompt, model=model, temperature=temperature, max_tokens=max_tokens, system=system
        )

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        response = await self.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system,
        )
        if response.content:
            yield response.content
