from __future__ import annotations

import json
from pathlib import Path

import pytest

from council.vis.dashboard import AgentStats, AgentView, CouncilDashboard, TimelineEvent


class TestAgentStats:
    def test_duration_zero_when_not_finished(self) -> None:
        stats = AgentStats(start_time=100.0)
        assert stats.duration_ms == 0.0

    def test_duration_when_finished(self) -> None:
        stats = AgentStats(start_time=100.0, end_time=101.5)
        assert stats.duration_ms == 1500.0


class TestAgentView:
    def test_defaults(self) -> None:
        view = AgentView(name="marcus", display_name="Marcus")
        assert view.state == "PENDING"
        assert view.round_num == 0
        assert view.activity == "Czeka..."
        assert view.progress_pct == 0
        assert view.last_content == ""
        assert view.avatar == "🤖"

    def test_avatar_from_meta(self) -> None:
        dash = CouncilDashboard(["marcus", "elena"])
        assert dash._agents["marcus"].avatar == "🏗️"
        assert dash._agents["elena"].avatar == "🎯"


class TestCouncilDashboard:
    def test_init_creates_agents(self) -> None:
        dash = CouncilDashboard(["marcus", "elena", "kai", "david"])
        assert len(dash._agents) == 4
        assert "marcus" in dash._agents
        assert dash._agents["marcus"].color == "cyan"
        assert dash._agents["marcus"].avatar == "🏗️"

    def test_update_agent(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent(
            "marcus",
            state="WRITING",
            round_num=1,
            activity="Generuje...",
            progress_pct=50,
            content="Hello",
        )
        assert dash._agents["marcus"].state == "WRITING"
        assert dash._agents["marcus"].round_num == 1
        assert dash._agents["marcus"].progress_pct == 50
        assert dash._agents["marcus"].last_content == "Hello"

    def test_progress_clamped(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent("marcus", progress_pct=150)
        assert dash._agents["marcus"].progress_pct == 100
        dash.update_agent("marcus", progress_pct=-10)
        assert dash._agents["marcus"].progress_pct == 0

    def test_update_unknown_agent_ignored(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent("unknown", state="DONE")

    def test_set_round(self) -> None:
        dash = CouncilDashboard(["marcus"], max_rounds=5)
        dash.set_round(2)
        assert dash._current_round == 2
        assert "Runda 2" in dash._logs[-1]

    def test_logs_are_colored(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent("marcus", state="WRITING")
        last_log = dash._logs[-1]
        assert "Marcus" in last_log
        assert "cyan" in last_log

    def test_timeline_tracks_events(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent("marcus", state="WRITING", round_num=1)
        dash.update_agent("marcus", state="DONE", round_num=1)
        assert len(dash._timeline) == 2
        assert dash._timeline[-1].event_type == "DONE"
        assert dash._timeline[-1].round_num == 1

    def test_stats_tracking(self) -> None:
        import time

        dash = CouncilDashboard(["marcus"])
        dash._agents["marcus"].stats.start_time = time.time()
        dash.update_agent("marcus", state="DONE")
        assert dash._agents["marcus"].stats.end_time is not None
        assert dash._agents["marcus"].stats.duration_ms >= 0

    def test_update_agent_stats(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent_stats("marcus", tokens_prompt=100, tokens_completion=50, cost_usd=0.002)
        assert dash._agents["marcus"].stats.tokens_prompt == 100
        assert dash._agents["marcus"].stats.tokens_completion == 50
        assert dash._agents["marcus"].stats.cost_usd == 0.002

    def test_animate_dots(self) -> None:
        dash = CouncilDashboard(["marcus"])
        base = "Wywołanie LLM"
        results = {dash._animate_dots(base) for _ in range(10)}
        assert len(results) <= 4  # cycles through 4 patterns max

    def test_callback_generating(self) -> None:
        dash = CouncilDashboard(["marcus"])
        cb = dash.make_callback()
        cb("marcus", "generating")
        assert dash._agents["marcus"].state == "WRITING"
        assert dash._agents["marcus"].progress_pct == 40

    def test_callback_done_with_content(self) -> None:
        dash = CouncilDashboard(["marcus"])
        cb = dash.make_callback()
        cb("marcus", "done", content="Generated text")
        assert dash._agents["marcus"].state == "DONE"
        assert dash._agents["marcus"].progress_pct == 100
        assert dash._agents["marcus"].last_content == "Generated text"

    def test_callback_error(self) -> None:
        dash = CouncilDashboard(["marcus"])
        cb = dash.make_callback()
        cb("marcus", "error", message="Connection failed")
        assert dash._agents["marcus"].state == "ERROR"
        assert "Connection failed" in dash._agents["marcus"].activity

    def test_callback_round_start(self) -> None:
        dash = CouncilDashboard(["marcus"], max_rounds=3)
        cb = dash.make_callback()
        cb("marcus", "round_start", round_num=2)
        assert dash._current_round == 2
        assert dash._agents["marcus"].round_num == 2

    def test_export_json_structure(self) -> None:
        dash = CouncilDashboard(["marcus"], max_rounds=3)
        dash.update_agent("marcus", state="DONE", round_num=1, progress_pct=100)
        dash.update_agent_stats("marcus", tokens_prompt=10, tokens_completion=20, cost_usd=0.001)
        json_str = dash.export_json()
        data = json.loads(json_str)
        assert data["round"] == 0  # set_round not called
        assert data["max_rounds"] == 3
        assert "marcus" in data["agents"]
        assert data["agents"]["marcus"]["state"] == "DONE"
        assert data["agents"]["marcus"]["progress_pct"] == 100
        assert data["agents"]["marcus"]["tokens"] == 30
        assert "logs" in data
        assert "timeline" in data

    def test_export_json_to_file(self, tmp_path: Path) -> None:
        dash = CouncilDashboard(["marcus"])
        out = tmp_path / "export.json"
        dash.export_json(path=out)
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "agents" in data

    def test_export_html_structure(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent("marcus", state="DONE", content="# Hello\n\nWorld")
        html = dash.export_html()
        assert "Council Run Report" in html
        assert "DONE" in html
        assert "Hello" in html
        assert "</html>" in html

    def test_export_html_to_file(self, tmp_path: Path) -> None:
        dash = CouncilDashboard(["marcus"])
        out = tmp_path / "export.html"
        dash.export_html(path=out)
        assert out.exists()
        assert "Council Run Report" in out.read_text(encoding="utf-8")

    def test_render_agent_panel(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent("marcus", state="WRITING", round_num=1, activity="Test", progress_pct=50)
        panel = dash._render_agent_panel(dash._agents["marcus"])
        assert "Marcus" in str(panel.title)
        assert "WRITING" in panel.renderable
        assert "50%" in panel.renderable
        assert "🏗️" in panel.renderable

    def test_render_header_and_footer(self) -> None:
        dash = CouncilDashboard(["marcus", "elena"], max_rounds=3)
        dash.set_round(1)
        header = dash._render_header()
        footer = dash._render_footer()
        assert "Council" in str(header.renderable)
        assert "Runda 1/3" in str(header.renderable)
        assert "Gotowi" in str(footer.renderable)

    def test_render_timeline(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash._timeline.append(TimelineEvent(0, "marcus", "WRITING", 1))
        panel = dash._render_timeline()
        assert "marcus" in str(panel.renderable).lower()

    def test_render_stats(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash._agents["marcus"].stats.start_time = 100.0
        dash._agents["marcus"].stats.end_time = 101.0
        panel = dash._render_stats()
        assert "Marcus" in str(panel.renderable)
        assert "1000ms" in str(panel.renderable)
