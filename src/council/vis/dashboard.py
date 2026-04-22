from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Optional

from rich.align import Align
from rich.bar import Bar
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


@dataclass
class AgentView:
    """Snapshot of a single agent's current state for the dashboard."""

    name: str
    display_name: str
    state: str = "PENDING"
    round_num: int = 0
    activity: str = "Czeka..."
    color: str = "white"
    progress_pct: int = 0
    last_content: str = ""
    updated_at: float = field(default_factory=time.time)


class CouncilDashboard:
    """Real-time terminal dashboard for the AI Marketing Council.

    Uses ``rich`` to render a split-pane layout with live-updating agent
    panels, a shared event log, and a content preview pane.

    Example::

        dashboard = CouncilDashboard(agent_names=["marcus", "elena", "kai", "david"])
        with dashboard:
            dashboard.update_agent("marcus", state="WRITING", round_num=1,
                                   activity="Generuje ofertę...", progress_pct=50)
            ...
    """

    _AGENT_COLORS: dict[str, str] = {
        "marcus": "cyan",
        "elena": "magenta",
        "kai": "green",
        "david": "yellow",
    }

    _STATE_EMOJI: dict[str, str] = {
        "PENDING": "⏳",
        "WRITING": "✍️ ",
        "WAITING": "🔄",
        "DONE": "✅",
        "ERROR": "❌",
    }

    def __init__(
        self,
        agent_names: list[str],
        max_rounds: int = 3,
        refresh_per_second: int = 4,
    ) -> None:
        self.agent_names = agent_names
        self.max_rounds = max_rounds
        self._agents: dict[str, AgentView] = {
            name: AgentView(
                name=name,
                display_name=name.capitalize(),
                color=self._AGENT_COLORS.get(name, "white"),
            )
            for name in agent_names
        }
        self._current_round: int = 0
        self._start_time: float = time.time()
        self._live: Optional[Live] = None
        self._layout = self._build_layout()
        self._logs: deque[str] = deque(maxlen=20)

    def _build_layout(self) -> Layout:
        """Construct the rich Layout with header, agents, log/preview, footer."""
        layout = Layout(name="root")
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        # Main area: left = agents grid, right = logs + preview
        layout["main"].split_row(
            Layout(name="agents", ratio=2),
            Layout(name="sidebar", ratio=1),
        )

        # Agents grid: 2 rows x 2 columns for 4 agents
        if len(self.agent_names) == 4:
            layout["agents"].split_column(
                Layout(name="agents_top"),
                Layout(name="agents_bottom"),
            )
            layout["agents_top"].split_row(
                Layout(name="agent_0"),
                Layout(name="agent_1"),
            )
            layout["agents_bottom"].split_row(
                Layout(name="agent_2"),
                Layout(name="agent_3"),
            )
        else:
            children = [Layout(name=f"agent_{i}", ratio=1) for i in range(len(self.agent_names))]
            layout["agents"].split_row(*children)

        # Sidebar: logs on top, preview on bottom
        layout["sidebar"].split_column(
            Layout(name="logs", ratio=1),
            Layout(name="preview", ratio=1),
        )

        return layout

    def _render_header(self) -> Panel:
        elapsed = time.time() - self._start_time
        title = Text(" Universal AI Marketing Council v3.1 ", style="bold white on blue")
        subtitle = Text(
            f" Runda {self._current_round}/{self.max_rounds} | "
            f"Czas: {elapsed:.1f}s ",
            style="dim",
        )
        content = Text.assemble(title, "\n", subtitle)
        return Panel(Align.center(content), style="blue", height=3)

    def _render_footer(self) -> Panel:
        done = sum(1 for a in self._agents.values() if a.state == "DONE")
        errors = sum(1 for a in self._agents.values() if a.state == "ERROR")
        status = f" Gotowi: {done}/{len(self.agent_names)} | Błędy: {errors} "
        text = Text(status, style="dim")
        if errors:
            text = Text(status, style="bold red")
        return Panel(Align.center(text), style="dim", height=3)

    def _render_progress(self, pct: int, color: str) -> Text:
        """Render a compact ASCII progress bar."""
        width = 14
        filled = int(width * pct / 100)
        bar = "█" * filled + "░" * (width - filled)
        return Text(f"{bar} {pct}%", style=f"bold {color}")

    def _render_agent_panel(self, agent: AgentView) -> Panel:
        emoji = self._STATE_EMOJI.get(agent.state, "❓")
        color = agent.color

        lines = Text()
        lines.append(f"{emoji} {agent.state}\n", style=f"bold {color}")
        lines.append(f"Runda: {agent.round_num}/{self.max_rounds}\n", style="dim")
        lines.append(self._render_progress(agent.progress_pct, color))
        lines.append("\n")
        lines.append("─" * 18 + "\n", style="dim")

        activity = agent.activity or "Czeka..."
        if len(activity) > 120:
            activity = activity[:117] + "..."
        lines.append(activity, style="white")

        return Panel(
            lines,
            title=f"[bold {color}]{agent.display_name}[/bold {color}]",
            border_style=color,
        )

    def _render_logs(self) -> Panel:
        if not self._logs:
            content = Text("Brak zdarzeń...", style="dim")
        else:
            content = Text()
            for line in self._logs:
                content.append(line + "\n", style="dim")
        return Panel(content, title="[bold]📋 Logi[/bold]", border_style="white")

    def _render_preview(self) -> Panel:
        # Show the most recently updated agent's content
        latest_agent = max(
            self._agents.values(),
            key=lambda a: a.updated_at,
            default=None,
        )
        if latest_agent and latest_agent.last_content:
            preview = latest_agent.last_content[:600]
            if len(latest_agent.last_content) > 600:
                preview += "\n..."
            header = Text(f"📝 {latest_agent.display_name}\n", style=f"bold {latest_agent.color}")
            body = Text(preview, style="white")
            content = Text.assemble(header, body)
        else:
            content = Text("Poczekaj na pierwszy output...", style="dim")
        return Panel(content, title="[bold]👁 Podgląd[/bold]", border_style="white")

    def _refresh(self) -> None:
        """Push latest agent state into the layout."""
        self._layout["header"].update(self._render_header())
        self._layout["footer"].update(self._render_footer())
        self._layout["logs"].update(self._render_logs())
        self._layout["preview"].update(self._render_preview())

        for i, name in enumerate(self.agent_names):
            agent_view = self._agents[name]
            self._layout[f"agent_{i}"].update(self._render_agent_panel(agent_view))

    def _add_log(self, message: str) -> None:
        ts = time.strftime("%H:%M:%S")
        self._logs.append(f"[{ts}] {message}")

    # ── Public API ──────────────────────────────────────────────────────────

    def update_agent(
        self,
        name: str,
        state: Optional[str] = None,
        round_num: Optional[int] = None,
        activity: Optional[str] = None,
        progress_pct: Optional[int] = None,
        content: Optional[str] = None,
    ) -> None:
        """Update the visual state of a single agent."""
        if name not in self._agents:
            return
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

        # Log significant state changes
        if state is not None:
            self._add_log(f"{agent.display_name}: {state}")
        if self._live:
            self._refresh()

    def set_round(self, round_num: int) -> None:
        """Announce that the council has moved to a new round."""
        self._current_round = round_num
        self._add_log(f"=== Runda {round_num} ===")
        if self._live:
            self._refresh()

    def make_callback(self) -> Callable[..., None]:
        """Return a callback suitable for passing to *AsyncOrchestrator*.

        The callback signature is flexible::

            callback(agent_name: str, event: str, **kwargs)

        where *event* is one of ``round_start``, ``generating``,
        ``writing``, ``done``, ``error``.
        """

        def _cb(agent_name: str, event: str, **kwargs: object) -> None:
            if event == "round_start":
                rnd = kwargs.get("round_num", 0)
                self.set_round(int(rnd))
                self.update_agent(agent_name, state="WRITING", round_num=int(rnd), progress_pct=10)
            elif event == "generating":
                self.update_agent(agent_name, state="WRITING", activity="Wywołanie LLM...", progress_pct=40)
            elif event == "writing":
                self.update_agent(agent_name, state="WRITING", activity="Zapisuje rundę...", progress_pct=80)
            elif event == "done":
                content = kwargs.get("content", "")
                self.update_agent(agent_name, state="DONE", activity="Runda zakończona ✓", progress_pct=100, content=str(content))
            elif event == "error":
                msg = kwargs.get("message", "Błąd")
                self.update_agent(agent_name, state="ERROR", activity=str(msg), progress_pct=0)

        return _cb

    # ── Context manager ─────────────────────────────────────────────────────

    def __enter__(self) -> "CouncilDashboard":
        self._start_time = time.time()
        self._refresh()
        self._live = Live(
            self._layout,
            refresh_per_second=4,
            screen=False,
            transient=False,
        )
        self._live.__enter__()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if self._live:
            self._live.__exit__(exc_type, exc_val, exc_tb)
            self._live = None
