from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from rich.align import Align
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
    updated_at: float = field(default_factory=time.time)


class CouncilDashboard:
    """Real-time terminal dashboard for the AI Marketing Council.

    Uses ``rich`` to render a split-pane layout with live-updating agent
    panels.  Designed to be invoked from CLI via ``--dashboard`` flag.

    Example::

        dashboard = CouncilDashboard(agent_names=["marcus", "elena", "kai", "david"])
        with dashboard:
            dashboard.update_agent("marcus", state="WRITING", round_num=1,
                                   activity="Generuje ofertę...")
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

    def _build_layout(self) -> Layout:
        """Construct the rich Layout with header, agent panes, and footer."""
        layout = Layout(name="root")
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )

        # Split body into equal columns — one per agent
        if len(self.agent_names) == 4:
            layout["body"].split_row(
                Layout(name="agent_0", ratio=1),
                Layout(name="agent_1", ratio=1),
                Layout(name="agent_2", ratio=1),
                Layout(name="agent_3", ratio=1),
            )
        else:
            # Fallback: generic split
            children = [Layout(name=f"agent_{i}", ratio=1) for i in range(len(self.agent_names))]
            layout["body"].split_row(*children)

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

    def _render_agent_panel(self, agent: AgentView) -> Panel:
        emoji = self._STATE_EMOJI.get(agent.state, "❓")
        color = agent.color

        lines = Text()
        lines.append(f"{emoji} {agent.state}\n", style=f"bold {color}")
        lines.append(f"Runda: {agent.round_num}/{self.max_rounds}\n", style="dim")
        lines.append("─" * 18 + "\n", style="dim")

        # Wrap activity text to fit narrow panel
        activity = agent.activity or "Czeka..."
        if len(activity) > 180:
            activity = activity[:177] + "..."
        lines.append(activity, style="white")

        return Panel(
            lines,
            title=f"[bold {color}]{agent.display_name}[/bold {color}]",
            border_style=color,
        )

    def _refresh(self) -> None:
        """Push latest agent state into the layout."""
        self._layout["header"].update(self._render_header())
        self._layout["footer"].update(self._render_footer())
        for i, name in enumerate(self.agent_names):
            agent_view = self._agents[name]
            self._layout[f"agent_{i}"].update(self._render_agent_panel(agent_view))

    # ── Public API ──────────────────────────────────────────────────────────

    def update_agent(
        self,
        name: str,
        state: Optional[str] = None,
        round_num: Optional[int] = None,
        activity: Optional[str] = None,
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
        agent.updated_at = time.time()
        if self._live:
            self._refresh()

    def set_round(self, round_num: int) -> None:
        """Announce that the council has moved to a new round."""
        self._current_round = round_num
        if self._live:
            self._refresh()

    def make_callback(self) -> Callable[..., None]:
        """Return a callback suitable for passing to *AsyncOrchestrator*.

        The callback signature is::

            callback(agent_name: str, event: str, **kwargs)

        where *event* is one of ``round_start``, ``generating``,
        ``writing``, ``done``, ``error``.
        """

        def _cb(agent_name: str, event: str, **kwargs: object) -> None:
            if event == "round_start":
                rnd = kwargs.get("round_num", 0)
                self.set_round(int(rnd))
                self.update_agent(agent_name, state="WRITING", round_num=int(rnd))
            elif event == "generating":
                self.update_agent(agent_name, state="WRITING", activity="Wywołanie LLM...")
            elif event == "writing":
                self.update_agent(agent_name, state="WRITING", activity="Zapisuje rundę...")
            elif event == "done":
                self.update_agent(agent_name, state="DONE", activity="Runda zakończona ✓")
            elif event == "error":
                msg = kwargs.get("message", "Błąd")
                self.update_agent(agent_name, state="ERROR", activity=str(msg))

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
