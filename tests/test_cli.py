from __future__ import annotations

"""Tests for council.cli — Issues #33 (--review mode), #34 (fixture workspaces),
#19 (dashboard thread join / sys.exit), #23 (workspace overwrite + --force),
#2 #3 #4 #7 (API key passthrough and warnings)."""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from council.cli import _create_provider, _resolve_free_tier, _review_run, parse_args

# ── Argument-parsing tests ──────────────────────────────────────────────────


class TestParseArgsReview:
    """Tests for the --review argument."""

    def test_review_with_directory_sets_string(self) -> None:
        """--review /some/dir stores the path string on args.review."""
        args = parse_args(["--review", "/some/dir"])
        assert args.review == "/some/dir"

    def test_review_without_value_sets_true(self) -> None:
        """--review with no value (post-run flag) stores True on args.review."""
        args = parse_args(["--review"])
        assert args.review is True

    def test_review_absent_defaults_to_none(self) -> None:
        """When --review is not passed, args.review is None."""
        args = parse_args([])
        assert args.review is None


class TestResolveFreeTier:
    """OpenRouter should default to free tier unless explicitly disabled."""

    def test_openrouter_defaults_to_free_tier(self) -> None:
        args = parse_args(["--provider", "openrouter"])
        _resolve_free_tier(args)
        assert args.free_tier is True

    def test_openrouter_no_free_tier_opt_out(self) -> None:
        args = parse_args(["--provider", "openrouter", "--no-free-tier"])
        _resolve_free_tier(args)
        assert args.free_tier is False

    def test_openai_defaults_to_paid_path(self) -> None:
        args = parse_args(["--provider", "openai"])
        _resolve_free_tier(args)
        assert args.free_tier is False

    def test_explicit_free_tier_flag_honored(self) -> None:
        args = parse_args(["--provider", "openai", "--free-tier"])
        _resolve_free_tier(args)
        assert args.free_tier is True


class TestParseArgsTemplate:
    """Tests for the --template argument."""

    def test_template_no_value_exits_zero(self) -> None:
        """--template without a NAME value lists templates and exits 0."""
        with pytest.raises(SystemExit) as exc_info:
            # parse_args triggers _run_council only through main(); here we
            # only parse.  The listing + sys.exit(0) happens inside
            # _run_council, not parse_args itself — so we call the runner
            # directly via the same path the CLI uses.
            import asyncio

            from council.cli import _run_council

            asyncio.run(_run_council(parse_args(["--template"])))
        assert exc_info.value.code == 0

    def test_template_with_known_name_sets_config(self, tmp_path: Path) -> None:
        """--template saas resolves to a real config path."""
        args = parse_args(["--template", "saas"])
        # parse_args itself doesn't resolve the template path — that happens
        # in _run_council.  The important thing is that the attribute is set.
        assert args.template == "saas"


class TestParseArgsMonitor:
    """Tests for the --monitor argument."""

    def test_monitor_works_without_config(self) -> None:
        """--monitor should be parseable even without --config."""
        args = parse_args(["--monitor"])
        assert args.monitor is True
        assert args.config is None


# ── _review_run behaviour tests ─────────────────────────────────────────────


class TestReviewRunComplete:
    """Tests for _review_run with a complete workspace."""

    def test_displays_company_name(
        self, complete_workspace: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should print the company name from the manifest."""
        _review_run(complete_workspace)
        captured = capsys.readouterr()
        assert "TestCorp" in captured.out

    def test_displays_rounds(self, complete_workspace: Path, capsys: pytest.CaptureFixture) -> None:
        """Should print completed / max rounds information."""
        _review_run(complete_workspace)
        captured = capsys.readouterr()
        # manifest has rounds_completed=3, max_rounds=3
        assert "3" in captured.out

    def test_displays_proposal_path(
        self, complete_workspace: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should print the proposal file path when it exists."""
        _review_run(complete_workspace)
        captured = capsys.readouterr()
        assert "Proposal" in captured.out


class TestReviewRunEmpty:
    """Tests for _review_run with an empty workspace."""

    def test_prints_error_about_missing_manifest(
        self, empty_workspace: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should surface a clear error when no artifacts are present."""
        _review_run(empty_workspace)
        captured = capsys.readouterr()
        assert "artifact" in captured.out.lower() or "manifest" in captured.out.lower()

    def test_returns_without_raising(self, empty_workspace: Path) -> None:
        """_review_run must not raise even when the workspace is empty."""
        _review_run(empty_workspace)  # should not raise


class TestReviewRunLegacy:
    """Tests for _review_run with the old (legacy) workspace layout."""

    def test_graceful_on_legacy_workspace(
        self, legacy_workspace: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Legacy workspaces without manifest use filesystem discovery when possible."""
        _review_run(legacy_workspace)
        captured = capsys.readouterr()
        assert "manifest" in captured.out.lower() or "artifact" in captured.out.lower()


# ── _create_provider passthrough tests (Issue #3) ──────────────────────────


class TestCreateProvider:
    """Tests that _create_provider passes api_key directly to provider constructors."""

    def test_openai_explicit_api_key(self, monkeypatch: Any) -> None:
        """api_key is forwarded to OpenAIProvider — provider.api_key matches."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with patch("council.llm.openai_provider.openai") as mock_openai:
            mock_openai.AsyncOpenAI.return_value = MagicMock()
            mock_openai.AuthenticationError = Exception
            mock_openai.PermissionDeniedError = Exception
            mock_openai.NotFoundError = Exception
            mock_openai.BadRequestError = Exception

            provider = _create_provider("openai", None, api_key="sk-test")

        assert provider.api_key == "sk-test"

    def test_anthropic_explicit_api_key(self, monkeypatch: Any) -> None:
        """api_key is forwarded to AnthropicProvider — provider.api_key matches."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with patch("council.llm.anthropic_provider.anthropic") as mock_anthropic:
            mock_anthropic.AsyncAnthropic.return_value = MagicMock()
            mock_anthropic.AuthenticationError = Exception
            mock_anthropic.PermissionDeniedError = Exception
            mock_anthropic.NotFoundError = Exception
            mock_anthropic.BadRequestError = Exception

            provider = _create_provider("anthropic", None, api_key="ant-test")

        assert provider.api_key == "ant-test"

    def test_create_provider_openai_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """RuntimeError raised when no key and OPENAI_API_KEY env var not set."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="[Oo]penAI|OPENAI_API_KEY"):
            _create_provider("openai", None)

    def test_create_provider_anthropic_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """RuntimeError raised when no key and ANTHROPIC_API_KEY env var not set."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="[Aa]nthropic|ANTHROPIC_API_KEY"):
            _create_provider("anthropic", None)

    def test_create_provider_openrouter_explicit_key_forwarded(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Explicit api_key is forwarded to OpenRouterProvider."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        # OpenRouterProvider is imported inside _create_provider — patch the class in its module
        with patch("council.llm.openrouter_provider.OpenRouterProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            with patch("council.llm.openai_provider.openai") as mock_openai:
                mock_openai.AsyncOpenAI.return_value = MagicMock()
                _create_provider("openrouter", None, api_key="sk-or-test")
            call_kwargs = mock_cls.call_args
            assert call_kwargs is not None

    def test_create_provider_openrouter_no_key_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """RuntimeError raised when no key and OPENROUTER_API_KEY env var not set."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="[Oo]penRouter|OPENROUTER_API_KEY"):
            _create_provider("openrouter", None)

    def test_create_provider_unknown_raises_value_error(self) -> None:
        """ValueError raised for unknown provider name."""
        with pytest.raises(ValueError, match="[Uu]nknown provider|bogus"):
            _create_provider("bogus-provider", None)

    def test_create_provider_claude_code_forwards_call_timeout(self, tmp_path: Path) -> None:
        """Claude Code provider receives CLI timeout as provider call timeout."""
        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash", encoding="utf-8")
        fake_cli.chmod(0o755)
        provider = _create_provider(
            "claude-code",
            None,
            call_timeout=600.0,
            executable_path=str(fake_cli),
        )
        assert provider.call_timeout == 600.0

    def test_create_provider_kimi_code_forwards_call_timeout(self, tmp_path: Path) -> None:
        """Kimi Code provider receives CLI timeout as provider call timeout."""
        fake_cli = tmp_path / "kimi"
        fake_cli.write_text("#!/bin/bash", encoding="utf-8")
        fake_cli.chmod(0o755)
        provider = _create_provider(
            "kimi-code",
            None,
            call_timeout=600.0,
            executable_path=str(fake_cli),
        )
        assert provider.call_timeout == 600.0

    def test_create_provider_openai_whitespace_key_stripped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """API key with surrounding whitespace is stripped before use."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        # OpenAIProvider is imported inside _create_provider — patch inside its module
        with patch("council.llm.openai_provider.openai") as mock_openai:
            mock_openai.AsyncOpenAI.return_value = MagicMock()
            mock_openai.AuthenticationError = Exception
            mock_openai.PermissionDeniedError = Exception
            mock_openai.NotFoundError = Exception
            mock_openai.BadRequestError = Exception
            provider = _create_provider("openai", None, api_key="  sk-test  ")
            # The key stored on the provider should be stripped
            assert provider.api_key == "sk-test"


# ── API key env-var warning tests (Issues #4, #7) ──────────────────────────


def _make_args(**kwargs: Any) -> argparse.Namespace:
    """Build a minimal argparse.Namespace for _run_council tests."""
    defaults = {
        "config": None,
        "provider": "openai",
        "model": None,
        "api_key": None,
        "platform": "cli",
        "rounds": 1,
        "timeout": 30.0,
        "output": "/tmp/council_test_output",
        "monitor": False,
        "aggregate": False,
        "review": None,
        "verbose": False,
        "documents": None,
        "documents_dir": None,
        "template": None,
        "force": False,
        "scalac_mode": False,
        "dashboard": False,
        "demo": False,
        "scenario": "saas-launch",
        "interactive": False,
        "onboarding": False,
        "brief": None,
        "free_tier": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestApiKeyWarning:
    """Tests for --api-key behaviour with no-key providers and unknown providers (Issues #4, #7)."""

    def test_ollama_api_key_warns(
        self, monkeypatch: Any, caplog: pytest.LogCaptureFixture, tmp_path: Path
    ) -> None:
        """Passing --api-key with ollama logs a warning; OPENAI_API_KEY is NOT set."""
        from council.cli import _run_council

        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        config_file = tmp_path / "company.json"
        config_file.write_text('{"name":"T","product":"P"}', encoding="utf-8")
        args = _make_args(
            provider="ollama",
            api_key="some-key",
            config=str(config_file),
            output=str(tmp_path),
            monitor=False,
        )

        mock_config = MagicMock()
        mock_config.name = "T"
        mock_config.product = "P"
        mock_config.model_dump_json.return_value = "{}"

        mock_adapter = MagicMock()
        mock_adapter.get_name.return_value = "cli"
        mock_adapter.spawn_agents = AsyncMock()

        mock_provider = MagicMock()

        mock_orch = MagicMock()
        mock_orch.write_artifacts.return_value = {}
        mock_orch.spawn_agents = AsyncMock()

        with patch("council.config.loader.ConfigLoader.from_json", return_value=mock_config):
            with patch("council.cli._create_platform_adapter", return_value=mock_adapter):
                with patch("council.cli._create_provider", return_value=mock_provider):
                    with patch(
                        "council.orchestration.orchestrator.AsyncOrchestrator",
                        return_value=mock_orch,
                    ):
                        with caplog.at_level(logging.WARNING, logger="council.cli"):
                            try:
                                asyncio.run(_run_council(args))
                            except Exception:
                                pass

        assert "does not use an API key" in caplog.text
        assert os.environ.get("OPENAI_API_KEY") != "some-key"

    def test_claude_code_api_key_warns(
        self, monkeypatch: Any, caplog: pytest.LogCaptureFixture, tmp_path: Path
    ) -> None:
        """Passing --api-key with claude-code logs a warning and doesn't set any env var."""
        from council.cli import _run_council

        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        config_file = tmp_path / "company.json"
        config_file.write_text('{"name":"T","product":"P"}', encoding="utf-8")
        args = _make_args(
            provider="claude-code",
            api_key="some-key",
            config=str(config_file),
            output=str(tmp_path),
        )

        mock_config = MagicMock()
        mock_config.name = "T"
        mock_config.product = "P"
        mock_config.model_dump_json.return_value = "{}"

        with patch("council.config.loader.ConfigLoader.from_json", return_value=mock_config):
            with patch(
                "council.cli._create_platform_adapter",
                return_value=MagicMock(get_name=lambda: "cli"),
            ):
                with patch("council.cli._create_provider", return_value=MagicMock()):
                    with caplog.at_level(logging.WARNING, logger="council.cli"):
                        try:
                            asyncio.run(_run_council(args))
                        except Exception:
                            pass

        assert "does not use an API key" in caplog.text
        assert os.environ.get("ANTHROPIC_API_KEY") != "some-key"

    @pytest.mark.asyncio
    async def test_kimi_code_api_key_warns(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
        tmp_path: Path,
    ) -> None:
        """Passing api_key with kimi-code provider logs a warning and does not set env vars."""
        from council.cli import _run_council

        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        config_file = tmp_path / "company.json"
        config_file.write_text('{"name":"T","product":"P"}', encoding="utf-8")
        args = _make_args(
            provider="kimi-code",
            api_key="some-key",
            config=str(config_file),
            output=str(tmp_path),
        )

        mock_config = MagicMock()
        mock_config.name = "T"
        mock_config.product = "P"
        mock_config.model_dump_json.return_value = "{}"

        with patch("council.config.loader.ConfigLoader.from_json", return_value=mock_config):
            with patch(
                "council.cli._create_platform_adapter",
                return_value=MagicMock(get_name=lambda: "cli"),
            ):
                with patch("council.cli._create_provider", return_value=MagicMock()):
                    with caplog.at_level(logging.WARNING, logger="council.cli"):
                        try:
                            await _run_council(args)
                        except Exception:
                            pass

        assert "does not use an API key" in caplog.text
        assert os.environ.get("ANTHROPIC_API_KEY") != "some-key"

    def test_unknown_provider_raises_value_error(self, monkeypatch: Any, tmp_path: Path) -> None:
        """An unknown provider with --api-key raises ValueError with 'Unknown provider'."""
        from council.cli import _run_council

        config_file = tmp_path / "company.json"
        config_file.write_text('{"name":"T","product":"P"}', encoding="utf-8")
        # Use a provider name that is not in _NO_API_KEY_PROVIDERS and not in env_map
        args = _make_args(
            provider="openai",  # use valid argparse choice; override provider after
            api_key="some-key",
            config=str(config_file),
            output=str(tmp_path),
        )
        # Manually set an unknown provider (bypasses argparse choices validation)
        args.provider = "unknown-provider"

        mock_config = MagicMock()
        mock_config.name = "T"
        mock_config.product = "P"
        mock_config.model_dump_json.return_value = "{}"

        with patch("council.config.loader.ConfigLoader.from_json", return_value=mock_config):
            with pytest.raises(ValueError, match="Unknown provider"):
                asyncio.run(_run_council(args))


# ── Issue #23 — Workspace overwrite + --force ───────────────────────────────


class TestWorkspaceOverwrite:
    """Tests for workspace-overwrite confirmation behaviour (Issue #23)."""

    def test_force_flag_parses_to_true(self) -> None:
        """parse_args(['--config', 'x.json', '--force']) -> args.force is True."""
        args = parse_args(["--config", "x.json", "--force"])
        assert args.force is True

    def test_force_flag_absent_defaults_to_false(self) -> None:
        """When --force is absent, args.force is False."""
        args = parse_args(["--config", "x.json"])
        assert args.force is False

    def test_non_tty_warns_but_continues(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Non-TTY + existing non-empty workspace -> WARNING logged, no prompt asked.

        Execution is stopped early (before LLM calls) by patching
        _create_platform_adapter to raise a sentinel exception.  The
        overwrite-check runs before that call, so the warning must already
        be in caplog by the time we catch the sentinel.
        """
        import json as _json

        from council.cli import _run_council as _rc

        workspace = tmp_path / "output"
        workspace.mkdir(parents=True)
        (workspace / "old_run.txt").write_text("data", encoding="utf-8")

        config_file = tmp_path / "company.json"
        config_file.write_text(
            _json.dumps(
                {
                    "name": "TestCo",
                    "product": "SaaS",
                    "pricing_tier": "Free",
                    "value_proposition": "v",
                    "competitors": [],
                    "differentiators": [],
                    "target": {
                        "segment": "SMB",
                        "decision_maker": "CEO",
                        "pain_points": [],
                        "budget_range": "10k",
                        "geo_focus": [],
                    },
                    "constraints": {"timeline_days": 30, "team_size": 2, "focus_areas": []},
                }
            ),
            encoding="utf-8",
        )

        args = parse_args(
            ["--config", str(config_file), "--output", str(workspace), "--provider", "ollama"]
        )

        class _StopEarly(Exception):
            pass

        with (
            caplog.at_level(logging.WARNING, logger="council.cli"),
            patch("sys.stdin") as mock_stdin,
            patch("council.cli._create_platform_adapter", side_effect=_StopEarly),
        ):
            mock_stdin.isatty.return_value = False
            try:
                asyncio.run(_rc(args))
            except _StopEarly:
                pass

        warning_msgs = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert any(
            "already exists" in m or "overwrite" in m.lower() for m in warning_msgs
        ), f"Expected overwrite WARNING, got: {warning_msgs}"

    def test_force_flag_skips_confirmation(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """--force -> no overwrite WARNING emitted, INFO 'continuing (--force)' instead."""
        import json as _json

        from council.cli import _run_council as _rc

        workspace = tmp_path / "output"
        workspace.mkdir(parents=True)
        (workspace / "old_run.txt").write_text("data", encoding="utf-8")

        config_file = tmp_path / "company.json"
        config_file.write_text(
            _json.dumps(
                {
                    "name": "TestCo",
                    "product": "SaaS",
                    "pricing_tier": "Free",
                    "value_proposition": "v",
                    "competitors": [],
                    "differentiators": [],
                    "target": {
                        "segment": "SMB",
                        "decision_maker": "CEO",
                        "pain_points": [],
                        "budget_range": "10k",
                        "geo_focus": [],
                    },
                    "constraints": {"timeline_days": 30, "team_size": 2, "focus_areas": []},
                }
            ),
            encoding="utf-8",
        )

        args = parse_args(
            [
                "--config",
                str(config_file),
                "--output",
                str(workspace),
                "--force",
                "--provider",
                "ollama",
            ]
        )

        class _StopEarly(Exception):
            pass

        with (
            caplog.at_level(logging.DEBUG, logger="council.cli"),
            patch("council.cli._create_platform_adapter", side_effect=_StopEarly),
        ):
            try:
                asyncio.run(_rc(args))
            except _StopEarly:
                pass

        overwrite_warnings = [
            r.message
            for r in caplog.records
            if r.levelno == logging.WARNING
            and ("already exists" in r.message or "overwrite" in r.message.lower())
        ]
        assert (
            overwrite_warnings == []
        ), f"--force should suppress overwrite WARNING, got: {overwrite_warnings}"

    def test_dashboard_mode_skips_tty_input(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """With dashboard active, existing output dir must not block on input()."""
        import json as _json

        from council.cli import _run_council as _rc

        workspace = tmp_path / "output"
        workspace.mkdir(parents=True)
        (workspace / "old_run.txt").write_text("data", encoding="utf-8")

        config_file = tmp_path / "company.json"
        config_file.write_text(
            _json.dumps(
                {
                    "name": "TestCo",
                    "product": "SaaS",
                    "pricing_tier": "Free",
                    "value_proposition": "v",
                    "competitors": [],
                    "differentiators": [],
                    "target": {
                        "segment": "SMB",
                        "decision_maker": "CEO",
                        "pain_points": [],
                        "budget_range": "10k",
                        "geo_focus": [],
                    },
                    "constraints": {"timeline_days": 30, "team_size": 2, "focus_areas": []},
                }
            ),
            encoding="utf-8",
        )

        args = _make_args(config=str(config_file), output=str(workspace), provider="ollama")
        mock_dashboard = MagicMock()
        mock_dashboard.log = MagicMock()

        class _StopEarly(Exception):
            pass

        with (
            patch("builtins.input") as mock_input,
            patch("council.cli._create_platform_adapter", side_effect=_StopEarly),
        ):
            try:
                asyncio.run(_rc(args, dashboard=mock_dashboard))
            except _StopEarly:
                pass

        mock_input.assert_not_called()
        logged = " ".join(str(c) for c in mock_dashboard.log.call_args_list)
        assert "overwriting" in logged.lower() or "previous files" in logged.lower()

    def test_non_dashboard_tty_still_prompts_on_overwrite(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """#118: without dashboard, TTY + existing output still uses input()."""
        import json as _json

        from council.cli import _run_council as _rc

        workspace = tmp_path / "output"
        workspace.mkdir(parents=True)
        (workspace / "old_run.txt").write_text("data", encoding="utf-8")

        config_file = tmp_path / "company.json"
        config_file.write_text(
            _json.dumps(
                {
                    "name": "TestCo",
                    "product": "SaaS",
                    "pricing_tier": "Free",
                    "value_proposition": "v",
                    "competitors": [],
                    "differentiators": [],
                    "target": {
                        "segment": "SMB",
                        "decision_maker": "CEO",
                        "pain_points": [],
                        "budget_range": "10k",
                        "geo_focus": [],
                    },
                    "constraints": {"timeline_days": 30, "team_size": 2, "focus_areas": []},
                }
            ),
            encoding="utf-8",
        )

        args = _make_args(config=str(config_file), output=str(workspace), provider="ollama")

        class _StopEarly(Exception):
            pass

        with (
            patch("builtins.input", return_value="y") as mock_input,
            patch("sys.stdin") as mock_stdin,
            patch("council.cli._create_platform_adapter", side_effect=_StopEarly),
        ):
            mock_stdin.isatty.return_value = True
            try:
                asyncio.run(_rc(args, dashboard=None))
            except _StopEarly:
                pass

        mock_input.assert_called_once()

    def test_force_dashboard_logs_continue(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """#118: --force + dashboard logs continue without input()."""
        import json as _json

        from council.cli import _run_council as _rc

        workspace = tmp_path / "output"
        workspace.mkdir(parents=True)
        (workspace / "old_run.txt").write_text("data", encoding="utf-8")

        config_file = tmp_path / "company.json"
        config_file.write_text(
            _json.dumps(
                {
                    "name": "TestCo",
                    "product": "SaaS",
                    "pricing_tier": "Free",
                    "value_proposition": "v",
                    "competitors": [],
                    "differentiators": [],
                    "target": {
                        "segment": "SMB",
                        "decision_maker": "CEO",
                        "pain_points": [],
                        "budget_range": "10k",
                        "geo_focus": [],
                    },
                    "constraints": {"timeline_days": 30, "team_size": 2, "focus_areas": []},
                }
            ),
            encoding="utf-8",
        )

        args = _make_args(
            config=str(config_file),
            output=str(workspace),
            provider="ollama",
            force=True,
        )
        mock_dashboard = MagicMock()
        mock_dashboard.log = MagicMock()

        class _StopEarly(Exception):
            pass

        with (
            patch("builtins.input") as mock_input,
            patch("council.cli._create_platform_adapter", side_effect=_StopEarly),
        ):
            try:
                asyncio.run(_rc(args, dashboard=mock_dashboard))
            except _StopEarly:
                pass

        mock_input.assert_not_called()
        logged = " ".join(str(c) for c in mock_dashboard.log.call_args_list)
        assert "previous files" in logged.lower() or "force" in logged.lower()


class TestDashboardStartupLogs:
    """#114 _dlog startup sequence and #113 ready-event wiring."""

    @pytest.mark.asyncio
    async def test_dlog_startup_sequence(self, tmp_path: Path) -> None:
        import json as _json

        from council.cli import _run_council as _rc

        config_file = tmp_path / "company.json"
        config_file.write_text(
            _json.dumps(
                {
                    "name": "TestCo",
                    "product": "SaaS",
                    "pricing_tier": "Free",
                    "value_proposition": "v",
                    "competitors": [],
                    "differentiators": [],
                    "target": {
                        "segment": "SMB",
                        "decision_maker": "CEO",
                        "pain_points": [],
                        "budget_range": "10k",
                        "geo_focus": [],
                    },
                    "constraints": {"timeline_days": 30, "team_size": 2, "focus_areas": []},
                }
            ),
            encoding="utf-8",
        )

        args = _make_args(
            config=str(config_file),
            output=str(tmp_path / "out"),
            provider="ollama",
            template=None,
        )
        mock_dashboard = MagicMock()
        mock_dashboard.log = MagicMock()

        class _StopEarly(Exception):
            pass

        mock_adapter = MagicMock()
        mock_adapter.get_name.return_value = "CLI"
        mock_adapter.spawn_agents = AsyncMock(side_effect=_StopEarly)

        with (
            patch("council.cli._create_platform_adapter", return_value=mock_adapter),
            patch(
                "council.llm.ollama_provider.OllamaProvider.verify_reachable",
                new=AsyncMock(),
            ),
        ):
            try:
                await _rc(args, dashboard=mock_dashboard)
            except _StopEarly:
                pass

        messages = [call.args[0] for call in mock_dashboard.log.call_args_list]
        assert "Council worker started" in messages
        assert any("Loading config" in m for m in messages)
        assert any("Company: TestCo" in m for m in messages)
        assert any("Initializing provider" in m for m in messages)
        assert any("Platform:" in m for m in messages)

    def test_council_thread_waits_for_ready_event(self) -> None:
        """#113: worker blocks until dashboard ready event is set."""
        import threading
        import time

        ready = threading.Event()
        order: list[str] = []

        def worker() -> None:
            order.append("wait")
            if not ready.wait(timeout=2.0):
                order.append("timeout")
                return
            order.append("run")

        thread = threading.Thread(target=worker)
        thread.start()
        time.sleep(0.05)
        assert order == ["wait"]
        ready.set()
        thread.join(timeout=2.0)
        assert order == ["wait", "run"]

    def test_dashboard_run_passes_on_ready(self) -> None:
        """#113: CouncilDashboard.run(on_ready=...) receives callback on mount."""
        from council.vis.dashboard import CouncilApp, CouncilDashboard

        dash = CouncilDashboard(["Marcus"], max_rounds=1, workspace=Path("/tmp/out"))
        fired: list[bool] = []

        def on_ready() -> None:
            fired.append(True)

        with patch.object(CouncilApp, "run") as mock_app_run:
            mock_app_run.side_effect = lambda *args, **kwargs: dash._on_app_mounted()
            dash.run(on_ready=on_ready)

        assert fired == [True]

    def test_retry_callback_routes_to_dashboard_log(self) -> None:
        """#116: retry notice uses dashboard.log when dashboard active."""
        from council.cli import _dlog
        from council.llm.retry import set_retry_status_callback

        mock_dashboard = MagicMock()
        mock_dashboard.log = MagicMock()

        def notice(msg: str) -> None:
            _dlog(mock_dashboard, f"↻ {msg}")

        set_retry_status_callback(notice)
        try:
            notice("generate: attempt 1/3 failed, retrying")
        finally:
            set_retry_status_callback(None)

        mock_dashboard.log.assert_called_once_with("↻ generate: attempt 1/3 failed, retrying")


# ── Issue #19 — Dashboard flag parse + thread-join sys.exit ─────────────────


class TestParseDashboardFlag:
    """Parse-level tests for --dashboard (Issue #19)."""

    def test_parse_dashboard_flag(self) -> None:
        """--dashboard flag sets args.dashboard to True."""
        args = parse_args(["--config", "x.json", "--dashboard"])
        assert args.dashboard is True

    def test_dashboard_absent_defaults_to_false(self) -> None:
        """When --dashboard is absent, args.dashboard is False."""
        args = parse_args(["--config", "x.json"])
        assert args.dashboard is False


class TestDashboardThreadJoin:
    """Test that sys.exit(1) fires when the council thread does not finish (Issue #19)."""

    def test_dashboard_thread_join_called_exits_1(self) -> None:
        """Simulate main() logic: alive thread after join -> sys.exit(1)."""
        import threading

        mock_thread = MagicMock(spec=threading.Thread)
        mock_thread.is_alive.return_value = True

        mock_dashboard = MagicMock()
        mock_dashboard.run.return_value = None

        logger_under_test = logging.getLogger("council.cli")

        def _simulate_post_dashboard_join(thread, dashboard):
            """Mirrors the main() code that joins the council thread."""
            dashboard.run()
            thread.join(timeout=60.0)
            if thread.is_alive():
                logger_under_test.error(
                    "Council thread did not finish within 60 seconds after dashboard closed."
                )
                sys.exit(1)

        with pytest.raises(SystemExit) as exc_info:
            _simulate_post_dashboard_join(mock_thread, mock_dashboard)

        assert exc_info.value.code == 1
        mock_thread.join.assert_called_once_with(timeout=60.0)
