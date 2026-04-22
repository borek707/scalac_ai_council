from __future__ import annotations

import pytest

from council.vis.dashboard import AgentView, CouncilDashboard


class TestAgentView:
    def test_defaults(self) -> None:
        view = AgentView(name="marcus", display_name="Marcus")
        assert view.state == "PENDING"
        assert view.round_num == 0
        assert view.activity == "Czeka..."
        assert view.progress_pct == 0
        assert view.last_content == ""


class TestCouncilDashboard:
    def test_init_creates_agents(self) -> None:
        dash = CouncilDashboard(["marcus", "elena", "kai", "david"])
        assert len(dash._agents) == 4
        assert "marcus" in dash._agents
        assert dash._agents["marcus"].color == "cyan"

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
        # Should not raise

    def test_set_round(self) -> None:
        dash = CouncilDashboard(["marcus"], max_rounds=5)
        dash.set_round(2)
        assert dash._current_round == 2
        assert "Runda 2" in dash._logs[-1]

    def test_logs_on_state_change(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent("marcus", state="WRITING")
        assert any("Marcus: WRITING" in log for log in dash._logs)

    def test_callback_generating(self) -> None:
        dash = CouncilDashboard(["marcus"])
        cb = dash.make_callback()
        cb("marcus", "generating")
        assert dash._agents["marcus"].state == "WRITING"
        assert dash._agents["marcus"].progress_pct == 40
        assert "LLM" in dash._agents["marcus"].activity

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
        assert dash._agents["marcus"].progress_pct == 10

    def test_render_agent_panel(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent("marcus", state="WRITING", round_num=1, activity="Test", progress_pct=50)
        panel = dash._render_agent_panel(dash._agents["marcus"])
        assert "Marcus" in str(panel.title)
        assert "WRITING" in panel.renderable
        assert "50%" in panel.renderable

    def test_render_header_and_footer(self) -> None:
        dash = CouncilDashboard(["marcus", "elena"], max_rounds=3)
        dash.set_round(1)
        header = dash._render_header()
        footer = dash._render_footer()
        assert "Council" in str(header.renderable)
        assert "Runda 1/3" in str(header.renderable)
        assert "Gotowi" in str(footer.renderable)

    def test_render_logs(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash._add_log("Test event")
        panel = dash._render_logs()
        assert "Test event" in panel.renderable

    def test_render_preview(self) -> None:
        dash = CouncilDashboard(["marcus"])
        dash.update_agent("marcus", content="Hello world")
        panel = dash._render_preview()
        assert "Hello world" in panel.renderable
        assert "Marcus" in panel.renderable
