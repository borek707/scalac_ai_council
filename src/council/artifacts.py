"""Artifact discovery layer for the AI Marketing Council.

Provides a stable, manifest-first view of all artifacts produced by a
council run.  Falls back to a filesystem scan when no manifest is
present, and never raises on missing files.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

ArtifactKind = Literal["proposal", "agent", "discussion", "manifest"]

_KIND_ORDER: dict[ArtifactKind, int] = {
    "proposal": 0,
    "agent": 1,
    "discussion": 2,
    "manifest": 3,
}


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
    agent: Optional[str]
    path: Path
    exists: bool = field(default=False)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_artifact(
    path: Path,
    kind: ArtifactKind,
    *,
    agent: Optional[str] = None,
    title: Optional[str] = None,
    artifact_id: Optional[str] = None,
) -> Artifact:
    """Construct an :class:`Artifact`, filling in defaults from *path*."""
    resolved = path.resolve()
    return Artifact(
        id=artifact_id or str(resolved),
        title=title or path.stem,
        kind=kind,
        agent=agent,
        path=resolved,
        exists=resolved.exists(),
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
    artifacts.append(
        _make_artifact(manifest_path, "manifest", title="manifest")
    )

    files: dict = data.get("files", {})

    # Proposal
    proposal_str = files.get("proposal")
    if proposal_str:
        artifacts.append(
            _make_artifact(Path(proposal_str), "proposal", title="proposal")
        )

    # Final agent deliverables (preferred over raw agent_outputs)
    final_deliverables: dict[str, str] = files.get("final_deliverables", {})
    for agent_name, path_str in final_deliverables.items():
        p = Path(path_str)
        artifacts.append(
            _make_artifact(
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
                p,
                "discussion",
                agent=agent_name,
                title=p.stem,
            )
        )

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
    artifacts.append(_make_artifact(proposal_primary, "proposal", title="proposal"))

    # Legacy: FINAL_PROPOSAL.md at workspace root
    legacy_proposal = workspace / "FINAL_PROPOSAL.md"
    if legacy_proposal.exists():
        artifacts.append(
            _make_artifact(legacy_proposal, "proposal", title="FINAL_PROPOSAL")
        )

    # -- Agent outputs: output/agents/*.md ------------------------------------
    agents_dir = workspace / "output" / "agents"
    if agents_dir.is_dir():
        for p in sorted(agents_dir.glob("*.md")):
            # Infer agent name from the file stem (e.g. "marcus_offer" → "marcus")
            agent_name = p.stem.split("_")[0].capitalize() if "_" in p.stem else p.stem
            artifacts.append(
                _make_artifact(p, "agent", agent=agent_name, title=p.stem)
            )

    # -- Other markdown files directly under output/ (but not agents/) --------
    output_dir = workspace / "output"
    if output_dir.is_dir():
        for p in sorted(output_dir.glob("*.md")):
            # proposal.md is already captured above
            if p.name == "proposal.md":
                continue
            artifacts.append(_make_artifact(p, "agent", title=p.stem))

    # -- Discussion round files: shared/discussion/*_round_*.md ---------------
    discussion_dir = workspace / "shared" / "discussion"
    if discussion_dir.is_dir():
        for p in sorted(discussion_dir.glob("*_round_*.md")):
            # File naming: {agent_lower}_round_{n}.md
            parts = p.stem.split("_round_")
            agent_name = parts[0].capitalize() if parts else p.stem
            artifacts.append(
                _make_artifact(p, "discussion", agent=agent_name, title=p.stem)
            )

    # -- Manifest -------------------------------------------------------------
    manifest_path = workspace / "output" / "manifest.json"
    artifacts.append(_make_artifact(manifest_path, "manifest", title="manifest"))

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


def get_default_artifact(artifacts: list[Artifact]) -> Optional[Artifact]:
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
