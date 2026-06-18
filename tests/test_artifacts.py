"""Tests for the artifact discovery module (issue #37).

Covers:
  - discover_artifacts() — manifest-first path and filesystem fallback
  - get_default_artifact() — priority logic
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from council.artifacts import (
    Artifact,
    ArtifactKind,
    discover_artifacts,
    discover_run_status,
    get_default_artifact,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_manifest(output_dir: Path, files: dict[str, Any]) -> Path:
    """Write a minimal manifest.json to *output_dir* and return its path."""
    manifest = {
        "generated_at": "2026-01-01T00:00:00+00:00",
        "company": "TestCorp",
        "product": "TestProduct",
        "provider": "openai",
        "model": "gpt-4o",
        "rounds_completed": 3,
        "max_rounds": 3,
        "agents": ["Marcus", "Elena"],
        "files": files,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


# ---------------------------------------------------------------------------
# TestDiscoverArtifacts — manifest-based discovery
# ---------------------------------------------------------------------------


class TestDiscoverArtifacts:

    # --- Workspace with manifest -------------------------------------------

    def test_discovers_proposal_from_manifest(self, tmp_path: Path) -> None:
        """Manifest pointing to an existing proposal.md → artifact with kind='proposal'."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)

        proposal_path = output_dir / "proposal.md"
        proposal_path.write_text("# Proposal\n\nContent.", encoding="utf-8")

        _write_manifest(output_dir, {"proposal": str(proposal_path)})

        artifacts = discover_artifacts(tmp_path)

        proposals = [a for a in artifacts if a.kind == "proposal"]
        assert len(proposals) == 1
        assert proposals[0].path == proposal_path.resolve()
        assert proposals[0].exists is True
        assert proposals[0].title == "proposal"

    def test_discovers_agent_outputs_from_manifest(self, tmp_path: Path) -> None:
        """Manifest with agent_outputs entries → those artifacts are included."""
        output_dir = tmp_path / "output"
        agents_dir = output_dir / "agents"
        agents_dir.mkdir(parents=True)

        proposal_path = output_dir / "proposal.md"
        proposal_path.write_text("# Proposal", encoding="utf-8")

        marcus_path = agents_dir / "marcus_offer.md"
        marcus_path.write_text("# Marcus offer", encoding="utf-8")
        elena_path = agents_dir / "elena_strategy.md"
        elena_path.write_text("# Elena strategy", encoding="utf-8")

        _write_manifest(
            output_dir,
            {
                "proposal": str(proposal_path),
                "agent_outputs": {
                    "Marcus": str(marcus_path),
                    "Elena": str(elena_path),
                },
            },
        )

        artifacts = discover_artifacts(tmp_path)
        agent_artifacts = [a for a in artifacts if a.kind == "agent" or a.kind == "discussion"]
        agent_paths = {a.path for a in agent_artifacts}

        assert marcus_path.resolve() in agent_paths
        assert elena_path.resolve() in agent_paths

    def test_manifest_agent_outputs_have_discussion_kind(self, tmp_path: Path) -> None:
        """agent_outputs in manifest are stored with kind='discussion'."""
        output_dir = tmp_path / "output"
        agents_dir = output_dir / "agents"
        agents_dir.mkdir(parents=True)

        proposal_path = output_dir / "proposal.md"
        proposal_path.write_text("# Proposal", encoding="utf-8")

        marcus_path = agents_dir / "marcus_round1.md"
        marcus_path.write_text("# Marcus round 1", encoding="utf-8")

        _write_manifest(
            output_dir,
            {
                "proposal": str(proposal_path),
                "agent_outputs": {"Marcus": str(marcus_path)},
            },
        )

        artifacts = discover_artifacts(tmp_path)
        marcus_artifact = next(a for a in artifacts if a.path == marcus_path.resolve())
        assert marcus_artifact.kind == "discussion"
        assert marcus_artifact.agent == "Marcus"

    def test_manifest_final_deliverables_have_agent_kind(self, tmp_path: Path) -> None:
        """final_deliverables in manifest are stored with kind='agent'."""
        output_dir = tmp_path / "output"
        agents_dir = output_dir / "agents"
        agents_dir.mkdir(parents=True)

        proposal_path = output_dir / "proposal.md"
        proposal_path.write_text("# Proposal", encoding="utf-8")

        deliverable_path = agents_dir / "marcus_final.md"
        deliverable_path.write_text("# Marcus final", encoding="utf-8")

        _write_manifest(
            output_dir,
            {
                "proposal": str(proposal_path),
                "final_deliverables": {"Marcus": str(deliverable_path)},
            },
        )

        artifacts = discover_artifacts(tmp_path)
        d_artifact = next(a for a in artifacts if a.path == deliverable_path.resolve())
        assert d_artifact.kind == "agent"
        assert d_artifact.agent == "Marcus"

    def test_manifest_always_includes_manifest_artifact(self, tmp_path: Path) -> None:
        """Manifest discovery always adds a manifest-kind artifact for manifest.json itself."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)
        manifest_path = _write_manifest(output_dir, {})

        artifacts = discover_artifacts(tmp_path)
        manifest_artifacts = [a for a in artifacts if a.kind == "manifest"]

        assert len(manifest_artifacts) == 1
        assert manifest_artifacts[0].path == manifest_path.resolve()

    def test_artifacts_include_metadata_and_relative_paths(self, tmp_path: Path) -> None:
        """Discovered artifacts expose display metadata for browser UIs."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)
        proposal = output_dir / "proposal.md"
        proposal.write_text("# Proposal\n\nUseful summary.", encoding="utf-8")
        _write_manifest(output_dir, {"proposal": str(proposal)})

        artifact = next(a for a in discover_artifacts(tmp_path) if a.path == proposal.resolve())

        assert artifact.relative_path == Path("output/proposal.md")
        assert artifact.size_bytes == proposal.stat().st_size
        assert artifact.modified_at is not None
        assert artifact.display_group == "Proposal"
        assert artifact.summary_hint == "Useful summary."

    # --- Workspace without manifest (filesystem fallback) ------------------

    def test_filesystem_fallback_finds_proposal(self, tmp_path: Path) -> None:
        """No manifest but output/proposal.md exists → discovered as proposal."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)
        proposal = output_dir / "proposal.md"
        proposal.write_text("# Proposal\n\nContent.", encoding="utf-8")

        artifacts = discover_artifacts(tmp_path)

        proposals = [a for a in artifacts if a.kind == "proposal"]
        assert any(a.path == proposal.resolve() for a in proposals)
        found = next(a for a in proposals if a.path == proposal.resolve())
        assert found.exists is True

    def test_filesystem_fallback_finds_agents_dir(self, tmp_path: Path) -> None:
        """No manifest, output/agents/marcus_offer.md exists → found as agent_output."""
        agents_dir = tmp_path / "output" / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / "marcus_offer.md"
        agent_file.write_text("# Marcus offer", encoding="utf-8")

        artifacts = discover_artifacts(tmp_path)

        agent_artifacts = [a for a in artifacts if a.kind == "agent"]
        agent_paths = {a.path for a in agent_artifacts}
        assert agent_file.resolve() in agent_paths

    def test_filesystem_fallback_infers_agent_name(self, tmp_path: Path) -> None:
        """Agent name is inferred from file stem (e.g. 'marcus_offer' → 'Marcus')."""
        agents_dir = tmp_path / "output" / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / "marcus_offer.md"
        agent_file.write_text("# Marcus", encoding="utf-8")

        artifacts = discover_artifacts(tmp_path)

        agent_artifact = next((a for a in artifacts if a.path == agent_file.resolve()), None)
        assert agent_artifact is not None
        assert agent_artifact.agent == "Marcus"

    def test_filesystem_fallback_legacy_final_proposal(self, tmp_path: Path) -> None:
        """FINAL_PROPOSAL.md in workspace root → discovered as proposal (legacy)."""
        legacy = tmp_path / "FINAL_PROPOSAL.md"
        legacy.write_text("# Final Proposal\n\nLegacy.", encoding="utf-8")

        artifacts = discover_artifacts(tmp_path)

        legacy_artifacts = [a for a in artifacts if a.path == legacy.resolve()]
        assert len(legacy_artifacts) == 1
        assert legacy_artifacts[0].kind == "proposal"
        assert legacy_artifacts[0].exists is True

    def test_filesystem_fallback_finds_discussion_rounds(self, tmp_path: Path) -> None:
        """shared/discussion/*_round_*.md → discovered as discussion kind."""
        disc_dir = tmp_path / "shared" / "discussion"
        disc_dir.mkdir(parents=True)
        round_file = disc_dir / "marcus_round_1.md"
        round_file.write_text("# Marcus round 1", encoding="utf-8")

        artifacts = discover_artifacts(tmp_path)

        discussion_artifacts = [a for a in artifacts if a.kind == "discussion"]
        assert any(a.path == round_file.resolve() for a in discussion_artifacts)

    def test_filesystem_fallback_exposes_trace_review_config_and_brief(self, tmp_path: Path) -> None:
        """Browser-visible support files are discoverable without manifest.json."""
        files = [
            tmp_path / "output" / "trace.json",
            tmp_path / "output" / "artifacts" / "reviews" / "review.md",
            tmp_path / "output" / "artifacts" / "reviews" / "review.json",
            tmp_path / "config.json",
            tmp_path / "shared" / "brief.md",
        ]
        for path in files:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("content", encoding="utf-8")

        by_relative_path = {a.relative_path: a for a in discover_artifacts(tmp_path)}

        assert by_relative_path[Path("output/trace.json")].kind == "trace"
        assert by_relative_path[Path("output/artifacts/reviews/review.md")].kind == "review"
        assert by_relative_path[Path("output/artifacts/reviews/review.json")].kind == "review"
        assert by_relative_path[Path("config.json")].kind == "input"
        assert by_relative_path[Path("shared/brief.md")].kind == "input"

    # --- Empty workspace ---------------------------------------------------

    def test_empty_workspace_returns_empty_list(self, tmp_path: Path) -> None:
        """A workspace with no files → empty list (no exists=True artifacts)."""
        # discover_artifacts still returns non-existent placeholder paths from
        # filesystem scan; we check that no artifact has exists=True
        artifacts = discover_artifacts(tmp_path)
        existing = [a for a in artifacts if a.exists]
        assert existing == []

    def test_run_status_marks_missing_manifest_partial_workspace_as_interrupted(
        self, tmp_path: Path
    ) -> None:
        """A workspace with artifacts but no manifest is interrupted, not empty."""
        discussion = tmp_path / "shared" / "discussion" / "marcus_round_1.md"
        discussion.parent.mkdir(parents=True)
        discussion.write_text("# Round 1", encoding="utf-8")

        assert discover_run_status(tmp_path) == "interrupted"

    def test_run_status_distinguishes_complete_and_in_progress(self, tmp_path: Path) -> None:
        """Manifest round counters expose complete vs in-progress states."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)
        _write_manifest(output_dir, {"proposal": ""})
        manifest_path = output_dir / "manifest.json"

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["rounds_completed"] = 1
        data["max_rounds"] = 3
        manifest_path.write_text(json.dumps(data), encoding="utf-8")
        assert discover_run_status(tmp_path) == "in_progress"

        data["rounds_completed"] = 3
        manifest_path.write_text(json.dumps(data), encoding="utf-8")
        assert discover_run_status(tmp_path) == "complete"

    # --- Deduplication / sort stability -----------------------------------

    def test_results_are_sorted_by_kind_then_title(self, tmp_path: Path) -> None:
        """Returned list is sorted: proposal → agent → discussion → manifest."""
        agents_dir = tmp_path / "output" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "output" / "proposal.md").write_text("p", encoding="utf-8")
        (agents_dir / "elena_offer.md").write_text("e", encoding="utf-8")
        (agents_dir / "marcus_offer.md").write_text("m", encoding="utf-8")

        artifacts = discover_artifacts(tmp_path)
        kinds = [a.kind for a in artifacts if a.exists]

        # proposals must come before agents
        proposal_indices = [i for i, a in enumerate(artifacts) if a.kind == "proposal" and a.exists]
        agent_indices = [i for i, a in enumerate(artifacts) if a.kind == "agent" and a.exists]
        if proposal_indices and agent_indices:
            assert max(proposal_indices) < min(agent_indices)

    def test_no_duplicate_paths(self, tmp_path: Path) -> None:
        """discover_artifacts deduplicates by resolved path."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)
        proposal = output_dir / "proposal.md"
        proposal.write_text("# Proposal", encoding="utf-8")

        artifacts = discover_artifacts(tmp_path)
        paths = [a.path for a in artifacts]
        assert len(paths) == len(set(paths))


# ---------------------------------------------------------------------------
# TestGetDefaultArtifact — priority logic
# ---------------------------------------------------------------------------


class TestGetDefaultArtifact:

    def _make(
        self,
        path: str,
        kind: ArtifactKind,
        title: str,
        exists: bool = True,
        agent: str | None = None,
    ) -> Artifact:
        return Artifact(
            id=path,
            title=title,
            kind=kind,
            agent=agent,
            path=Path(path),
            exists=exists,
        )

    def test_default_prefers_proposal(self) -> None:
        """When list contains proposal and agent_output, returns proposal."""
        artifacts = [
            self._make(
                "/ws/output/agents/marcus_offer.md", "agent", "marcus_offer", agent="Marcus"
            ),
            self._make("/ws/output/proposal.md", "proposal", "proposal"),
        ]
        result = get_default_artifact(artifacts)
        assert result is not None
        assert result.kind == "proposal"
        assert result.path.name == "proposal.md"

    def test_default_falls_back_to_agent_output(self) -> None:
        """No proposal in list, agent artifact present → returns agent artifact."""
        artifacts = [
            self._make(
                "/ws/output/agents/marcus_offer.md", "agent", "marcus_offer", agent="Marcus"
            ),
            self._make(
                "/ws/output/agents/elena_strategy.md", "agent", "elena_strategy", agent="Elena"
            ),
        ]
        result = get_default_artifact(artifacts)
        assert result is not None
        assert result.kind == "agent"

    def test_default_falls_back_to_legacy_final_proposal(self) -> None:
        """No standard proposal.md, but FINAL_PROPOSAL exists → returns it."""
        artifacts = [
            self._make("/ws/FINAL_PROPOSAL.md", "proposal", "FINAL_PROPOSAL"),
            self._make(
                "/ws/output/agents/marcus_offer.md", "agent", "marcus_offer", agent="Marcus"
            ),
        ]
        result = get_default_artifact(artifacts)
        assert result is not None
        assert result.kind == "proposal"
        assert result.title.upper() == "FINAL_PROPOSAL"

    def test_default_prefers_proposal_over_legacy(self) -> None:
        """Standard proposal.md takes priority over FINAL_PROPOSAL."""
        artifacts = [
            self._make("/ws/FINAL_PROPOSAL.md", "proposal", "FINAL_PROPOSAL"),
            self._make("/ws/output/proposal.md", "proposal", "proposal"),
        ]
        result = get_default_artifact(artifacts)
        assert result is not None
        assert result.path.name == "proposal.md"

    def test_default_empty_returns_none(self) -> None:
        """Empty artifact list → None."""
        assert get_default_artifact([]) is None

    def test_default_manifest_only_returns_none(self) -> None:
        """Only manifest artifact in list → no proposal or agent → returns None."""
        artifacts = [
            self._make("/ws/output/manifest.json", "manifest", "manifest"),
        ]
        result = get_default_artifact(artifacts)
        assert result is None

    def test_default_discussion_only_returns_none(self) -> None:
        """Only discussion artifacts → returns None (not proposal, not agent)."""
        artifacts = [
            self._make(
                "/ws/shared/discussion/marcus_round_1.md",
                "discussion",
                "marcus_round_1",
                agent="Marcus",
            ),
        ]
        result = get_default_artifact(artifacts)
        assert result is None

    def test_default_uses_first_agent_alphabetically(self, tmp_path: Path) -> None:
        """When multiple agent artifacts exist, alphabetically first is returned."""
        # discover_artifacts sorts by title, so feeding already-sorted list
        artifacts = [
            self._make("/ws/output/agents/elena_offer.md", "agent", "elena_offer", agent="Elena"),
            self._make(
                "/ws/output/agents/marcus_offer.md", "agent", "marcus_offer", agent="Marcus"
            ),
        ]
        result = get_default_artifact(artifacts)
        assert result is not None
        assert result.agent == "Elena"


# ---------------------------------------------------------------------------
# Integration tests using conftest fixtures
# ---------------------------------------------------------------------------


class TestWithConftestFixtures:
    """Smoke tests re-using fixtures already defined in conftest.py."""

    def test_complete_workspace_has_proposal(self, complete_workspace: Path) -> None:
        """complete_workspace fixture → discover_artifacts finds proposal."""
        artifacts = discover_artifacts(complete_workspace)
        proposals = [a for a in artifacts if a.kind == "proposal" and a.exists]
        assert len(proposals) >= 1

    def test_complete_workspace_default_is_proposal(self, complete_workspace: Path) -> None:
        """get_default_artifact on complete_workspace returns proposal."""
        artifacts = discover_artifacts(complete_workspace)
        default = get_default_artifact(artifacts)
        assert default is not None
        assert default.kind == "proposal"

    def test_empty_workspace_no_existing_artifacts(self, empty_workspace: Path) -> None:
        """empty_workspace fixture → no existing artifacts."""
        artifacts = discover_artifacts(empty_workspace)
        assert all(not a.exists for a in artifacts)

    def test_legacy_workspace_finds_final_proposal(self, legacy_workspace: Path) -> None:
        """legacy_workspace fixture → FINAL_PROPOSAL.md discovered."""
        artifacts = discover_artifacts(legacy_workspace)
        legacy = [a for a in artifacts if a.exists and "FINAL_PROPOSAL" in a.path.name]
        assert len(legacy) == 1
        assert legacy[0].kind == "proposal"

    def test_legacy_workspace_default_is_final_proposal(self, legacy_workspace: Path) -> None:
        """get_default_artifact on legacy_workspace returns FINAL_PROPOSAL."""
        artifacts = discover_artifacts(legacy_workspace)
        existing = [a for a in artifacts if a.exists]
        default = get_default_artifact(existing)
        assert default is not None
        assert "FINAL_PROPOSAL" in default.path.name
