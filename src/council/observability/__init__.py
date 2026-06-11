"""Observability for council runs: structured traces and debate analysis."""

from __future__ import annotations

from council.observability.analysis import (
    DivergenceResult,
    FeedMessage,
    LatencyTimeline,
    build_debate_feed,
    build_latency_timeline,
    divergence_score,
    round_diff,
)
from council.observability.traces import RunTrace, Span

__all__ = [
    "DivergenceResult",
    "FeedMessage",
    "LatencyTimeline",
    "RunTrace",
    "Span",
    "build_debate_feed",
    "build_latency_timeline",
    "divergence_score",
    "round_diff",
]
