"""Read-only Textual browser for council run artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Markdown, OptionList, Static
from textual.widgets.option_list import Option

from council.artifacts import Artifact, ArtifactKind, discover_artifacts, discover_run_status

ARTIFACT_LABELS: dict[ArtifactKind, str] = {
    "proposal": "[PROPOSAL]",
    "agent": "[AGENT]",
    "discussion": "[ROUND]",
    "manifest": "[MANIFEST]",
    "trace": "[TRACE]",
    "review": "[REVIEW]",
    "input": "[INPUT]",
}

_PREVIEW_LIMIT_BYTES = 1_000_000


@dataclass(frozen=True)
class ArtifactListItem:
    artifact: Artifact
    label: str


@dataclass(frozen=True)
class ArtifactGroup:
    name: str
    items: list[ArtifactListItem]


@dataclass(frozen=True)
class ArtifactBrowserModel:
    workspace: Path
    status: str
    groups: list[ArtifactGroup]
    default_artifact: Artifact | None


def _artifact_label(artifact: Artifact) -> str:
    if artifact.kind == "discussion" and artifact.round_num is not None:
        marker = f"[ROUND {artifact.round_num}]"
    else:
        marker = ARTIFACT_LABELS[artifact.kind]
    return f"{marker} {artifact.relative_path}"


def build_artifact_browser_model(workspace: Path) -> ArtifactBrowserModel:
    """Build a grouped, display-ready model for browser UIs."""
    workspace = workspace.resolve()
    artifacts = [artifact for artifact in discover_artifacts(workspace) if artifact.exists]
    groups_by_name: dict[str, list[ArtifactListItem]] = {}
    for artifact in artifacts:
        groups_by_name.setdefault(artifact.display_group, []).append(
            ArtifactListItem(artifact=artifact, label=_artifact_label(artifact))
        )

    groups = [
        ArtifactGroup(name=name, items=items) for name, items in groups_by_name.items() if items
    ]

    default = _default_browser_artifact(artifacts)
    return ArtifactBrowserModel(
        workspace=workspace,
        status=discover_run_status(workspace),
        groups=groups,
        default_artifact=default,
    )


def _default_browser_artifact(artifacts: list[Artifact]) -> Artifact | None:
    for artifact in artifacts:
        if artifact.kind == "proposal" and artifact.path.name == "proposal.md":
            return artifact
    for artifact in artifacts:
        if artifact.kind == "proposal":
            return artifact
    return artifacts[0] if artifacts else None


def read_artifact_preview(artifact: Artifact) -> str:
    """Read preview content without truncating normal Markdown artifacts."""
    if artifact.size_bytes is not None and artifact.size_bytes > _PREVIEW_LIMIT_BYTES:
        return (
            f"# Preview limited\n\n"
            f"{artifact.relative_path} is {artifact.size_bytes:,} bytes. "
            "Open the file directly for the full content."
        )
    try:
        return artifact.path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"# Binary or non-UTF-8 file\n\nOpen path: `{artifact.path}`"
    except OSError as exc:
        return f"# Could not read artifact\n\n{exc}"


def format_artifact_metadata(artifact: Artifact | None, status: str, workspace: Path) -> str:
    """Render compact metadata for the side panel."""
    lines = [
        f"Status: {status}",
        f"Workspace: {workspace}",
    ]
    if artifact is None:
        lines.append("Selected: none")
        return "\n".join(lines)

    lines.extend(
        [
            "",
            f"Selected: {artifact.relative_path}",
            f"Type: {artifact.kind}",
            f"Group: {artifact.display_group}",
            f"Agent: {artifact.agent or '-'}",
            f"Round: {artifact.round_num if artifact.round_num is not None else '-'}",
            f"Size: {artifact.size_bytes if artifact.size_bytes is not None else '-'} bytes",
            f"Modified: {artifact.modified_at.isoformat(timespec='seconds') if artifact.modified_at else '-'}",
        ]
    )
    if artifact.summary_hint:
        lines.extend(["", f"Summary: {artifact.summary_hint}"])
    return "\n".join(lines)


class ArtifactBrowserApp(App[None]):
    """Full-screen read-only artifact browser."""

    CSS = """
    Screen { layout: vertical; }

    #browser-body {
        height: 1fr;
        width: 100%;
    }

    #artifact-list-pane {
        width: 36;
        min-width: 30;
        height: 100%;
        border: solid $primary-darken-2;
        padding: 0 1;
    }

    #preview-pane {
        width: 1fr;
        height: 100%;
        border: solid $surface-lighten-1;
        padding: 0 1;
    }

    #metadata {
        height: auto;
        padding: 1 0;
        color: $text-muted;
    }

    #artifact-preview {
        height: 1fr;
        overflow-y: auto;
    }

    .pane-title {
        text-style: bold;
        padding: 1 0;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    selected_artifact: reactive[Artifact | None] = reactive(None)

    def __init__(self, workspace: Path, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.workspace = workspace.resolve()
        self.model = build_artifact_browser_model(self.workspace)
        self._artifact_by_id: dict[str, Artifact] = {
            str(item.artifact.path): item.artifact
            for group in self.model.groups
            for item in group.items
        }

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="browser-body"):
            with Vertical(id="artifact-list-pane"):
                yield Static("Artifacts", classes="pane-title")
                yield Static(
                    f"Run status: {self.model.status}",
                    id="run-status",
                )
                yield OptionList(id="artifact-list")
            with Vertical(id="preview-pane"):
                yield Static("Preview", classes="pane-title")
                yield Static(id="metadata")
                yield Markdown("*Select an artifact to preview it.*", id="artifact-preview")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Council Artifact Browser"
        self.sub_title = str(self.workspace)
        option_list = self.query_one("#artifact-list", OptionList)
        for group in self.model.groups:
            for item in group.items:
                option_list.add_option(Option(item.label, id=str(item.artifact.path)))

        if self.model.default_artifact is not None:
            self._select_artifact(self.model.default_artifact)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option_id = getattr(event, "option_id", None)
        artifact = self._artifact_by_id.get(str(option_id))
        if artifact is not None:
            self._select_artifact(artifact)

    def _select_artifact(self, artifact: Artifact) -> None:
        self.selected_artifact = artifact
        self.query_one("#metadata", Static).update(
            format_artifact_metadata(artifact, self.model.status, self.workspace)
        )
        self.query_one("#artifact-preview", Markdown).update(read_artifact_preview(artifact))


def browse_artifacts(workspace: Path) -> None:
    """Run the Textual artifact browser."""
    ArtifactBrowserApp(workspace).run(mouse=True, inline=False)
