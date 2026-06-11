"""Structured output schemas for council artifacts.

Provides versioned Pydantic models for:

* the run **manifest** (``output/manifest.json``) — a product contract used
  by the CLI ``--review``, the dashboard, and any external integration;
* **final deliverables** — a typed representation that can be validated and
  rendered to the markdown that remains the public artifact format.

Markdown stays the user-facing format; these schemas add validation,
versioning, and a stable shape for tooling.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# Bump when the manifest/deliverable shape changes in a backwards-incompatible
# way.  Readers should tolerate a missing version (legacy v3.x manifests).
SCHEMA_VERSION = "1.0"


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


class ManifestFiles(BaseModel):
    """Recorded artifact paths for a run."""

    proposal: str | None = None
    agents_dir: str | None = None
    agent_outputs: dict[str, str] = Field(default_factory=dict)
    final_deliverables: dict[str, str] = Field(default_factory=dict)


class Manifest(BaseModel):
    """Versioned manifest written after a completed council run."""

    schema_version: str = SCHEMA_VERSION
    generated_at: str
    company: str
    product: str
    provider: str
    model: str | None = None
    rounds_completed: int = Field(ge=0)
    max_rounds: int = Field(ge=0)
    status: str = "complete"
    agents: list[str] = Field(default_factory=list)
    files: ManifestFiles = Field(default_factory=ManifestFiles)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Manifest:
        """Validate a manifest dict, tolerating legacy (unversioned) layouts.

        Legacy manifests (council v3.x) had no ``schema_version`` or
        ``status`` field; defaults fill those in so old runs remain readable.
        """
        payload = dict(data)
        payload.setdefault("schema_version", "0")
        files = payload.get("files")
        if isinstance(files, dict):
            payload["files"] = ManifestFiles(
                proposal=files.get("proposal"),
                agents_dir=files.get("agents_dir"),
                agent_outputs=files.get("agent_outputs", {}) or {},
                final_deliverables=files.get("final_deliverables", {}) or {},
            )
        return cls.model_validate(payload)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict suitable for ``json.dump``."""
        return self.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Final deliverables
# ---------------------------------------------------------------------------


class DeliverableSection(BaseModel):
    """One titled section of a final deliverable."""

    heading: str = Field(min_length=1)
    content: str = Field(min_length=1)


class FinalDeliverable(BaseModel):
    """Typed representation of a single agent's final deliverable."""

    schema_version: str = SCHEMA_VERSION
    agent: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    sections: list[DeliverableSection] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        """Render the deliverable to the public markdown format."""
        lines: list[str] = [f"# {self.title}", "", f"_by {self.agent}_", "", self.summary, ""]
        for section in self.sections:
            lines.append(f"## {section.heading}")
            lines.append("")
            lines.append(section.content)
            lines.append("")
        if self.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            lines.extend(f"- {rec}" for rec in self.recommendations)
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "SCHEMA_VERSION",
    "DeliverableSection",
    "FinalDeliverable",
    "Manifest",
    "ManifestFiles",
]
