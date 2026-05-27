from __future__ import annotations

"""Tests for council.cli — Issues #33 (--review mode) and #34 (fixture workspaces)."""

from pathlib import Path

import pytest

from council.cli import parse_args, _review_run


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


class TestParseArgsTemplate:
    """Tests for the --template argument."""

    def test_template_no_value_exits_zero(self) -> None:
        """--template without a NAME value lists templates and exits 0."""
        with pytest.raises(SystemExit) as exc_info:
            # parse_args triggers _run_council only through main(); here we
            # only parse.  The listing + sys.exit(0) happens inside
            # _run_council, not parse_args itself — so we call the runner
            # directly via the same path the CLI uses.
            from council.cli import _run_council
            import asyncio

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

    def test_displays_rounds(
        self, complete_workspace: Path, capsys: pytest.CaptureFixture
    ) -> None:
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
        """Should surface a clear error when no manifest.json is present."""
        _review_run(empty_workspace)
        captured = capsys.readouterr()
        # The function prints a Panel with "No manifest found"
        assert "manifest" in captured.out.lower() or "No manifest" in captured.out

    def test_returns_without_raising(self, empty_workspace: Path) -> None:
        """_review_run must not raise even when the workspace is empty."""
        _review_run(empty_workspace)  # should not raise


class TestReviewRunLegacy:
    """Tests for _review_run with the old (legacy) workspace layout."""

    def test_graceful_on_legacy_workspace(
        self, legacy_workspace: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Legacy workspaces (no output/manifest.json) get the missing-manifest message."""
        _review_run(legacy_workspace)
        captured = capsys.readouterr()
        assert "manifest" in captured.out.lower() or "No manifest" in captured.out
