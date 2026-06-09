"""Opt-in live smoke tests for OpenRouter.

These tests make real network calls and may consume OpenRouter credits. They
are skipped unless OPENROUTER_API_KEY is set and are excluded from default
pytest runs by the project pytest configuration.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from council.config.env_loader import load_dotenv_from_cwd
from council.llm.openrouter_provider import OpenRouterProvider

pytestmark = pytest.mark.live

PYTHON = sys.executable
LIVE_MODEL = "openai/gpt-4o-mini"


def _openrouter_key() -> str:
    load_dotenv_from_cwd()
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        pytest.skip("OPENROUTER_API_KEY is not set")
    return key


@pytest.mark.asyncio
async def test_openrouter_provider_minimal_completion() -> None:
    """Provider-level smoke test using the real OpenRouter API."""
    provider = OpenRouterProvider(api_key=_openrouter_key(), model=LIVE_MODEL)

    response = await provider.generate(
        "Reply with exactly: ok",
        temperature=0,
        max_tokens=8,
    )

    assert response.content.strip()
    assert "ok" in response.content.lower()
    assert response.model


def test_openrouter_cli_smoke_writes_markdown_artifacts(tmp_path: Path) -> None:
    """Black-box CLI smoke test for a one-round OpenRouter council run."""
    key = _openrouter_key()
    config = tmp_path / "company.json"
    output = tmp_path / "out"
    config.write_text(
        json.dumps(
            {
                "name": "Live Smoke Co",
                "product": "Tiny validation run",
                "pricing_tier": "Free trial",
                "value_proposition": "Fast validation of council live smoke tests.",
                "competitors": [
                    {
                        "name": "Manual QA",
                        "threat": "LOW",
                        "pricing": "Internal time",
                        "weakness": "Slow feedback loops",
                        "clients": [],
                    }
                ],
                "differentiators": ["Automated live smoke coverage"],
            }
        ),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = key
    result = subprocess.run(
        [
            PYTHON,
            "-m",
            "council",
            "--config",
            str(config),
            "--provider",
            "openrouter",
            "--model",
            LIVE_MODEL,
            "--rounds",
            "1",
            "--timeout",
            "120",
            "--output",
            str(output),
            "--force",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
        timeout=180,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    discussion = output / "shared" / "discussion"
    markdown_files = sorted(discussion.glob("*_round_1.md"))
    assert markdown_files, "expected round markdown artifacts"
    assert all(path.read_text(encoding="utf-8").strip() for path in markdown_files)
