from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from council.llm.claude_code_provider import ClaudeCodeProvider


class TestClaudeCodeProvider:
    """Tests for ClaudeCodeProvider."""

    def test_raises_when_no_strategy_available(self) -> None:
        with patch.object(ClaudeCodeProvider, "_detect_executable", return_value=None):
            with patch.object(ClaudeCodeProvider, "_read_oauth_token", return_value=None):
                with pytest.raises(RuntimeError, match="Claude Code provider"):
                    ClaudeCodeProvider()

    def test_subprocess_mode_when_executable_found(self, tmp_path: Path) -> None:
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash\necho hello")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))
        assert provider.executable_path == str(fake_cli)

    def test_http_mode_when_token_found(self, tmp_path: Path) -> None:
        creds = tmp_path / ".credentials.json"
        creds.write_text(
            json.dumps({"claudeAiOauth": {"accessToken": "fake-oauth-token"}}),
            encoding="utf-8",
        )

        with patch.object(ClaudeCodeProvider, "_detect_executable", return_value=None):
            with patch.object(
                ClaudeCodeProvider,
                "_read_oauth_token",
                return_value="fake-oauth-token",
            ):
                with patch.object(ClaudeCodeProvider, "_init_http_client") as mock_init:
                    provider = ClaudeCodeProvider()
                    mock_init.assert_called_once_with("fake-oauth-token")

    def test_read_oauth_token_success(self, tmp_path: Path) -> None:
        creds = tmp_path / ".claude" / ".credentials.json"
        creds.parent.mkdir(parents=True, exist_ok=True)
        creds.write_text(
            json.dumps({"claudeAiOauth": {"accessToken": "secret-123"}}),
            encoding="utf-8",
        )

        with patch("council.llm.claude_code_provider.Path.home", return_value=tmp_path):
            token = ClaudeCodeProvider._read_oauth_token()
            assert token == "secret-123"

    def test_read_oauth_token_missing_file(self, tmp_path: Path) -> None:
        with patch("council.llm.claude_code_provider.Path.home", return_value=tmp_path):
            token = ClaudeCodeProvider._read_oauth_token()
            assert token is None

    def test_read_oauth_token_malformed_json(self, tmp_path: Path) -> None:
        creds = tmp_path / ".claude" / ".credentials.json"
        creds.parent.mkdir(parents=True, exist_ok=True)
        creds.write_text("not json", encoding="utf-8")

        with patch("council.llm.claude_code_provider.Path.home", return_value=tmp_path):
            token = ClaudeCodeProvider._read_oauth_token()
            assert token is None

    def test_build_cmd_with_system(self, tmp_path: Path) -> None:
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli), model="claude-opus")
        cmd = provider._build_cmd("Hello", system="You are a marketer")
        assert cmd[0] == str(fake_cli)
        assert cmd[1] == "-p"
        assert "--model" in cmd
        assert "claude-opus" in cmd
        assert "You are a marketer" in cmd[-1]
        assert "Hello" in cmd[-1]

    def test_build_cmd_without_system(self, tmp_path: Path) -> None:
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))
        cmd = provider._build_cmd("Hello")
        assert cmd[-1] == "Hello"

    def test_call_timeout_is_configurable(self, tmp_path: Path) -> None:
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli), call_timeout=600.0)
        assert provider.call_timeout == 600.0

    @pytest.mark.asyncio
    async def test_generate_subprocess_timeout_has_context(self, tmp_path: Path) -> None:
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli), call_timeout=0.01)

        mock_proc = MagicMock()
        mock_proc.kill = MagicMock()
        mock_proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError)

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with pytest.raises(RuntimeError, match="Claude Code provider timed out after 0.01s"):
                await provider._generate_subprocess("prompt")
        mock_proc.kill.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_subprocess_success(self, tmp_path: Path) -> None:
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"Test response", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            resp = await provider._generate_subprocess("prompt")
            assert resp.content == "Test response"
            assert resp.model == "claude-sonnet-4-6"

    @pytest.mark.asyncio
    async def test_generate_subprocess_failure(self, tmp_path: Path) -> None:
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))

        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.communicate = AsyncMock(return_value=(b"", b"error: something went wrong"))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with pytest.raises(RuntimeError, match="Claude CLI failed"):
                await provider._generate_subprocess("prompt")

    @pytest.mark.asyncio
    async def test_stream_yields_content(self, tmp_path: Path) -> None:
        """stream() parses stream-json lines and yields only text_delta chunks."""
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))

        # Build realistic stream-json lines the CLI emits
        text_delta = (
            json.dumps(
                {
                    "type": "stream_event",
                    "event": {
                        "type": "content_block_delta",
                        "index": 1,
                        "delta": {"type": "text_delta", "text": "Hello"},
                    },
                }
            ).encode()
            + b"\n"
        )
        text_delta2 = (
            json.dumps(
                {
                    "type": "stream_event",
                    "event": {
                        "type": "content_block_delta",
                        "index": 1,
                        "delta": {"type": "text_delta", "text": " world"},
                    },
                }
            ).encode()
            + b"\n"
        )
        # Non-text event that should be ignored
        rate_limit = json.dumps({"type": "rate_limit_event"}).encode() + b"\n"

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = MagicMock()
        mock_proc.stdout.readline = AsyncMock(
            side_effect=[text_delta, rate_limit, text_delta2, b""]
        )
        mock_proc.stderr = MagicMock()
        mock_proc.wait = AsyncMock(return_value=0)

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            chunks = []
            async for chunk in provider.stream("prompt"):
                chunks.append(chunk)
        assert chunks == ["Hello", " world"]

    @pytest.mark.asyncio
    async def test_stream_ignores_non_text_events(self, tmp_path: Path) -> None:
        """stream() skips thinking_delta, rate_limit, system, and result events."""
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))

        non_text_events = [
            json.dumps({"type": "system", "subtype": "init"}).encode() + b"\n",
            json.dumps(
                {
                    "type": "stream_event",
                    "event": {
                        "type": "content_block_delta",
                        "index": 0,
                        "delta": {"type": "thinking_delta", "thinking": "thoughts"},
                    },
                }
            ).encode()
            + b"\n",
            json.dumps({"type": "result", "subtype": "success", "result": "final"}).encode()
            + b"\n",
            json.dumps(
                {
                    "type": "stream_event",
                    "event": {
                        "type": "content_block_delta",
                        "index": 1,
                        "delta": {"type": "text_delta", "text": "actual output"},
                    },
                }
            ).encode()
            + b"\n",
            b"",
        ]

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = MagicMock()
        mock_proc.stdout.readline = AsyncMock(side_effect=non_text_events)
        mock_proc.stderr = MagicMock()
        mock_proc.wait = AsyncMock(return_value=0)

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            chunks = []
            async for chunk in provider.stream("prompt"):
                chunks.append(chunk)
        assert chunks == ["actual output"]

    @pytest.mark.asyncio
    async def test_stream_subprocess_uses_stream_json_flags(self, tmp_path: Path) -> None:
        """_build_cmd with streaming=True includes the stream-json flags."""
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))
        cmd = provider._build_cmd("prompt", streaming=True)
        assert "--output-format" in cmd
        assert "stream-json" in cmd
        assert "--include-partial-messages" in cmd
        assert "--verbose" in cmd

    @pytest.mark.asyncio
    async def test_stream_subprocess_default_no_stream_flags(self, tmp_path: Path) -> None:
        """_build_cmd without streaming=True does NOT include stream-json flags."""
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))
        cmd = provider._build_cmd("prompt")
        assert "--output-format" not in cmd
        assert "--include-partial-messages" not in cmd

    @pytest.mark.asyncio
    async def test_prompt_not_in_debug_log(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Full prompt text must NOT appear in debug logs; <prompt:Nchars> MUST (Issue #17)."""
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))

        long_prompt = "B" * 200  # distinct long prompt

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"response text", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with caplog.at_level(logging.DEBUG, logger="council.llm.claude_code_provider"):
                await provider._generate_subprocess(long_prompt)

        assert long_prompt not in caplog.text
        assert "<prompt:" in caplog.text
