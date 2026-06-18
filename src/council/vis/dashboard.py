"""Real-time terminal dashboard for the AI Marketing Council.

Uses **Textual** (a reactive TUI framework) for 60 fps, CSS transitions,
and a native Markdown widget — inspired by the design of ``glow``.

Key improvements over the old rich-based dashboard:
- CSS transitions (border colours fade smoothly between states)
- Reactive updates (no manual refresh calls)
- Native ``Markdown`` widget for live content preview
- ``ProgressBar`` widget with smooth animation
- ``RichLog`` for syntax-highlighted logs
- Runs synchronously in the main thread (Textual requirement)
"""

from __future__ import annotations

import html
import json
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from rich.panel import Panel
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Footer,
    Header,
    Markdown,
    OptionList,
    ProgressBar,
    RichLog,
    Rule,
    Static,
)
from textual.widgets.option_list import Option

from council.artifacts import Artifact, discover_artifacts
from council.vis.agent_meta import AGENT_META
from council.vis.artifact_browser import ARTIFACT_LABELS

_AGENT_LABEL = "[AGENT]"


def _artifact_marker(artifact: Artifact) -> str:
    if artifact.kind == "discussion" and artifact.round_num is not None:
        return f"[ROUND {artifact.round_num}]"
    return ARTIFACT_LABELS[artifact.kind]


@dataclass
class AgentStats:
    """Performance statistics for a single agent run."""

    start_time: float | None = None
    end_time: float | None = None
    tokens_prompt: int = 0
    tokens_completion: int = 0
    cost_usd: float = 0.0

    @property
    def duration_ms(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0


@dataclass
class AgentView:
    """Snapshot of a single agent's current state for the dashboard."""

    name: str
    display_name: str
    avatar: str = _AGENT_LABEL
    state: str = "PENDING"
    round_num: int = 0
    activity: str = "Czeka..."
    color: str = "white"
    progress_pct: int = 0
    last_content: str = ""
    stats: AgentStats = field(default_factory=AgentStats)
    updated_at: float = field(default_factory=time.time)


@dataclass
class TimelineEvent:
    """Single event on the timeline."""

    timestamp: float
    agent_name: str
    event_type: str
    round_num: int


class AgentCard(Static):
    """A single agent panel with reactive state, progress and activity."""

    DEFAULT_CSS = """
    AgentCard {
        width: 100%;
        height: 100%;
        min-width: 22;
        border: solid $surface-darken-1;
        padding: 1 2;
        transition: border 300ms in_out_cubic, background 300ms in_out_cubic, tint 300ms in_out_cubic;
    }
    AgentCard.writing {
        border: solid #f39c12;
        background: #f39c12 8%;
        tint: #f39c12 10%;
    }
    AgentCard.done {
        border: solid #2ecc71;
        background: #2ecc71 8%;
        tint: #2ecc71 10%;
    }
    AgentCard.error {
        border: solid #e74c3c;
        background: #e74c3c 8%;
        tint: #e74c3c 10%;
    }
    AgentCard.pending {
        border: solid $surface-lighten-1;
        background: $surface-darken-1 50%;
    }
    AgentCard.waiting {
        border: solid #3498db;
        background: #3498db 8%;
        tint: #3498db 10%;
    }
    AgentCard .agent-name {
        text-style: bold;
        width: 100%;
        content-align: center middle;
        height: auto;
        color: $text;
    }
    AgentCard .agent-status {
        width: 100%;
        content-align: center middle;
        height: auto;
        margin: 1 0;
        text-style: bold;
    }
    AgentCard .agent-progress {
        width: 100%;
        margin: 1 0;
    }
    AgentCard .agent-activity {
        width: 100%;
        content-align: center middle;
        height: auto;
        color: $text-muted;
        text-style: italic;
    }
    """

    agent_name: str = ""
    agent_avatar: str = _AGENT_LABEL
    agent_color: str = "white"
    state: str = reactive("PENDING")
    progress: int = reactive(0)
    activity: str = reactive("Waiting...")

    def __init__(
        self,
        name: str,
        avatar: str = _AGENT_LABEL,
        color: str = "white",
        **kwargs,
    ) -> None:
        self.agent_name = name
        self.agent_avatar = avatar
        self.agent_color = color
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Static(
            f"{self.agent_avatar} {self.agent_name}",
            classes="agent-name",
        )
        yield Static("[PENDING] PENDING", classes="agent-status")
        yield ProgressBar(total=100, show_eta=False, classes="agent-progress")
        yield Static("Waiting for assignment...", classes="agent-activity")

    def watch_state(self, new_state: str) -> None:
        self.remove_class("pending", "writing", "done", "error", "waiting")
        self.add_class(new_state.lower())
        marker = {
            "pending": "[PENDING]",
            "writing": "[WRITING]",
            "done": "[DONE]",
            "error": "[ERROR]",
            "waiting": "[WAITING]",
        }.get(new_state.lower(), "[STATE]")
        status = self.query_one(".agent-status", Static)
        status.update(f"{marker} {new_state}")
        status.styles.color = self.agent_color

    def watch_progress(self, value: int) -> None:
        bar = self.query_one(ProgressBar)
        bar.update(progress=max(0, min(100, value)))

    def watch_activity(self, text: str) -> None:
        self.query_one(".agent-activity", Static).update(text)


class CouncilApp(App):
    """Textual TUI for the Marketing Council — glow-inspired design."""

    CSS = """
    Screen { align: center middle; }

    #main-grid {
        grid-size: 2;
        grid-columns: 3fr 1fr;
        grid-rows: 1fr;
        width: 100%;
        height: 100%;
        grid-gutter: 1;
    }

    #agents-grid {
        grid-size: 2 2;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr 1fr;
        grid-gutter: 1;
        width: 100%;
        height: 100%;
    }

    #sidebar {
        width: 100%;
        height: 100%;
        min-width: 26;
        border: solid $primary-darken-2;
        padding: 0 1;
        background: $surface-darken-1 30%;
        overflow-y: auto;
    }

    #sidebar .sidebar-title {
        text-style: bold underline;
        width: 100%;
        height: auto;
        padding: 1 0;
        color: $text;
        content-align: left middle;
    }

    #preview {
        height: 30%;
        border: solid $surface-lighten-1;
        padding: 1;
        background: $surface-darken-1 20%;
        overflow-y: auto;
    }

    #file-list {
        height: 18%;
        border: solid $surface-lighten-1;
        background: $surface-darken-1 20%;
        padding: 0 1;
    }

    #file-list:focus {
        border: solid $primary;
    }

    #logs {
        height: 22%;
        border: solid $surface-lighten-1;
        background: $surface-darken-1 20%;
        overflow-y: auto;
    }

    #stats {
        height: 15%;
        border: solid $surface-lighten-1;
        padding: 1;
        background: $surface-darken-1 20%;
        overflow-y: auto;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "toggle_logs", "Toggle logs"),
    ]

    def __init__(
        self,
        agent_names: list[str],
        max_rounds: int = 3,
        workspace: Path = Path("./output"),
        on_mounted: Callable[[], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._agent_names = agent_names
        self._max_rounds = max_rounds
        self.workspace = workspace
        self._on_mounted = on_mounted
        self._agent_cards: dict[str, AgentCard] = {}
        self._current_round = 0
        self._start_time = time.time()
        self._logs: deque[str] = deque(maxlen=200)
        self._timeline: deque[TimelineEvent] = deque(maxlen=100)
        self._agents_data: dict[str, AgentView] = {}
        self._mounted = False

        for name in agent_names:
            meta = AGENT_META.get(name, {"color": "white"})
            self._agents_data[name] = AgentView(
                name=name,
                display_name=name,
                color=meta["color"],
                avatar=_AGENT_LABEL,
            )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Grid(id="main-grid"):
            with Grid(id="agents-grid"):
                for name in self._agent_names:
                    agent = self._agents_data[name]
                    card = AgentCard(
                        name=agent.display_name,
                        avatar=agent.avatar,
                        color=agent.color,
                    )
                    self._agent_cards[name] = card
                    yield card
            with Vertical(id="sidebar"):
                yield Static("Content Preview", classes="sidebar-title")
                yield Markdown(
                    "*Council starting — waiting for agent output...*",
                    id="preview",
                )
                yield Rule()
                yield Static("Files", classes="sidebar-title")
                yield OptionList(id="file-list")
                yield Rule()
                yield Static("Event Log", classes="sidebar-title")
                yield RichLog(id="logs", max_lines=200, highlight=True)
                yield Rule()
                yield Static("Stats", classes="sidebar-title")
                yield Static(id="stats")
        yield Footer()

    def on_mount(self) -> None:
        self._mounted = True
        self.title = "Universal AI Marketing Council"
        self.sub_title = f"Starting... | 0/{self._max_rounds} rounds"
        for name in self._agent_names:
            card = self._agent_cards.get(name)
            if card:
                card.state = "PENDING"
                card.progress = 5
                card.activity = "Initializing council..."
        self._add_log("Dashboard ready - waiting for council thread...")
        self.set_interval(0.5, self._tick_header)
        self.set_interval(2.0, self._refresh_files)
        self._refresh_files()
        if self._on_mounted is not None:
            self._on_mounted()

    def _tick_header(self) -> None:
        elapsed = time.time() - self._start_time
        if self._current_round <= 0:
            self.sub_title = f"Starting... | {elapsed:.0f}s"
        else:
            self.sub_title = f"Round {self._current_round}/{self._max_rounds} | {elapsed:.0f}s"

    def update_agent(
        self,
        name: str,
        state: str | None = None,
        round_num: int | None = None,
        activity: str | None = None,
        progress_pct: int | None = None,
        content: str | None = None,
    ) -> None:
        if name not in self._agents_data:
            return
        agent = self._agents_data[name]
        old_state = agent.state

        if state is not None:
            agent.state = state
        if round_num is not None:
            agent.round_num = round_num
        if activity is not None:
            agent.activity = activity
        if progress_pct is not None:
            agent.progress_pct = max(0, min(100, progress_pct))
        if content is not None:
            agent.last_content = content
        agent.updated_at = time.time()

        card = self._agent_cards.get(name)
        if card:
            if state is not None:
                card.state = state
            if progress_pct is not None:
                card.progress = progress_pct
            if activity is not None:
                card.activity = activity

        if content is not None:
            preview = self.query_one("#preview", Markdown)
            latest = agent.last_content
            truncated = latest[:5000]
            if len(latest) > 5000:
                truncated += "\n\n*... [truncated]*"
            preview.update(truncated)

        if state == "WRITING" and agent.stats.start_time is None:
            agent.stats.start_time = time.time()
        if state in ("DONE", "ERROR") and agent.stats.end_time is None:
            agent.stats.end_time = time.time()

        if state is not None:
            self._add_log(state, agent_name=name)
            self._add_timeline(name, state, agent.round_num)

        if state == "DONE":
            self._refresh_files()

        self._refresh_stats()

    def update_agent_stats(
        self,
        name: str,
        tokens_prompt: int | None = None,
        tokens_completion: int | None = None,
        cost_usd: float | None = None,
    ) -> None:
        if name not in self._agents_data:
            return
        stats = self._agents_data[name].stats
        if tokens_prompt is not None:
            stats.tokens_prompt = tokens_prompt
        if tokens_completion is not None:
            stats.tokens_completion = tokens_completion
        if cost_usd is not None:
            stats.cost_usd = cost_usd
        self._refresh_stats()

    def set_round(self, round_num: int) -> None:
        self._current_round = round_num
        self.sub_title = f"Round {self._current_round}/{self._max_rounds}"
        self._add_log(f"=== Round {round_num} ===")

    def _add_log(self, message: str, agent_name: str | None = None) -> None:
        ts = time.strftime("%H:%M:%S")
        if agent_name and agent_name in self._agents_data:
            display = self._agents_data[agent_name].display_name
            self._logs.append(f"[{ts}] {display}: {message}")
        else:
            self._logs.append(f"[{ts}] {message}")
        log_widget = self.query_one("#logs", RichLog)
        log_widget.write(self._logs[-1])

    def _add_timeline(self, agent_name: str, event_type: str, round_num: int) -> None:
        self._timeline.append(
            TimelineEvent(
                timestamp=time.time(),
                agent_name=agent_name,
                event_type=event_type,
                round_num=round_num,
            )
        )

    def _refresh_stats(self) -> None:
        lines: list[str] = []
        for name in self._agent_names:
            a = self._agents_data[name]
            stats = a.stats
            duration = stats.duration_ms
            dur_str = f"{duration:.0f} ms" if duration else "-"
            tokens = stats.tokens_prompt + stats.tokens_completion
            cost = f"${stats.cost_usd:.4f}" if stats.cost_usd else "$0.0000"
            lines.append(
                f"{a.avatar} {a.display_name:8} | "
                f"{dur_str:>10} | "
                f"{tokens:>5} tok | "
                f"{cost}"
            )

        max_dur = max((a.stats.duration_ms for a in self._agents_data.values()), default=1)
        if max_dur > 0:
            lines.append("")
            for name in self._agent_names:
                a = self._agents_data[name]
                dur = a.stats.duration_ms
                bar_len = int(12 * dur / max_dur) if max_dur else 0
                bar = "#" * bar_len + "-" * (12 - bar_len)
                lines.append(f"{bar} {a.avatar} {a.display_name}")

        stats_widget = self.query_one("#stats", Static)
        stats_widget.update("\n".join(lines))

    def _refresh_files(self) -> None:
        try:
            file_list = self.query_one("#file-list", OptionList)
        except Exception:
            return
        file_list.clear_options()
        artifacts = [artifact for artifact in discover_artifacts(self.workspace) if artifact.exists]
        for artifact in artifacts:
            path = artifact.path
            file_list.add_option(
                Option(f"{_artifact_marker(artifact)} {artifact.relative_path}", id=str(path))
            )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option_id = getattr(event, "option_id", None)
        if option_id:
            path = Path(option_id)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                preview = self.query_one("#preview", Markdown)
                truncated = content[:4000]
                if len(content) > 4000:
                    truncated += "\n\n*... (truncated)*"
                preview.update(truncated)

    def action_toggle_logs(self) -> None:
        logs = self.query_one("#logs", RichLog)
        logs.toggle_class("hidden")


class CouncilDashboard:
    """Wrapper that exposes the same API as the old rich-based dashboard.

    Internally manages a Textual ``CouncilApp``.  Because Textual must run
    in the main thread, :meth:`run` blocks.  The caller should start the
    council work in a background thread and call :meth:`stop` when done.
    """

    def __init__(
        self,
        agent_names: list[str],
        max_rounds: int = 3,
        refresh_per_second: int = 4,  # kept for API compat, ignored
        workspace: Path = Path("./output"),
    ) -> None:
        self.agent_names = agent_names
        self.max_rounds = max_rounds
        self.workspace = workspace
        self._app: CouncilApp | None = None
        # Back-compat: internal data structures available even before run()
        self._agents: dict[str, AgentView] = {}
        self._logs: deque[str] = deque(maxlen=200)
        self._timeline: deque[TimelineEvent] = deque(maxlen=100)
        self._current_round = 0
        self._pending_logs: list[str] = []
        self._ready_callback: Callable[[], None] | None = None
        _META = {
            "marcus": ("cyan", _AGENT_LABEL),
            "elena": ("magenta", _AGENT_LABEL),
            "kai": ("green", _AGENT_LABEL),
            "david": ("yellow", _AGENT_LABEL),
        }
        for name in agent_names:
            color, avatar = _META.get(name.lower(), ("white", _AGENT_LABEL))
            self._agents[name] = AgentView(
                name=name,
                display_name=name.capitalize(),
                color=color,
                avatar=avatar,
            )

    # ── Blocking run / stop ────────────────────────────────────────────────

    def run(self, on_ready: Callable[[], None] | None = None) -> None:
        """Block and run the Textual app in the main thread."""
        self._ready_callback = on_ready
        self._app = CouncilApp(
            agent_names=self.agent_names,
            max_rounds=self.max_rounds,
            workspace=self.workspace,
            on_mounted=self._on_app_mounted,
        )
        self._app.run(mouse=True, inline=False)

    def _on_app_mounted(self) -> None:
        """Flush pre-mount logs and release the council worker thread."""
        self._flush_pending_logs()
        if self._ready_callback is not None:
            self._ready_callback()

    def _flush_pending_logs(self) -> None:
        if self._app is None or not self._app._mounted:
            return
        for message in self._pending_logs:
            self._app.call_from_thread(self._app._add_log, message)
        self._pending_logs.clear()

    def stop(self) -> None:
        """Signal the Textual app to exit."""
        if self._app is not None and self._app._mounted and self._app.is_running:
            self._app.exit()

    # ── Public API (same as before) ────────────────────────────────────────

    def update_agent(
        self,
        name: str,
        state: str | None = None,
        round_num: int | None = None,
        activity: str | None = None,
        progress_pct: int | None = None,
        content: str | None = None,
    ) -> None:
        if name in self._agents:
            agent = self._agents[name]
            if state is not None:
                agent.state = state
            if round_num is not None:
                agent.round_num = round_num
            if activity is not None:
                agent.activity = activity
            if progress_pct is not None:
                agent.progress_pct = max(0, min(100, progress_pct))
            if content is not None:
                agent.last_content = content
            agent.updated_at = time.time()
            if state == "WRITING" and agent.stats.start_time is None:
                agent.stats.start_time = time.time()
            if state in ("DONE", "ERROR") and agent.stats.end_time is None:
                agent.stats.end_time = time.time()
            if state is not None:
                ts = time.strftime("%H:%M:%S")
                self._logs.append(
                    f"[{ts}] [{agent.color}]{agent.display_name}[/{agent.color}]: {state}"
                )
                self._timeline.append(
                    TimelineEvent(
                        timestamp=time.time(),
                        agent_name=name,
                        event_type=state,
                        round_num=agent.round_num,
                    )
                )
        if self._app is not None and self._app._mounted:
            self._app.call_from_thread(
                self._app.update_agent,
                name,
                state,
                round_num,
                activity,
                progress_pct,
                content,
            )

    def update_agent_stats(
        self,
        name: str,
        tokens_prompt: int | None = None,
        tokens_completion: int | None = None,
        cost_usd: float | None = None,
    ) -> None:
        if name in self._agents:
            stats = self._agents[name].stats
            if tokens_prompt is not None:
                stats.tokens_prompt = tokens_prompt
            if tokens_completion is not None:
                stats.tokens_completion = tokens_completion
            if cost_usd is not None:
                stats.cost_usd = cost_usd
        if self._app is not None and self._app._mounted:
            self._app.call_from_thread(
                self._app.update_agent_stats,
                name,
                tokens_prompt,
                tokens_completion,
                cost_usd,
            )

    def set_round(self, round_num: int) -> None:
        self._current_round = round_num
        ts = time.strftime("%H:%M:%S")
        self._logs.append(f"[{ts}] === Round {round_num} ===")
        if self._app is not None and self._app._mounted:
            self._app.call_from_thread(self._app.set_round, round_num)

    def log(self, message: str) -> None:
        ts = time.strftime("%H:%M:%S")
        self._logs.append(f"[{ts}] {message}")
        if self._app is not None and self._app._mounted:
            self._app.call_from_thread(self._app._add_log, message)
        else:
            self._pending_logs.append(message)

    def refresh_files(self) -> None:
        """Refresh the Textual Files panel from the worker thread."""
        if self._app is not None and self._app._mounted:
            self._app.call_from_thread(self._app._refresh_files)

    def make_callback(self) -> Callable[..., None]:
        def _cb(agent_name: str, event: str, **kwargs: object) -> None:
            if event == "round_start":
                rnd = kwargs.get("round_num", 0)
                self.set_round(int(rnd))
                self.update_agent(
                    agent_name,
                    state="WRITING",
                    round_num=int(rnd),
                    progress_pct=10,
                    activity="Starting round...",
                )
            elif event == "generating":
                self.log(f"{agent_name}: calling LLM...")
                self.update_agent(
                    agent_name,
                    state="WRITING",
                    activity="Calling LLM...",
                    progress_pct=40,
                )
            elif event == "writing":
                self.update_agent(
                    agent_name,
                    state="WRITING",
                    activity="Writing round...",
                    progress_pct=80,
                )
            elif event == "waiting":
                self.update_agent(
                    agent_name,
                    state="WAITING",
                    activity=str(kwargs.get("activity", "Waiting for peers...")),
                    progress_pct=95,
                )
            elif event == "done":
                content = kwargs.get("content", "")
                self.update_agent(
                    agent_name,
                    state="DONE",
                    activity="Complete",
                    progress_pct=100,
                    content=str(content),
                )
                tokens_prompt = kwargs.get("tokens_prompt")
                tokens_completion = kwargs.get("tokens_completion")
                cost_usd = kwargs.get("cost_usd")
                if any(v is not None for v in (tokens_prompt, tokens_completion, cost_usd)):
                    self.update_agent_stats(
                        agent_name,
                        tokens_prompt=(
                            int(tokens_prompt) if tokens_prompt is not None else None
                        ),
                        tokens_completion=(
                            int(tokens_completion) if tokens_completion is not None else None
                        ),
                        cost_usd=(float(cost_usd) if cost_usd is not None else None),
                    )
            elif event == "error":
                msg = kwargs.get("message", "Error")
                self.log(f"{agent_name}: ERROR - {msg}")
                self.update_agent(
                    agent_name,
                    state="ERROR",
                    activity=str(msg),
                    progress_pct=0,
                )

        return _cb

    def export_json(self, path: Path | None = None) -> str:
        data = {
            "round": self._current_round,
            "max_rounds": self.max_rounds,
            "elapsed_seconds": round(
                time.time() - (self._app._start_time if self._app else time.time()), 2
            ),
            "agents": {
                name: {
                    "state": a.state,
                    "round": a.round_num,
                    "progress_pct": a.progress_pct,
                    "duration_ms": round(a.stats.duration_ms, 2),
                    "tokens": a.stats.tokens_prompt + a.stats.tokens_completion,
                    "cost_usd": round(a.stats.cost_usd, 6),
                }
                for name, a in self._agents.items()
            },
            "logs": list(self._logs),
            "timeline": [
                {
                    "time": time.strftime("%H:%M:%S", time.localtime(ev.timestamp)),
                    "agent": ev.agent_name,
                    "event": ev.event_type,
                    "round": ev.round_num,
                }
                for ev in self._timeline
            ],
        }
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if path:
            Path(path).write_text(json_str, encoding="utf-8")
        return json_str

    def export_html(self, path: Path | None = None) -> str:
        lines = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'>",
            "<title>Council Dashboard Export</title>",
            "<style>body{font-family:sans-serif;max-width:900px;margin:2em auto;}",
            ".agent{border:2px solid #ccc;padding:1em;margin:1em 0;border-radius:8px;}",
            ".done{border-color:green;}.error{border-color:red;}.writing{border-color:orange;}",
            "pre{background:#f4f4f4;padding:1em;overflow:auto;}th,td{padding:0.5em;text-align:left;}</style></head><body>",
            "<h1>Council Run Report</h1>",
            f"<p><strong>Round:</strong> {self._current_round}/{self.max_rounds} | "
            f"<strong>Time:</strong> {round(time.time()-(self._app._start_time if self._app else time.time()),1)}s</p>",
            "<h2>Agents</h2>",
        ]
        for name, a in self._agents.items():
            cls = html.escape(a.state.lower())
            lines.append(f'<div class="agent {cls}">')
            lines.append(f"<h3>{a.avatar} {html.escape(a.display_name)} - {html.escape(a.state)}</h3>")
            lines.append(
                f"<p>Progress: {a.progress_pct}% | "
                f"Time: {a.stats.duration_ms:.0f}ms | "
                f"Cost: ${a.stats.cost_usd:.4f}</p>"
            )
            if a.last_content:
                lines.append(f"<pre>{html.escape(a.last_content[:500])}</pre>")
            lines.append("</div>")
        lines.append("<h2>Logs</h2><ul>")
        for log in self._logs:
            lines.append(f"<li>{html.escape(log)}</li>")
        lines.append("</ul></body></html>")
        html_output = "\n".join(lines)
        if path:
            Path(path).write_text(html_output, encoding="utf-8")
        return html_output

    # ── Back-compat rendering helpers (used by tests) ──────────────────────

    def _animate_dots(self, base_text: str) -> str:
        dots = ["...", "..", ".", "..."]
        idx = int(time.time() * 2) % len(dots)
        return base_text + dots[idx]

    def _render_agent_panel(self, agent: AgentView) -> Panel:
        marker = {
            "PENDING": "[PENDING]",
            "WRITING": "[WRITING]",
            "DONE": "[DONE]",
            "ERROR": "[ERROR]",
        }.get(
            agent.state, "[STATE]"
        )
        lines = Text()
        lines.append(f"{agent.avatar} {agent.display_name}\n", style=f"bold {agent.color}")
        lines.append(f"{marker} {agent.state}\n", style=f"bold {agent.color}")
        lines.append(f"Round: {agent.round_num}/{self.max_rounds}\n", style="dim")
        lines.append(f"Progress: {agent.progress_pct}%\n")
        lines.append("-" * 16 + "\n", style="dim")
        lines.append(agent.activity or "Waiting...")
        return Panel(lines, title=f"[bold {agent.color}]{agent.display_name}[/bold {agent.color}]")

    def _render_header(self) -> Panel:
        elapsed = time.time() - (self._app._start_time if self._app else time.time())
        title = Text(" Universal AI Marketing Council v3.3 ", style="bold white on blue")
        subtitle = Text(
            f" Runda {self._current_round}/{self.max_rounds} | Czas: {elapsed:.1f}s ", style="dim"
        )
        content = Text.assemble(title, "\n", subtitle)
        return Panel(content, style="blue")

    def _render_footer(self) -> Panel:
        done = sum(1 for a in self._agents.values() if a.state == "DONE")
        errors = sum(1 for a in self._agents.values() if a.state == "ERROR")
        writing = sum(1 for a in self._agents.values() if a.state == "WRITING")
        parts = [f"Gotowi: {done}/{len(self.agent_names)}"]
        if writing:
            parts.append(f"Piszą: {writing}")
        if errors:
            parts.append(f"Błędy: {errors}")
        status = " | ".join(parts)
        text = Text(f" {status} ", style="dim")
        if errors:
            text = Text(f" {status} ", style="bold red")
        return Panel(text, style="dim")

    def _render_timeline(self) -> Panel:
        if not self._timeline:
            return Panel(Text("Brak zdarzeń...", style="dim"))
        content = Text()
        _META = {
            "marcus": ("cyan", _AGENT_LABEL),
            "elena": ("magenta", _AGENT_LABEL),
            "kai": ("green", _AGENT_LABEL),
            "david": ("yellow", _AGENT_LABEL),
        }
        for ev in list(self._timeline)[-12:]:
            ts = time.strftime("%H:%M:%S", time.localtime(ev.timestamp))
            color, avatar = _META.get(ev.agent_name, ("white", _AGENT_LABEL))
            content.append(f"[{ts}] ", style="dim")
            content.append(f"{avatar} {ev.agent_name.capitalize()}: ", style=f"bold {color}")
            content.append(f"{ev.event_type} (r{ev.round_num})\n", style="white")
        return Panel(content, title="[bold]Timeline[/bold]", border_style="blue")

    def _render_stats(self) -> Panel:
        lines = Text()
        for name in self.agent_names:
            a = self._agents[name]
            duration = a.stats.duration_ms
            dur_str = f"{duration:.0f}ms" if duration else "-"
            tokens = a.stats.tokens_prompt + a.stats.tokens_completion
            cost = f"${a.stats.cost_usd:.4f}" if a.stats.cost_usd else "$0.0000"
            lines.append(f"{a.avatar} {a.display_name}\n", style=f"bold {a.color}")
            lines.append(f"  Czas: {dur_str}  Tok: {tokens}  Koszt: {cost}\n", style="dim")
        max_dur = max((a.stats.duration_ms for a in self._agents.values()), default=1)
        if max_dur > 0:
            lines.append("\n")
            for name in self.agent_names:
                a = self._agents[name]
                dur = a.stats.duration_ms
                bar_len = int(10 * dur / max_dur) if max_dur else 0
                bar = "#" * bar_len + "-" * (10 - bar_len)
                lines.append(f"{bar} {a.avatar}\n", style=a.color)
        return Panel(lines, title="[bold]Statystyki[/bold]", border_style="green")

    # ── Context manager (lightweight, no thread spawn) ─────────────────────

    def __enter__(self) -> CouncilDashboard:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.stop()
