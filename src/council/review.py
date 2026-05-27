"""AI-assisted artifact quality review for the AI Marketing Council.

Provides a ReviewRunner that evaluates council artifacts using an LLM
and writes human-readable and structured output summaries.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from council.artifacts import Artifact
from council.llm.provider import LLMProvider

logger = logging.getLogger(__name__)

_MAX_CONTENT_CHARS = 3000

_REVIEW_SYSTEM = (
    "You are an expert content reviewer for marketing strategy documents. "
    "Evaluate artifacts with precision and provide actionable, specific feedback."
)

_REVIEW_PROMPT_TEMPLATE = """\
Review the following marketing artifact and evaluate it on four dimensions:
1. Clarity — Is the content easy to understand? Is the language precise?
2. Completeness — Does it cover all necessary aspects? Are there obvious gaps?
3. Actionability — Can the reader act on this? Are recommendations concrete?
4. Overall quality — Holistic assessment of the artifact.

Return your review as a JSON object with exactly these fields:
- "score": a number from 1 to 10 (overall quality score)
- "summary": a 2-3 sentence summary of the artifact's quality
- "suggestions": a list of 2-5 specific, actionable improvement suggestions

Artifact title: {title}
Artifact content:
---
{content}
---

Respond with valid JSON only. No markdown fences, no extra text."""


def _build_prompt(artifact: Artifact, content: str) -> str:
    """Build a bounded review prompt, truncating content to _MAX_CONTENT_CHARS."""
    bounded = content[:_MAX_CONTENT_CHARS]
    if len(content) > _MAX_CONTENT_CHARS:
        bounded += "\n\n[...content truncated for review...]"
    return _REVIEW_PROMPT_TEMPLATE.format(title=artifact.title, content=bounded)


def _parse_review_response(
    artifact: Artifact, raw: str, reviewed_at: str
) -> ReviewResult:
    """Parse LLM JSON response into a ReviewResult.

    Falls back gracefully if the response is not valid JSON.
    """
    text = raw.strip()
    # Strip optional markdown code fences the model may emit despite instructions
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop opening fence line and closing fence line if present
        inner = [l for l in lines if not l.startswith("```")]
        text = "\n".join(inner).strip()

    try:
        data = json.loads(text)
        score_raw = data.get("score")
        score: Optional[float] = float(score_raw) if score_raw is not None else None
        if score is not None:
            score = max(0.0, min(10.0, score))
        summary = str(data.get("summary", "")).strip()
        suggestions_raw = data.get("suggestions", [])
        suggestions = [str(s).strip() for s in suggestions_raw if str(s).strip()]
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.warning(
            "Could not parse review response for artifact %r: %s", artifact.id, exc
        )
        score = None
        summary = raw.strip()[:500]
        suggestions = []

    return ReviewResult(
        artifact_id=artifact.id,
        artifact_title=artifact.title,
        score=score,
        summary=summary,
        suggestions=suggestions,
        reviewed_at=reviewed_at,
    )


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass
class ReviewResult:
    """Quality review result for a single artifact.

    Attributes
    ----------
    artifact_id:
        Stable identifier of the reviewed artifact (matches :attr:`Artifact.id`).
    artifact_title:
        Human-readable name of the artifact.
    score:
        Overall quality score in the range 0–10, or ``None`` if scoring failed.
    summary:
        2-3 sentence narrative summary of the review.
    suggestions:
        List of specific, actionable improvement suggestions.
    reviewed_at:
        ISO 8601 timestamp (UTC) when the review was produced.
    """

    artifact_id: str
    artifact_title: str
    score: Optional[float]
    summary: str
    suggestions: list[str] = field(default_factory=list)
    reviewed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


class ReviewRunner:
    """Runs AI-assisted quality reviews over a list of artifacts.

    Parameters
    ----------
    provider:
        An :class:`~council.llm.provider.LLMProvider` instance used to call
        the LLM for each review.
    workspace:
        Root directory of the council run (same value passed to the
        orchestrator — without the ``/output`` suffix).
    """

    def __init__(self, provider: LLMProvider, workspace: Path) -> None:
        self.provider = provider
        self.workspace = workspace.resolve()

    # ------------------------------------------------------------------
    # Review
    # ------------------------------------------------------------------

    async def review_artifacts(self, artifacts: list[Artifact]) -> list[ReviewResult]:
        """Review a list of artifacts and return structured results.

        Artifacts where :attr:`~Artifact.exists` is ``False`` are skipped
        silently.  An empty artifact list returns an empty list immediately.

        Parameters
        ----------
        artifacts:
            Artifacts to review, typically from :func:`~council.artifacts.discover_artifacts`.

        Returns
        -------
        list[ReviewResult]
            One result per artifact that was successfully reviewed.
        """
        if not artifacts:
            logger.debug("review_artifacts: empty artifact list, returning []")
            return []

        reviewable = [a for a in artifacts if a.exists]
        if not reviewable:
            logger.info("review_artifacts: no artifacts exist on disk, returning []")
            return []

        results: list[ReviewResult] = []
        for artifact in reviewable:
            reviewed_at = datetime.now(timezone.utc).isoformat()
            try:
                content = artifact.path.read_text(encoding="utf-8")
            except OSError as exc:
                logger.warning("Could not read artifact %r: %s", artifact.id, exc)
                results.append(
                    ReviewResult(
                        artifact_id=artifact.id,
                        artifact_title=artifact.title,
                        score=None,
                        summary=f"Could not read artifact file: {exc}",
                        suggestions=[],
                        reviewed_at=reviewed_at,
                    )
                )
                continue

            prompt = _build_prompt(artifact, content)
            try:
                response = await self.provider.generate(
                    prompt=prompt,
                    system=_REVIEW_SYSTEM,
                    temperature=0.3,
                    max_tokens=1024,
                )
                result = _parse_review_response(artifact, response.content, reviewed_at)
            except Exception as exc:  # noqa: BLE001
                logger.error("LLM review failed for artifact %r: %s", artifact.id, exc)
                result = ReviewResult(
                    artifact_id=artifact.id,
                    artifact_title=artifact.title,
                    score=None,
                    summary=f"Review failed due to provider error: {exc}",
                    suggestions=[],
                    reviewed_at=reviewed_at,
                )

            results.append(result)
            logger.info(
                "Reviewed artifact %r — score: %s", artifact.title, result.score
            )

        return results

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def save_results(self, results: list[ReviewResult]) -> Path:
        """Persist review results to disk and update the workspace manifest.

        Writes two files under ``output/artifacts/reviews/``:

        * ``review.md``  — human-readable markdown summary
        * ``review.json`` — structured JSON array of all results

        Also adds a ``"reviews"`` key to ``output/manifest.json`` when that
        file exists.

        Parameters
        ----------
        results:
            List of :class:`ReviewResult` objects to persist.

        Returns
        -------
        Path
            Absolute path to the written ``review.md`` file.
        """
        reviews_dir = self.workspace / "output" / "artifacts" / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)

        md_path = reviews_dir / "review.md"
        json_path = reviews_dir / "review.json"

        # --- Markdown summary ---
        md_lines: list[str] = [
            "# Artifact Quality Review",
            "",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"**Artifacts reviewed:** {len(results)}",
            "",
            "---",
            "",
        ]

        if not results:
            md_lines.append("*No artifacts were reviewed.*")
        else:
            for result in results:
                score_display = f"{result.score:.1f}/10" if result.score is not None else "N/A"
                md_lines += [
                    f"## {result.artifact_title}",
                    "",
                    f"**Score:** {score_display}  ",
                    f"**Reviewed at:** {result.reviewed_at}",
                    "",
                    "### Summary",
                    "",
                    result.summary,
                    "",
                ]
                if result.suggestions:
                    md_lines += ["### Suggestions", ""]
                    for suggestion in result.suggestions:
                        md_lines.append(f"- {suggestion}")
                    md_lines.append("")
                md_lines.append("---")
                md_lines.append("")

        md_path.write_text("\n".join(md_lines), encoding="utf-8")
        logger.info("Review markdown written to %s", md_path)

        # --- JSON structured output ---
        json_data = [
            {
                "artifact_id": r.artifact_id,
                "artifact_title": r.artifact_title,
                "score": r.score,
                "summary": r.summary,
                "suggestions": r.suggestions,
                "reviewed_at": r.reviewed_at,
            }
            for r in results
        ]
        json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        logger.info("Review JSON written to %s", json_path)

        # --- Update manifest ---
        manifest_path = self.workspace / "output" / "manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["reviews"] = {
                    "reviewed_at": datetime.now(timezone.utc).isoformat(),
                    "artifact_count": len(results),
                    "files": {
                        "review_md": str(md_path),
                        "review_json": str(json_path),
                    },
                }
                manifest_path.write_text(
                    json.dumps(manifest, indent=2), encoding="utf-8"
                )
                logger.info("Manifest updated with reviews key at %s", manifest_path)
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("Could not update manifest %s: %s", manifest_path, exc)

        return md_path
