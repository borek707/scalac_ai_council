from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
import time
from pathlib import Path
from typing import AsyncGenerator, Optional

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
        executable_path: Optional[str] = None,
        model: Optional[str] = None,
        work_dir: Optional[str] = None,
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
    def _detect_executable() -> Optional[str]:
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
        model: Optional[str] = None,
        system: Optional[str] = None,
    ) -> list[str]:
        """Build the subprocess command for Kimi CLI."""
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

    @retry_with_backoff(max_retries=2, exceptions=(Exception,))
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> LLMResponse:
        """Generate a response by invoking Kimi Code CLI."""
        cmd = self._build_cmd(prompt, model=model, system=system)
        start = time.time()

        logger.debug("KimiCodeProvider executing: %s", " ".join(cmd))

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
                "Kimi CLI exited with code %d. stderr: %s",
                proc.returncode,
                stderr[:500],
            )
            raise RuntimeError(
                f"Kimi CLI failed (exit {proc.returncode}): {stderr[:500]}"
            )

        content = self._clean_output(stdout)

        # Kimi CLI does not expose token counts in quiet mode; we fall back to
        # rough character-based heuristics so the CostTracker can still work.
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
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a response.

        Kimi CLI quiet mode returns the full response at once, so we yield the
        entire text as a single chunk.
        """
        response = await self.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system,
        )
        if response.content:
            yield response.content
