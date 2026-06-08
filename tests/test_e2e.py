"""End-to-end CLI smoke tests — full process, no mocks.

These complement unit tests by exercising ``python -m council`` as a black box.
They run without API keys (demo / ollama / review / template list paths).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PYTHON = sys.executable
MODULE = "council"


def _run_council(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, "-m", MODULE, *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )


@pytest.mark.integration
class TestE2EDemoPipeline:
    """Demo CLI → artifacts → review (issues #101, #103)."""

    def test_demo_cli_writes_manifest_and_proposal(self, tmp_path: Path) -> None:
        output = tmp_path / "out"
        result = _run_council(
            "--demo",
            "--scenario",
            "saas-launch",
            "--rounds",
            "1",
            "--output",
            str(output),
        )
        assert result.returncode == 0, result.stderr or result.stdout

        manifest = output / "output" / "manifest.json"
        proposal = output / "output" / "proposal.md"
        config = output / "config.json"

        assert manifest.exists(), "manifest.json missing after demo"
        assert proposal.exists(), "proposal.md missing after demo"
        assert config.exists(), "config.json missing after demo"

        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert data.get("provider") == "demo"
        assert data.get("rounds_completed", 0) >= 1
        assert "TaskFlow" in proposal.read_text(encoding="utf-8")

    def test_review_after_demo(self, tmp_path: Path) -> None:
        output = tmp_path / "out"
        run = _run_council(
            "--demo",
            "--scenario",
            "saas-launch",
            "--rounds",
            "1",
            "--output",
            str(output),
        )
        assert run.returncode == 0

        review = _run_council("--review", str(output))
        assert review.returncode == 0, review.stderr
        assert "TaskFlow" in review.stdout or "Previous Run" in review.stdout

    def test_review_filesystem_fallback_without_manifest(self, tmp_path: Path) -> None:
        ws = tmp_path / "legacy"
        discussion = ws / "shared" / "discussion"
        discussion.mkdir(parents=True)
        (discussion / "marcus_round_1.md").write_text("# Marcus\n\nOffer draft.", encoding="utf-8")

        review = _run_council("--review", str(ws))
        assert review.returncode == 0
        assert "manifest" in review.stdout.lower() or "discovered" in review.stdout.lower()


@pytest.mark.integration
class TestE2ECliEntrypoints:
    """CLI flags and fail-fast behavior."""

    def test_help_exits_zero(self) -> None:
        result = _run_council("--help")
        assert result.returncode == 0
        assert "Universal AI Marketing Council" in result.stdout

    def test_template_list_exits_zero(self) -> None:
        result = _run_council("--template")
        assert result.returncode == 0
        assert "saas" in result.stdout.lower() or "template" in result.stdout.lower()

    def test_missing_api_key_fails_before_run(self, tmp_path: Path) -> None:
        config = tmp_path / "company.json"
        config.write_text(
            json.dumps(
                {
                    "name": "E2E Co",
                    "product": "Test",
                    "pricing_tier": "",
                    "value_proposition": "",
                    "competitors": [],
                    "differentiators": [],
                }
            ),
            encoding="utf-8",
        )
        result = _run_council(
            "--config",
            str(config),
            "--output",
            str(tmp_path / "out"),
            "--provider",
            "openai",
        )
        assert result.returncode != 0
        assert "OPENAI_API_KEY" in result.stdout or "API key" in result.stdout

    def test_ollama_provider_passes_key_validation(self, tmp_path: Path) -> None:
        config = tmp_path / "company.json"
        config.write_text(
            json.dumps(
                {
                    "name": "E2E Co",
                    "product": "Test",
                    "pricing_tier": "",
                    "value_proposition": "",
                    "competitors": [],
                    "differentiators": [],
                }
            ),
            encoding="utf-8",
        )
        result = _run_council(
            "--config",
            str(config),
            "--output",
            str(tmp_path / "out"),
            "--provider",
            "ollama",
            "--rounds",
            "1",
        )
        combined = (result.stdout + result.stderr).lower()
        assert "openai_api_key" not in combined
        assert "api key missing" not in combined or "ollama" in combined


@pytest.mark.integration
class TestE2EOpenRouterFreeTierLogic:
    """Free-model chain helpers (no network)."""

    def test_free_model_sorting_and_detection(self) -> None:
        from council.llm.openrouter_provider import OpenRouterProvider

        assert OpenRouterProvider._is_free_model_entry(
            {"id": "vendor/model:free", "pricing": {"prompt": "1", "completion": "1"}}
        )
        sorted_ids = OpenRouterProvider._sort_free_models(
            ["z/model:free", "deepseek/deepseek-chat:free", "a/model:free"]
        )
        assert sorted_ids[0] == "deepseek/deepseek-chat:free"
