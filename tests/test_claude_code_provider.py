from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from council.llm.claude_code_provider import ClaudeCodeProvider
from council.llm.provider import LLMResponse


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
                with patch.object(
                    ClaudeCodeProvider, "_init_http_client"
                ) as mock_init:
                    provider = ClaudeCodeProvider()
                    mock_init.assert_called_once_with("fake-oauth-token")

    def test_read_oauth_token_success(self, tmp_path: Path) -> None:
        creds = tmp_path / ".claude" / ".credentials.json"
        creds.parent.mkdir(parents=True, exist_ok=True)
        creds.write_text(
            json.dumps({"claudeAiOauth": {"accessToken": "secret-123"}}),
            encoding="utf-8",
        )

        with patch(
            "council.llm.claude_code_provider.Path.home", return_value=tmp_path
        ):
            token = ClaudeCodeProvider._read_oauth_token()
            assert token == "secret-123"

    def test_read_oauth_token_missing_file(self, tmp_path: Path) -> None:
        with patch(
            "council.llm.claude_code_provider.Path.home", return_value=tmp_path
        ):
            token = ClaudeCodeProvider._read_oauth_token()
            assert token is None

    def test_read_oauth_token_malformed_json(self, tmp_path: Path) -> None:
        creds = tmp_path / ".claude" / ".credentials.json"
        creds.parent.mkdir(parents=True, exist_ok=True)
        creds.write_text("not json", encoding="utf-8")

        with patch(
            "council.llm.claude_code_provider.Path.home", return_value=tmp_path
        ):
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

    @pytest.mark.asyncio
    async def test_generate_subprocess_success(self, tmp_path: Path) -> None:
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(
            return_value=(b"Test response", b"")
        )

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_proc
        ):
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
        mock_proc.communicate = AsyncMock(
            return_value=(b"", b"error: something went wrong")
        )

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_proc
        ):
            with pytest.raises(RuntimeError, match="Claude CLI failed"):
                await provider._generate_subprocess("prompt")

    @pytest.mark.asyncio
    async def test_stream_yields_content(self, tmp_path: Path) -> None:
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(
            return_value=(b"Streamed text", b"")
        )

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_proc
        ):
            chunks = []
            async for chunk in provider.stream("prompt"):
                chunks.append(chunk)
            assert chunks == ["Streamed text"]
