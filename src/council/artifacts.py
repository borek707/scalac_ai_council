"""Artifact discovery layer for the AI Marketing Council.

Provides a stable, manifest-first view of all artifacts produced by a
council run.  Falls back to a filesystem scan when no manifest is
present, and never raises on missing files.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

ArtifactKind = Literal["proposal", "agent", "discussion", "manifest", "trace", "review", "input"]
RunStatus = Literal["complete", "in_progress", "interrupted", "missing_manifest"]

_KIND_ORDER: dict[ArtifactKind, int] = {
    "proposal": 0,
    "agent": 1,
    "discussion": 2,
    "manifest": 3,
    "trace": 4,
    "review": 5,
    "input": 6,
}

_DISPLAY_GROUPS: dict[ArtifactKind, str] = {
    "proposal": "Proposal",
    "agent": "Agent Outputs",
    "discussion": "Discussion",
    "manifest": "Manifest",
    "trace": "Trace",
    "review": "Review",
    "input": "Inputs",
}

_ROUND_RE = re.compile(r"_round_(?P<round>\d+)$")


@dataclass
class Artifact:
    """A single discoverable artifact produced by a council run.

    Attributes
    ----------
    id:
        Stable identifier derived from the artifact's relative path or a
        slug from the manifest.
    title:
        Human-readable display name (file stem or manifest key).
    kind:
        Category of the artifact (proposal / agent / discussion / manifest).
    agent:
        Name of the agent that produced this artifact, or ``None`` for
        non-agent artifacts (proposal, manifest, …).
    path:
        Absolute ``Path`` to the file.  May not exist on disk when
        ``exists`` is ``False``.
    exists:
        ``True`` when ``path`` exists on disk at discovery time.
    """

    id: str
    title: str
    kind: ArtifactKind
    agent: str | None
    path: Path
    exists: bool = field(default=False)
    relative_path: Path = field(default_factory=Path)
    size_bytes: int | None = None
    modified_at: datetime | None = None
    round_num: int | None = None
    display_group: str = ""
    summary_hint: str = ""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_artifact_path(workspace: Path, path: Path) -> Path:
    """Resolve manifest paths relative to *workspace* when needed."""
    if path.is_absolute():
        return path.resolve()
    return (workspace / path).resolve()


def _relative_to_workspace(workspace: Path, path: Path) -> Path:
    try:
        return path.relative_to(workspace)
    except ValueError:
        return path


def _stat_metadata(path: Path) -> tuple[bool, int | None, datetime | None]:
    try:
        stat = path.stat()
    except OSError:
        return False, None, None
    return True, stat.st_size, datetime.fromtimestamp(stat.st_mtime)


def _infer_round_num(path: Path) -> int | None:
    match = _ROUND_RE.search(path.stem)
    if not match:
        return None
    return int(match.group("round"))


def _summary_hint(path: Path) -> str:
    if path.suffix.lower() not in {".md", ".txt"}:
        return ""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    heading_fallback = ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            heading_fallback = heading_fallback or stripped.lstrip("#").strip()
            continue
        clean = stripped
        if clean:
            return clean[:160]
    return heading_fallback[:160]


def _discover_support_files(workspace: Path) -> list[Artifact]:
    """Return browser-visible supporting inputs, traces, and reviews."""
    known: list[tuple[Path, ArtifactKind, str]] = [
        (workspace / "output" / "trace.json", "trace", "trace"),
        (
            workspace / "output" / "artifacts" / "reviews" / "review.md",
            "review",
            "review",
        ),
        (
            workspace / "output" / "artifacts" / "reviews" / "review.json",
            "review",
            "review_json",
        ),
        (workspace / "config.json", "input", "config"),
        (workspace / "shared" / "brief.md", "input", "brief"),
    ]
    return [
        _make_artifact(workspace, path, kind, title=title)
        for path, kind, title in known
        if path.exists()
    ]


def _make_artifact(
    workspace: Path,
    path: Path,
    kind: ArtifactKind,
    *,
    agent: str | None = None,
    title: str | None = None,
    artifact_id: str | None = None,
) -> Artifact:
    """Construct an :class:`Artifact`, filling in defaults from *path*."""
    resolved = _resolve_artifact_path(workspace, path)
    relative_path = _relative_to_workspace(workspace, resolved)
    exists, size_bytes, modified_at = _stat_metadata(resolved)
    return Artifact(
        id=artifact_id or str(relative_path),
        title=title or path.stem,
        kind=kind,
        agent=agent,
        path=resolved,
        exists=exists,
        relative_path=relative_path,
        size_bytes=size_bytes,
        modified_at=modified_at,
        round_num=_infer_round_num(resolved),
        display_group=_DISPLAY_GROUPS[kind],
        summary_hint=_summary_hint(resolved),
    )


def _discover_from_manifest(workspace: Path) -> list[Artifact] | None:
    """Try to build the artifact list from ``output/manifest.json``.

    Returns ``None`` when no manifest exists so the caller can fall back
    to filesystem scanning.  Never raises.
    """
    manifest_path = (workspace / "output" / "manifest.json").resolve()
    if not manifest_path.exists():
        return None

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not parse manifest %s: %s", manifest_path, exc)
        return None

    artifacts: list[Artifact] = []

    # Manifest itself
    artifacts.append(_make_artifact(workspace, manifest_path, "manifest", title="manifest"))

    files: dict[str, Any] = data.get("files", {})

    # Proposal
    proposal_str = files.get("proposal")
    if proposal_str:
        artifacts.append(
            _make_artifact(workspace, Path(proposal_str), "proposal", title="proposal")
        )

    # Final agent deliverables (preferred over raw agent_outputs)
    final_deliverables: dict[str, str] = files.get("final_deliverables", {})
    for agent_name, path_str in final_deliverables.items():
        p = Path(path_str)
        artifacts.append(
            _make_artifact(
                workspace,
                p,
                "agent",
                agent=agent_name,
                title=p.stem,
            )
        )

    # Round outputs filed under agent_outputs (discussion kind)
    agent_outputs: dict[str, str] = files.get("agent_outputs", {})
    for agent_name, path_str in agent_outputs.items():
        p = Path(path_str)
        artifacts.append(
            _make_artifact(
                workspace,
                p,
                "discussion",
                agent=agent_name,
                title=p.stem,
            )
        )

    reviews = data.get("reviews", {})
    review_files: dict[str, str] = reviews.get("files", {}) if isinstance(reviews, dict) else {}
    for title, path_str in review_files.items():
        if path_str:
            artifacts.append(_make_artifact(workspace, Path(path_str), "review", title=title))

    artifacts.extend(_discover_support_files(workspace))

    logger.debug("Manifest discovery: found %d artifacts", len(artifacts))
    return artifacts


def _discover_from_filesystem(workspace: Path) -> list[Artifact]:
    """Scan the workspace for known artifact locations.

    Never raises.  Sets ``exists=False`` for every path that does not
    exist on disk (which by construction cannot happen here, but the
    dataclass field is set correctly via :func:`_make_artifact`).
    """
    artifacts: list[Artifact] = []

    # -- Proposal paths -------------------------------------------------------
    # Primary: output/proposal.md
    proposal_primary = workspace / "output" / "proposal.md"
    artifacts.append(_make_artifact(workspace, proposal_primary, "proposal", title="proposal"))

    # Legacy: FINAL_PROPOSAL.md at workspace root
    legacy_proposal = workspace / "FINAL_PROPOSAL.md"
    if legacy_proposal.exists():
        artifacts.append(
            _make_artifact(workspace, legacy_proposal, "proposal", title="FINAL_PROPOSAL")
        )

    # -- Agent outputs: output/agents/*.md ------------------------------------
    agents_dir = workspace / "output" / "agents"
    if agents_dir.is_dir():
        for p in sorted(agents_dir.glob("*.md")):
            # Infer agent name from the file stem (e.g. "marcus_offer" → "marcus")
            agent_name = p.stem.split("_")[0].capitalize() if "_" in p.stem else p.stem
            artifacts.append(_make_artifact(workspace, p, "agent", agent=agent_name, title=p.stem))

    # -- Other markdown files directly under output/ (but not agents/) --------
    output_dir = workspace / "output"
    if output_dir.is_dir():
        for p in sorted(output_dir.glob("*.md")):
            # proposal.md is already captured above
            if p.name == "proposal.md":
                continue
            artifacts.append(_make_artifact(workspace, p, "agent", title=p.stem))

    # -- Discussion round files: shared/discussion/*_round_*.md ---------------
    discussion_dir = workspace / "shared" / "discussion"
    if discussion_dir.is_dir():
        for p in sorted(discussion_dir.glob("*_round_*.md")):
            # File naming: {agent_lower}_round_{n}.md
            parts = p.stem.split("_round_")
            agent_name = parts[0].capitalize() if parts else p.stem
            artifacts.append(
                _make_artifact(workspace, p, "discussion", agent=agent_name, title=p.stem)
            )

    # -- Manifest -------------------------------------------------------------
    manifest_path = workspace / "output" / "manifest.json"
    artifacts.append(_make_artifact(workspace, manifest_path, "manifest", title="manifest"))
    artifacts.extend(_discover_support_files(workspace))

    logger.debug("Filesystem discovery: found %d artifacts", len(artifacts))
    return artifacts


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def discover_artifacts(workspace: Path) -> list[Artifact]:
    """Discover all artifacts in *workspace*.

    Tries manifest-first: reads ``output/manifest.json`` when it exists
    and builds the artifact list from its recorded paths.  Falls back to
    a filesystem scan covering:

    * ``output/proposal.md``
    * ``output/agents/*.md``
    * ``FINAL_PROPOSAL.md`` (legacy root-level file)
    * ``output/*.md``
    * ``shared/discussion/*_round_*.md``

    Deduplicates by resolved path and returns a stable list sorted by
    ``kind`` then ``title``.  Never raises on missing files — sets
    ``exists=False`` for paths that are absent from disk.

    Parameters
    ----------
    workspace:
        Root directory of a council run (the value passed as ``--output``
        to the CLI, *without* the ``/output`` suffix).

    Returns
    -------
    list[Artifact]
        Sorted, deduplicated list of discovered artifacts.
    """
    workspace = workspace.resolve()

    raw: list[Artifact] = _discover_from_manifest(workspace) or _discover_from_filesystem(workspace)

    # Deduplicate by resolved path, preserving first occurrence
    seen: set[Path] = set()
    unique: list[Artifact] = []
    for artifact in raw:
        if artifact.path not in seen:
            seen.add(artifact.path)
            unique.append(artifact)

    # Stable sort: kind order first, then title alphabetically
    unique.sort(key=lambda a: (_KIND_ORDER.get(a.kind, 99), a.title.lower()))

    return unique


def discover_run_status(workspace: Path) -> RunStatus:
    """Return a coarse status for a council workspace.

    Missing manifests are not treated as empty by default: if any known
    artifact exists, the run is considered interrupted because the writer did
    not reach manifest creation.
    """
    workspace = workspace.resolve()
    manifest_path = workspace / "output" / "manifest.json"
    if not manifest_path.exists():
        existing = [
            artifact for artifact in _discover_from_filesystem(workspace) if artifact.exists
        ]
        return "interrupted" if existing else "missing_manifest"

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "interrupted"

    status = data.get("status")
    if status in {"complete", "completed", "success"}:
        return "complete"
    if status in {"running", "in_progress"}:
        return "in_progress"
    if status in {"interrupted", "failed", "error"}:
        return "interrupted"

    rounds_completed = data.get("rounds_completed")
    max_rounds = data.get("max_rounds")
    if isinstance(rounds_completed, int) and isinstance(max_rounds, int):
        return "complete" if rounds_completed >= max_rounds else "in_progress"
    return "complete"


def get_default_artifact(artifacts: list[Artifact]) -> Artifact | None:
    """Return the most relevant single artifact from a discovered list.

    Selection priority:
    1. ``output/proposal.md`` or any artifact whose title is ``"proposal"``
       (kind == ``"proposal"`` and path ends with ``proposal.md``).
    2. Any artifact with title ``"FINAL_PROPOSAL"`` (legacy path).
    3. First artifact of kind ``"agent"`` (first agent output alphabetically).

    Returns ``None`` when *artifacts* is empty.

    Parameters
    ----------
    artifacts:
        List returned by :func:`discover_artifacts`.
    """
    if not artifacts:
        return None

    # 1. Primary proposal: kind="proposal", file named proposal.md
    for a in artifacts:
        if a.kind == "proposal" and a.path.name == "proposal.md":
            return a

    # 2. Legacy FINAL_PROPOSAL
    for a in artifacts:
        if a.kind == "proposal" and a.title.upper() == "FINAL_PROPOSAL":
            return a

    # 3. Any proposal-kind artifact
    for a in artifacts:
        if a.kind == "proposal":
            return a

    # 4. First agent output
    for a in artifacts:
        if a.kind == "agent":
            return a

    return None
