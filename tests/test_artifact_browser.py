from __future__ import annotations

import json
from pathlib import Path

from council.vis.artifact_browser import (
    ARTIFACT_LABELS,
    ArtifactBrowserApp,
    build_artifact_browser_model,
    read_artifact_preview,
)


def test_browser_model_groups_artifacts_and_selects_proposal(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    agents_dir = output_dir / "agents"
    discussion_dir = tmp_path / "shared" / "discussion"
    agents_dir.mkdir(parents=True)
    discussion_dir.mkdir(parents=True)
    proposal = output_dir / "proposal.md"
    proposal.write_text("# Proposal\n\nFull proposal.", encoding="utf-8")
    agent = agents_dir / "marcus_offer.md"
    agent.write_text("# Marcus", encoding="utf-8")
    discussion = discussion_dir / "marcus_round_1.md"
    discussion.write_text("# Round", encoding="utf-8")
    (output_dir / "trace.json").write_text("{}", encoding="utf-8")
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "rounds_completed": 1,
                "max_rounds": 1,
                "files": {
                    "proposal": str(proposal),
                    "final_deliverables": {"Marcus": str(agent)},
                    "agent_outputs": {"Marcus": str(discussion)},
                },
            }
        ),
        encoding="utf-8",
    )

    model = build_artifact_browser_model(tmp_path)

    assert model.status == "complete"
    assert model.default_artifact is not None
    assert model.default_artifact.relative_path == Path("output/proposal.md")
    assert [group.name for group in model.groups][:4] == [
        "Proposal",
        "Agent Outputs",
        "Discussion",
        "Manifest",
    ]
    rendered_labels = [item.label for group in model.groups for item in group.items]
    assert "[PROPOSAL] output/proposal.md" in rendered_labels
    assert "[AGENT] output/agents/marcus_offer.md" in rendered_labels
    assert "[ROUND 1] shared/discussion/marcus_round_1.md" in rendered_labels
    assert "[TRACE] output/trace.json" in rendered_labels
    assert all("📋" not in label and "🎯" not in label and "💬" not in label for label in rendered_labels)


def test_read_artifact_preview_does_not_truncate_normal_markdown(tmp_path: Path) -> None:
    path = tmp_path / "output" / "proposal.md"
    path.parent.mkdir(parents=True)
    content = "# Proposal\n\n" + ("Long but normal markdown.\n" * 400)
    path.write_text(content, encoding="utf-8")
    artifact = build_artifact_browser_model(tmp_path).default_artifact

    assert artifact is not None
    assert read_artifact_preview(artifact) == content


def test_artifact_labels_are_ascii_structural_labels() -> None:
    assert ARTIFACT_LABELS["proposal"] == "[PROPOSAL]"
    assert ARTIFACT_LABELS["agent"] == "[AGENT]"
    assert ARTIFACT_LABELS["discussion"] == "[ROUND]"
    assert ARTIFACT_LABELS["manifest"] == "[MANIFEST]"
    assert ARTIFACT_LABELS["trace"] == "[TRACE]"
    assert ARTIFACT_LABELS["review"] == "[REVIEW]"


async def test_artifact_browser_mounts_with_default_preview(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)
    proposal = output_dir / "proposal.md"
    proposal.write_text("# Proposal\n\nBrowser preview.", encoding="utf-8")

    app = ArtifactBrowserApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert app.selected_artifact is not None
        assert app.selected_artifact.path == proposal.resolve()
