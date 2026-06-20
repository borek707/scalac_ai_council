"""Textual integration tests for CouncilApp (epic #111, phase B)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from textual.widgets import Markdown, OptionList

from council.demo import run_demo
from council.vis.dashboard import CouncilApp, CouncilDashboard


@pytest.mark.asyncio
class TestCouncilAppRunTest:
    """CouncilApp mounted via textual run_test()."""

    async def test_mount_shows_initial_state(self, tmp_path: Path) -> None:
        """#115: header Starting, cards Initializing, first log line."""
        app = CouncilApp(
            agent_names=["Marcus", "Elena", "Kai", "David"],
            max_rounds=3,
            workspace=tmp_path,
        )
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            assert "Starting" in app.sub_title
            marcus = app._agent_cards["Marcus"]
            assert "Initializing" in marcus.activity
            log_text = "\n".join(app._logs)
            assert "Dashboard ready" in log_text

    async def test_agent_state_transitions_update_widgets(self, tmp_path: Path) -> None:
        """#117: callback-driven WRITING → preview content."""
        app = CouncilApp(
            agent_names=["Marcus"],
            max_rounds=2,
            workspace=tmp_path,
        )
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            app.set_round(1)
            app.update_agent(
                "Marcus",
                state="WRITING",
                round_num=1,
                activity="Calling LLM...",
                progress_pct=40,
            )
            await pilot.pause()
            card = app._agent_cards["Marcus"]
            assert card.state == "WRITING"
            assert card.progress == 40
            assert "Round 1" in app.sub_title

            app.update_agent(
                "Marcus",
                state="DONE",
                activity="Complete",
                progress_pct=100,
                content="# Marcus offer\n\nHello council",
            )
            await pilot.pause()
            assert app._agents_data["Marcus"].last_content == "# Marcus offer\n\nHello council"

    async def test_file_select_updates_preview(self, tmp_path: Path) -> None:
        """#119: Files list click loads markdown into preview."""
        proposal_dir = tmp_path / "output"
        proposal_dir.mkdir(parents=True)
        proposal = proposal_dir / "proposal.md"
        proposal.write_text("# Proposal\n\nPreview text here.", encoding="utf-8")

        app = CouncilApp(
            agent_names=["Marcus"],
            max_rounds=1,
            workspace=tmp_path,
        )
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            app._refresh_files()
            await pilot.pause()
            file_list = app.query_one("#file-list", OptionList)
            assert file_list.option_count >= 1

            class _SelectEvent:
                option_id = str(proposal)

            preview = app.query_one("#preview", Markdown)
            captured: list[str] = []
            original_update = preview.update

            def capture_update(text: str) -> None:
                captured.append(text)
                return original_update(text)

            preview.update = capture_update  # type: ignore[method-assign]
            app.on_option_list_option_selected(_SelectEvent())
            await pilot.pause()
            assert any("Preview text here" in text for text in captured)

    async def test_file_list_uses_manifest_artifacts(self, tmp_path: Path) -> None:
        """Files panel should show artifacts recorded in manifest.json."""
        output_dir = tmp_path / "output"
        custom_dir = tmp_path / "custom-deliverables"
        output_dir.mkdir(parents=True)
        custom_dir.mkdir(parents=True)
        deliverable = custom_dir / "marcus_custom.md"
        deliverable.write_text("# Marcus custom\n\nManifest-only artifact.", encoding="utf-8")
        manifest = {
            "files": {
                "final_deliverables": {
                    "Marcus": str(deliverable),
                },
            },
        }
        (output_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        app = CouncilApp(
            agent_names=["Marcus"],
            max_rounds=1,
            workspace=tmp_path,
        )
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            app._refresh_files()
            await pilot.pause()
            file_list = app.query_one("#file-list", OptionList)
            option_ids = [
                file_list.get_option_at_index(index).id for index in range(file_list.option_count)
            ]
            assert str(deliverable.resolve()) in option_ids

    async def test_file_list_uses_ascii_artifact_labels(self, tmp_path: Path) -> None:
        """Files panel should use stable ASCII labels instead of emoji icons."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)
        proposal = output_dir / "proposal.md"
        proposal.write_text("# Proposal", encoding="utf-8")

        app = CouncilApp(
            agent_names=["Marcus"],
            max_rounds=1,
            workspace=tmp_path,
        )
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            app._refresh_files()
            await pilot.pause()
            file_list = app.query_one("#file-list", OptionList)
            label = str(file_list.get_option_at_index(0).prompt)
            assert "[PROPOSAL]" in label
            assert "📋" not in label


class TestCouncilDashboardFlush:
    """Phase A: pending log flush (#112)."""

    def test_flush_pending_logs_invokes_add_log(self) -> None:
        dash = CouncilDashboard(["Marcus"])
        dash.log("first")
        dash.log("second")
        assert len(dash._pending_logs) == 2

        dash._app = type("FakeApp", (), {})()  # minimal stub
        dash._app._mounted = True
        dash._app.call_from_thread = lambda fn, msg: fn(msg)

        captured: list[str] = []
        dash._app._add_log = captured.append  # type: ignore[attr-defined]

        dash._flush_pending_logs()
        assert dash._pending_logs == []
        assert captured == ["first", "second"]

    def test_on_app_mounted_fires_ready_callback(self) -> None:
        dash = CouncilDashboard(["Marcus"])
        events: list[str] = []

        def on_ready() -> None:
            events.append("ready")

        dash._ready_callback = on_ready
        dash._app = type("FakeApp", (), {})()
        dash._app._mounted = True
        dash._app.call_from_thread = lambda fn, msg: fn(msg)
        dash._app._add_log = lambda msg: None  # type: ignore[attr-defined]

        dash.log("buffered")
        dash._on_app_mounted()
        assert events == ["ready"]
        assert dash._pending_logs == []

    def test_refresh_files_invokes_app_refresh(self) -> None:
        dash = CouncilDashboard(["Marcus"])
        calls: list[str] = []

        dash._app = type("FakeApp", (), {})()
        dash._app._mounted = True
        dash._app.call_from_thread = lambda fn: fn()
        dash._app._refresh_files = lambda: calls.append("refresh")  # type: ignore[attr-defined]

        dash.refresh_files()

        assert calls == ["refresh"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestDemoDashboardIntegration:
    """Phase D: demo + dashboard callback path (#120)."""

    async def test_demo_callback_drives_all_agents_to_done(self, tmp_path: Path) -> None:
        dash = CouncilDashboard(
            ["Marcus", "Elena", "Kai", "David"],
            max_rounds=1,
            workspace=tmp_path,
        )
        await run_demo(
            scenario_key="saas-launch",
            rounds=1,
            workspace=tmp_path,
            progress_callback=dash.make_callback(),
            delay=0,
            breath=0,
        )
        for name in ("Marcus", "Elena", "Kai", "David"):
            assert dash._agents[name].state == "DONE"
        discussion = tmp_path / "shared" / "discussion"
        assert list(discussion.glob("*_round_*.md"))
