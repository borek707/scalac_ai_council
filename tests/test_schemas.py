from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from council.artifacts import discover_artifacts
from council.schemas import (
    SCHEMA_VERSION,
    DeliverableSection,
    FinalDeliverable,
    Manifest,
    ManifestFiles,
)


class TestManifestSchema:
    def test_roundtrip_sets_schema_version(self) -> None:
        m = Manifest(
            generated_at="2026-06-11T00:00:00+00:00",
            company="Acme",
            product="Widget",
            provider="openai",
            model="gpt-4o",
            rounds_completed=3,
            max_rounds=3,
            agents=["Marcus", "Elena"],
            files=ManifestFiles(proposal="output/proposal.md"),
        )
        data = m.to_dict()
        assert data["schema_version"] == SCHEMA_VERSION
        assert data["files"]["proposal"] == "output/proposal.md"

    def test_from_dict_tolerates_legacy_manifest(self) -> None:
        legacy = {
            "generated_at": "2026-01-01T00:00:00+00:00",
            "company": "OldCo",
            "product": "Legacy",
            "provider": "openai",
            "model": "gpt-4o",
            "rounds_completed": 2,
            "max_rounds": 3,
            "agents": ["Marcus"],
            "files": {
                "proposal": "output/proposal.md",
                "agent_outputs": {"Marcus": "x.md"},
            },
        }
        m = Manifest.from_dict(legacy)
        assert m.schema_version == "0"
        assert m.status == "complete"
        assert m.files.agent_outputs == {"Marcus": "x.md"}

    def test_negative_rounds_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Manifest(
                generated_at="t",
                company="c",
                product="p",
                provider="openai",
                rounds_completed=-1,
                max_rounds=3,
            )


class TestFinalDeliverable:
    def test_to_markdown_renders_sections_and_recs(self) -> None:
        d = FinalDeliverable(
            agent="Marcus",
            title="Offer Strategy",
            summary="A crisp offer.",
            sections=[DeliverableSection(heading="Pricing", content="Good-Better-Best")],
            recommendations=["Launch tier 1", "Test pricing"],
        )
        md = d.to_markdown()
        assert "# Offer Strategy" in md
        assert "_by Marcus_" in md
        assert "## Pricing" in md
        assert "- Launch tier 1" in md

    def test_empty_summary_rejected(self) -> None:
        with pytest.raises(ValidationError):
            FinalDeliverable(agent="Marcus", title="t", summary="")


class TestManifestDiscoveryCases:
    def test_discovery_with_valid_manifest(self, tmp_path: Path) -> None:
        out = tmp_path / "output"
        out.mkdir()
        (out / "proposal.md").write_text("# Proposal", encoding="utf-8")
        manifest = Manifest(
            generated_at="t",
            company="c",
            product="p",
            provider="openai",
            rounds_completed=1,
            max_rounds=1,
            files=ManifestFiles(proposal=str(out / "proposal.md")),
        )
        (out / "manifest.json").write_text(json.dumps(manifest.to_dict()), encoding="utf-8")
        artifacts = discover_artifacts(tmp_path)
        assert any(a.kind == "proposal" for a in artifacts)
        assert any(a.kind == "manifest" for a in artifacts)

    def test_discovery_missing_manifest_falls_back(self, tmp_path: Path) -> None:
        out = tmp_path / "output"
        out.mkdir()
        (out / "proposal.md").write_text("# Proposal", encoding="utf-8")
        artifacts = discover_artifacts(tmp_path)
        # No manifest on disk -> filesystem scan still finds the proposal.
        assert any(a.kind == "proposal" and a.exists for a in artifacts)

    def test_discovery_legacy_manifest_readable(self, tmp_path: Path) -> None:
        out = tmp_path / "output"
        out.mkdir()
        (out / "proposal.md").write_text("# Proposal", encoding="utf-8")
        legacy = {
            "generated_at": "t",
            "company": "c",
            "product": "p",
            "provider": "openai",
            "model": "gpt-4o",
            "rounds_completed": 1,
            "max_rounds": 1,
            "agents": ["Marcus"],
            "files": {"proposal": str(out / "proposal.md")},
        }
        (out / "manifest.json").write_text(json.dumps(legacy), encoding="utf-8")
        # Legacy manifest must still validate through the schema.
        m = Manifest.from_dict(json.loads((out / "manifest.json").read_text()))
        assert m.files.proposal is not None
        artifacts = discover_artifacts(tmp_path)
        assert any(a.kind == "proposal" for a in artifacts)
