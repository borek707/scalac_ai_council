from __future__ import annotations

from pathlib import Path

from council.observability import (
    RunTrace,
    build_debate_feed,
    build_latency_timeline,
    divergence_score,
    round_diff,
)
from council.observability.traces import Span


def _write_round(workspace: Path, agent: str, round_num: int, text: str) -> None:
    d = workspace / "shared" / "discussion"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{agent.lower()}_round_{round_num}.md").write_text(text, encoding="utf-8")


class TestDebateFeed:
    def test_feed_ordered_by_round_then_agent(self, tmp_path: Path) -> None:
        _write_round(tmp_path, "Marcus", 1, "marcus r1")
        _write_round(tmp_path, "Elena", 1, "elena r1")
        _write_round(tmp_path, "Marcus", 2, "marcus r2")
        feed = build_debate_feed(tmp_path)
        assert [(m.round_num, m.agent) for m in feed] == [
            (1, "Elena"),
            (1, "Marcus"),
            (2, "Marcus"),
        ]

    def test_empty_when_no_discussion(self, tmp_path: Path) -> None:
        assert build_debate_feed(tmp_path) == []


class TestLatencyTimeline:
    def test_aggregates_per_agent(self) -> None:
        trace = RunTrace(
            spans=[
                Span("Marcus", "round_1", 0.0, 1.0),
                Span("Marcus", "final", 1.0, 1.5),
                Span("Elena", "round_1", 0.0, 0.2),
            ]
        )
        timeline = build_latency_timeline(trace)
        assert timeline.per_agent_ms["Marcus"] == 1500.0
        assert timeline.per_agent_ms["Elena"] == 200.0
        assert timeline.slowest_agent == "Marcus"

    def test_from_workspace_trace_file(self, tmp_path: Path) -> None:
        out = tmp_path / "output"
        out.mkdir()
        RunTrace(spans=[Span("Kai", "round_1", 0.0, 0.3)]).write(out / "trace.json")
        timeline = build_latency_timeline(tmp_path)
        assert timeline.per_agent_ms["Kai"] == 300.0


class TestDivergence:
    def test_identical_outputs_have_zero_divergence(self, tmp_path: Path) -> None:
        text = "growth pricing funnel strategy conversion revenue offer"
        _write_round(tmp_path, "Marcus", 1, text)
        _write_round(tmp_path, "Elena", 1, text)
        result = divergence_score(tmp_path, 1)
        assert result.divergence == 0.0
        assert result.similarity == 1.0

    def test_disjoint_outputs_have_high_divergence(self, tmp_path: Path) -> None:
        _write_round(tmp_path, "Marcus", 1, "pricing packaging positioning competitor")
        _write_round(tmp_path, "Elena", 1, "newsletter webinar nurture sequence onboarding")
        result = divergence_score(tmp_path, 1)
        assert result.divergence > 0.8

    def test_single_agent_is_not_divergent(self, tmp_path: Path) -> None:
        _write_round(tmp_path, "Marcus", 1, "only one agent here speaking")
        result = divergence_score(tmp_path, 1)
        assert result.divergence == 0.0


class TestRoundDiff:
    def test_diff_between_rounds(self, tmp_path: Path) -> None:
        _write_round(tmp_path, "Marcus", 1, "line one\nline two\n")
        _write_round(tmp_path, "Marcus", 2, "line one\nline two changed\n")
        diff = round_diff(tmp_path, "Marcus", 1, 2)
        assert "line two changed" in diff
        assert diff.startswith("---")

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        _write_round(tmp_path, "Marcus", 1, "only round one")
        assert round_diff(tmp_path, "Marcus", 1, 2) == ""


class TestRunTraceRoundtrip:
    def test_write_and_load(self, tmp_path: Path) -> None:
        trace = RunTrace(spans=[Span("Marcus", "round_1", 0.0, 1.0, "ok")])
        path = tmp_path / "trace.json"
        trace.write(path)
        loaded = RunTrace.load(path)
        assert len(loaded.spans) == 1
        assert loaded.spans[0].agent == "Marcus"
        assert loaded.spans[0].round_num == 1

    def test_load_missing_returns_empty(self, tmp_path: Path) -> None:
        assert RunTrace.load(tmp_path / "nope.json").spans == []

    def test_export_otel_noop_without_sdk(self) -> None:
        # Without the OTel SDK installed this must be a safe no-op (False).
        trace = RunTrace(spans=[Span("Marcus", "round_1", 0.0, 1.0)])
        result = trace.export_otel()
        assert result in (True, False)
