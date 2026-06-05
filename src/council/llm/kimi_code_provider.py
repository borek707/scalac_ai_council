from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
import time
from collections.abc import AsyncIterator
from pathlib import Path

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff

logger = logging.getLogger(__name__)

_RESUME_SESSION_RE = re.compile(r"^To resume this session:.*$", re.MULTILINE)


class KimiCodeProvider(LLMProvider):
    """LLM provider backed by the local Kimi Code CLI.

    This provider spawns the ``kimi`` binary in non-interactive print mode
    (``kimi --quiet --yolo --prompt "..."``) and returns the generated text.

    Because Kimi Code is a full *agent* (not a raw LLM endpoint) it may
    internally read files, run terminal commands, etc.  The ``--yolo`` flag
    auto-approves those actions, so the provider behaves like a deterministic
    text generator.

    Environment detection
        The provider auto-discovers the ``kimi`` executable in the following
        order:
        1. ``KIMI_CLI_PATH`` environment variable
        2. ``$PATH`` lookup (``shutil.which("kimi")``)
        3. VS Code global-storage path used by the Kimi Code extension

    Configuration
        ``--model`` is forwarded via ``--model`` if given, otherwise the default
        from ``~/.kimi/config.toml`` is used.
    """

    def __init__(
        self,
        executable_path: str | None = None,
        model: str | None = None,
        work_dir: str | None = None,
    ) -> None:
        self.model = model or "kimi-for-coding"
        self.executable_path = executable_path or self._detect_executable()
        self.work_dir = work_dir

        if not self.executable_path or not os.path.isfile(self.executable_path):
            raise RuntimeError(
                "Kimi Code CLI binary not found. "
                "Set KIMI_CLI_PATH or ensure 'kimi' is on your PATH."
            )

    @staticmethod
    def _detect_executable() -> str | None:
        """Try to locate the ``kimi`` binary."""
        env_path = os.environ.get("KIMI_CLI_PATH")
        if env_path and os.path.isfile(env_path):
            return env_path

        path_kimi = shutil.which("kimi")
        if path_kimi:
            return path_kimi

        # VS Code extension default install location
        vscode_path = (
            Path.home()
            / ".vscode-remote"
            / "data"
            / "User"
            / "globalStorage"
            / "moonshot-ai.kimi-code"
            / "bin"
            / "kimi"
            / "kimi"
        )
        if vscode_path.is_file():
            return str(vscode_path)

        # Also try the non-remote VS Code path
        local_vscode_path = (
            Path.home()
            / ".vscode"
            / "extensions"
            / "moonshot-ai.kimi-code-*"
            / "bin"
            / "kimi"
            / "kimi"
        )
        import glob

        matches = glob.glob(str(local_vscode_path))
        if matches and os.path.isfile(matches[0]):
            return matches[0]

        return None

    def _build_cmd(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
    ) -> list[str]:
        """Build the subprocess command for Kimi CLI."""
        assert self.executable_path is not None
        cmd = [self.executable_path, "--quiet", "--yolo"]

        if self.work_dir:
            cmd += ["--work-dir", self.work_dir]

        # Kimi CLI does not have a native --system flag; we prepend the system
        # prompt to the user prompt when one is provided.
        full_prompt = prompt
        if system:
            full_prompt = f"[System Instruction]\n{system}\n\n[User Prompt]\n{prompt}"

        cmd += ["--prompt", full_prompt]

        # Only forward --model when explicitly overridden; otherwise let the
        # CLI use its configured default (avoids "LLM not set" errors).
        explicit_model = model or self.model
        if explicit_model and explicit_model != "kimi-for-coding":
            cmd += ["--model", explicit_model]

        return cmd

    @staticmethod
    def _clean_output(raw: str) -> str:
        """Remove the resume-session trailer and surrounding whitespace."""
        cleaned = _RESUME_SESSION_RE.sub("", raw)
        return cleaned.strip()

    @retry_with_backoff(
        max_retries=2,
        exceptions=(Exception,),
        non_retryable_exceptions=(ValueError, FileNotFoundError, PermissionError),
    )
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        """Generate a response by invoking Kimi Code CLI."""
        cmd = self._build_cmd(prompt, model=model, system=system)
        start = time.time()

        # Redact the prompt argument to avoid exposing full prompt text in logs
        safe_cmd = cmd[:-1] + [f"<prompt:{len(cmd[-1])}chars>"]
        logger.debug("KimiCodeProvider executing: %s", " ".join(safe_cmd))

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Kimi CLI can take a long time on large workspaces; cap single call at 2 min
        stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=120.0)
        latency = (time.time() - start) * 1000

        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")

        if proc.returncode != 0:
            logger.error(
                "Kimi CLI exited with code %d. stderr: %s",
                proc.returncode,
                stderr[:500],
            )
            raise RuntimeError(f"Kimi CLI failed (exit {proc.returncode}): {stderr[:500]}")

        content = self._clean_output(stdout)

        # Kimi CLI does not expose token counts in quiet mode; we fall back to
        # rough character-based heuristics for token estimates in LLMResponse.
        tokens_prompt = len(prompt) // 4
        tokens_completion = len(content) // 4

        return LLMResponse(
            content=content,
            model=model or self.model,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            cost_usd=0.0,
            latency_ms=latency,
        )

    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        # Kimi CLI has no streaming mode — it prints the full response only after
        # the request finishes. We yield it as one chunk so the interface is consistent,
        # but there will be no visible token-by-token output.
        response = await self.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system,
        )
        if response.content:
            yield response.content
