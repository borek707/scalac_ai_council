"""Debate analysis over council run artifacts.

All functions read from the workspace's discussion files and (optionally) the
structured trace.  They never raise on missing data and are pure/​testable.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path

from council.observability.traces import TRACE_FILENAME, RunTrace, Span

_ROUND_FILE_RE = re.compile(r"^(?P<agent>.+)_round_(?P<round>\d+)\.md$")
_WORD_RE = re.compile(r"[a-z]{5,}")


# ---------------------------------------------------------------------------
# #52 Debate chat view — chronological feed
# ---------------------------------------------------------------------------


@dataclass
class FeedMessage:
    """One message in the chronological debate feed."""

    round_num: int
    agent: str
    content: str
    path: Path


def _discussion_dir(workspace: Path) -> Path:
    return workspace / "shared" / "discussion"


def build_debate_feed(workspace: Path) -> list[FeedMessage]:
    """Return all agent round messages ordered by (round, agent)."""
    directory = _discussion_dir(workspace)
    if not directory.is_dir():
        return []

    messages: list[FeedMessage] = []
    for path in directory.glob("*_round_*.md"):
        match = _ROUND_FILE_RE.match(path.name)
        if not match:
            continue
        agent = match.group("agent").capitalize()
        round_num = int(match.group("round"))
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            content = ""
        messages.append(
            FeedMessage(round_num=round_num, agent=agent, content=content, path=path)
        )

    messages.sort(key=lambda m: (m.round_num, m.agent.lower()))
    return messages


# ---------------------------------------------------------------------------
# #53 Per-agent latency timeline
# ---------------------------------------------------------------------------


@dataclass
class LatencyTimeline:
    """Per-agent latency aggregated from a run trace."""

    per_agent_ms: dict[str, float] = field(default_factory=dict)
    per_phase_ms: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def slowest_agent(self) -> str | None:
        if not self.per_agent_ms:
            return None
        return max(self.per_agent_ms, key=lambda a: self.per_agent_ms[a])

    @property
    def total_ms(self) -> float:
        return sum(self.per_agent_ms.values())


def build_latency_timeline(trace_or_workspace: RunTrace | Path) -> LatencyTimeline:
    """Build a latency timeline from a :class:`RunTrace` or a workspace path."""
    if isinstance(trace_or_workspace, Path):
        trace = RunTrace.load(trace_or_workspace / "output" / TRACE_FILENAME)
    else:
        trace = trace_or_workspace

    timeline = LatencyTimeline()
    for span in trace.spans:
        timeline.per_agent_ms[span.agent] = (
            timeline.per_agent_ms.get(span.agent, 0.0) + span.duration_ms
        )
        timeline.per_phase_ms.setdefault(span.phase, {})[span.agent] = span.duration_ms
    return timeline


# ---------------------------------------------------------------------------
# #54 Debate divergence meter
# ---------------------------------------------------------------------------


@dataclass
class DivergenceResult:
    """How much agents disagree in a given round (1.0 = fully divergent)."""

    round_num: int
    divergence: float
    similarity: float
    agents: list[str]


def _round_word_sets(workspace: Path, round_num: int) -> dict[str, set[str]]:
    directory = _discussion_dir(workspace)
    out: dict[str, set[str]] = {}
    if not directory.is_dir():
        return out
    for path in directory.glob(f"*_round_{round_num}.md"):
        match = _ROUND_FILE_RE.match(path.name)
        if not match:
            continue
        agent = match.group("agent").capitalize()
        try:
            text = path.read_text(encoding="utf-8").lower()
        except OSError:
            continue
        words = set(_WORD_RE.findall(text))
        if words:
            out[agent] = words
    return out


def divergence_score(workspace: Path, round_num: int) -> DivergenceResult:
    """Compute divergence for a round via mean pairwise Jaccard distance."""
    word_sets = _round_word_sets(workspace, round_num)
    agents = sorted(word_sets)
    if len(agents) < 2:
        return DivergenceResult(
            round_num=round_num, divergence=0.0, similarity=1.0, agents=agents
        )

    similarities: list[float] = []
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            a, b = word_sets[agents[i]], word_sets[agents[j]]
            union = a | b
            if not union:
                continue
            similarities.append(len(a & b) / len(union))

    mean_similarity = sum(similarities) / len(similarities) if similarities else 0.0
    return DivergenceResult(
        round_num=round_num,
        divergence=round(1.0 - mean_similarity, 4),
        similarity=round(mean_similarity, 4),
        agents=agents,
    )


# ---------------------------------------------------------------------------
# #55 Round-over-round diff
# ---------------------------------------------------------------------------


def _agent_round_file(workspace: Path, agent: str, round_num: int) -> Path:
    return _discussion_dir(workspace) / f"{agent.lower()}_round_{round_num}.md"


def round_diff(workspace: Path, agent: str, round_a: int, round_b: int) -> str:
    """Return a unified diff of *agent*'s output between two rounds.

    Returns an empty string when either file is missing.
    """
    path_a = _agent_round_file(workspace, agent, round_a)
    path_b = _agent_round_file(workspace, agent, round_b)
    if not path_a.exists() or not path_b.exists():
        return ""
    try:
        text_a = path_a.read_text(encoding="utf-8").splitlines()
        text_b = path_b.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    diff = difflib.unified_diff(
        text_a,
        text_b,
        fromfile=f"{agent} round {round_a}",
        tofile=f"{agent} round {round_b}",
        lineterm="",
    )
    return "\n".join(diff)


__all__ = [
    "DivergenceResult",
    "FeedMessage",
    "LatencyTimeline",
    "Span",
    "build_debate_feed",
    "build_latency_timeline",
    "divergence_score",
    "round_diff",
]
