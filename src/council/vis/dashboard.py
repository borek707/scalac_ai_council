from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from rich.align import Align
from rich.bar import Bar
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


@dataclass
class AgentStats:
    """Performance statistics for a single agent run."""

    start_time: Optional[float] = None
    end_time: Optional[float] = None
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
    avatar: str = "🤖"
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
    """Single event on the mini-timeline."""

    timestamp: float
    agent_name: str
    event_type: str
    round_num: int


class CouncilDashboard:
    """Real-time terminal dashboard for the AI Marketing Council.

    Uses ``rich`` to render a split-pane layout with live-updating agent
    panels, a shared event log, content preview, mini-timeline, and
    per-agent performance statistics.

    Example::

        dashboard = CouncilDashboard(agent_names=["marcus", "elena", "kai", "david"])
        with dashboard:
            dashboard.update_agent("marcus", state="WRITING", round_num=1,
                                   activity="Generuje ofertę...", progress_pct=50)
            ...
    """

    _AGENT_META: dict[str, tuple[str, str]] = {
        "marcus": ("cyan", "🏗️"),
        "elena": ("magenta", "🎯"),
        "kai": ("green", "✍️"),
        "david": ("yellow", "🎣"),
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
        self._agents: dict[str, AgentView] = {}
        for name in agent_names:
            color, avatar = self._AGENT_META.get(name, ("white", "🤖"))
            self._agents[name] = AgentView(
                name=name,
                display_name=name.capitalize(),
                color=color,
                avatar=avatar,
            )
        self._current_round: int = 0
        self._start_time: float = time.time()
        self._live: Optional[Live] = None
        self._layout = self._build_layout()
        self._logs: deque[str] = deque(maxlen=30)
        self._timeline: deque[TimelineEvent] = deque(maxlen=50)
        self._alert_flash: bool = False
        self._alert_until: float = 0.0
        self._animation_frame: int = 0
        self._last_anim_tick: float = 0.0

    def _build_layout(self) -> Layout:
        """Construct the rich Layout with header, agents, log/preview, footer."""
        layout = Layout(name="root")
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1),
        )

        # Left: agents grid (top) + stats/timeline (bottom)
        layout["left"].split_column(
            Layout(name="agents"),
            Layout(name="bottom_left", size=8),
        )

        # Agents grid: 2x2
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

        # Bottom left: timeline + stats side by side
        layout["bottom_left"].split_row(
            Layout(name="timeline", ratio=1),
            Layout(name="stats", ratio=1),
        )

        # Right sidebar: logs + preview
        layout["right"].split_column(
            Layout(name="logs", ratio=1),
            Layout(name="preview", ratio=1),
        )

        return layout

    def _render_header(self) -> Panel:
        elapsed = time.time() - self._start_time
        title = Text(f" {self._get_avatar('council')} Universal AI Marketing Council v3.1 ", style="bold white on blue")
        subtitle = Text(
            f" Runda {self._current_round}/{self.max_rounds} | "
            f"Czas: {elapsed:.1f}s ",
            style="dim",
        )
        content = Text.assemble(title, "\n", subtitle)
        if self._alert_flash and time.time() < self._alert_until:
            return Panel(Align.center(content), style="bold red on black", height=3)
        return Panel(Align.center(content), style="blue", height=3)

    def _render_footer(self) -> Panel:
        done = sum(1 for a in self._agents.values() if a.state == "DONE")
        errors = sum(1 for a in self._agents.values() if a.state == "ERROR")
        writing = sum(1 for a in self._agents.values() if a.state == "WRITING")
        status_parts = [f"✅ Gotowi: {done}/{len(self.agent_names)}"]
        if writing:
            status_parts.append(f"✍️ Piszą: {writing}")
        if errors:
            status_parts.append(f"❌ Błędy: {errors}")
        status = " | ".join(status_parts)
        text = Text(f" {status} ", style="dim")
        if errors:
            text = Text(f" {status} ", style="bold red")
        return Panel(Align.center(text), style="dim", height=3)

    def _get_avatar(self, name: str) -> str:
        if name == "council":
            return "🏛️"
        return self._AGENT_META.get(name, ("", "🤖"))[1]

    def _render_progress(self, pct: int, color: str) -> Text:
        width = 12
        filled = int(width * pct / 100)
        bar = "█" * filled + "░" * (width - filled)
        return Text(f"{bar} {pct}%", style=f"bold {color}")

    def _animate_dots(self, base_text: str) -> str:
        """Cycle dots for WRITING state: ... → .. → . → ..."""
        dots = ["...", "..", ".", "..."]
        return base_text + dots[self._animation_frame % len(dots)]

    def _render_agent_panel(self, agent: AgentView) -> Panel:
        emoji = self._STATE_EMOJI.get(agent.state, "❓")
        color = agent.color
        avatar = agent.avatar

        lines = Text()
        lines.append(f"{avatar} {agent.display_name}\n", style=f"bold {color}")
        lines.append(f"{emoji} {agent.state}\n", style=f"bold {color}")
        lines.append(f"Runda: {agent.round_num}/{self.max_rounds}\n", style="dim")
        lines.append(self._render_progress(agent.progress_pct, color))
        lines.append("\n")
        lines.append("─" * 16 + "\n", style="dim")

        activity = agent.activity or "Czeka..."
        if agent.state == "WRITING":
            activity = self._animate_dots(activity)
        if len(activity) > 100:
            activity = activity[:97] + "..."
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
                content.append(line + "\n")
        return Panel(content, title="[bold]📋 Logi[/bold]", border_style="white")

    def _render_preview(self) -> Panel:
        latest_agent = max(
            self._agents.values(),
            key=lambda a: a.updated_at,
            default=None,
        )
        if latest_agent and latest_agent.last_content:
            preview = latest_agent.last_content[:800]
            if len(latest_agent.last_content) > 800:
                preview += "\n\n..."
            md = Markdown(preview)
            header = Text(f"{latest_agent.avatar} {latest_agent.display_name}\n", style=f"bold {latest_agent.color}")
            return Panel(md, title=f"[bold {latest_agent.color}]👁 Podgląd[/bold {latest_agent.color}]", border_style=latest_agent.color)
        else:
            content = Text("Poczekaj na pierwszy output...", style="dim")
            return Panel(content, title="[bold]👁 Podgląd[/bold]", border_style="white")

    def _render_timeline(self) -> Panel:
        if not self._timeline:
            content = Text("Brak zdarzeń...", style="dim")
        else:
            content = Text()
            for ev in list(self._timeline)[-12:]:
                ts = time.strftime("%H:%M:%S", time.localtime(ev.timestamp))
                _, avatar = self._AGENT_META.get(ev.agent_name, ("white", "🤖"))
                color = self._AGENT_META.get(ev.agent_name, ("white", ""))[0]
                content.append(f"[{ts}] ", style="dim")
                content.append(f"{avatar} {ev.agent_name.capitalize()}: ", style=f"bold {color}")
                content.append(f"{ev.event_type} (r{ev.round_num})\n", style="white")
        return Panel(content, title="[bold]⏱ Timeline[/bold]", border_style="blue")

    def _render_stats(self) -> Panel:
        lines = Text()
        for name in self.agent_names:
            agent = self._agents[name]
            stats = agent.stats
            color = agent.color
            duration = stats.duration_ms
            duration_str = f"{duration:.0f}ms" if duration else "—"
            tokens = stats.tokens_prompt + stats.tokens_completion
            cost = f"${stats.cost_usd:.4f}" if stats.cost_usd else "$0.0000"

            lines.append(f"{agent.avatar} {agent.display_name}\n", style=f"bold {color}")
            lines.append(f"  Czas: {duration_str}  Tok: {tokens}  Koszt: {cost}\n", style="dim")

        # Mini bar chart
        lines.append("\n")
        max_dur = max((a.stats.duration_ms for a in self._agents.values()), default=1)
        if max_dur > 0:
            for name in self.agent_names:
                agent = self._agents[name]
                dur = agent.stats.duration_ms
                bar_len = int(10 * dur / max_dur) if max_dur else 0
                bar = "█" * bar_len + "░" * (10 - bar_len)
                lines.append(f"{bar} {agent.avatar}\n", style=agent.color)

        return Panel(lines, title="[bold]📊 Statystyki[/bold]", border_style="green")

    def _tick_animation(self) -> None:
        now = time.time()
        if now - self._last_anim_tick > 0.5:
            self._animation_frame += 1
            self._last_anim_tick = now

    def _refresh(self) -> None:
        self._tick_animation()
        self._layout["header"].update(self._render_header())
        self._layout["footer"].update(self._render_footer())
        self._layout["logs"].update(self._render_logs())
        self._layout["preview"].update(self._render_preview())
        self._layout["timeline"].update(self._render_timeline())
        self._layout["stats"].update(self._render_stats())

        for i, name in enumerate(self.agent_names):
            agent_view = self._agents[name]
            self._layout[f"agent_{i}"].update(self._render_agent_panel(agent_view))

    def _add_log(self, message: str, agent_name: Optional[str] = None) -> None:
        ts = time.strftime("%H:%M:%S")
        if agent_name and agent_name in self._agents:
            color = self._agents[agent_name].color
            display = self._agents[agent_name].display_name
            self._logs.append(f"[{ts}] [{color}]{display}[/{color}]: {message}")
        else:
            self._logs.append(f"[{ts}] {message}")

    def _add_timeline(self, agent_name: str, event_type: str, round_num: int) -> None:
        self._timeline.append(TimelineEvent(
            timestamp=time.time(),
            agent_name=agent_name,
            event_type=event_type,
            round_num=round_num,
        ))

    def _trigger_alert(self) -> None:
        self._alert_flash = True
        self._alert_until = time.time() + 2.0
        print("\a", end="")  # Terminal bell

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
        if name not in self._agents:
            return
        agent = self._agents[name]
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

        # Update stats
        if state == "WRITING" and agent.stats.start_time is None:
            agent.stats.start_time = time.time()
        if state in ("DONE", "ERROR") and agent.stats.end_time is None:
            agent.stats.end_time = time.time()

        if state is not None:
            self._add_log(state, agent_name=name)
            self._add_timeline(name, state, agent.round_num)
        if state == "ERROR":
            self._trigger_alert()
        if self._live:
            self._refresh()

    def update_agent_stats(
        self,
        name: str,
        tokens_prompt: Optional[int] = None,
        tokens_completion: Optional[int] = None,
        cost_usd: Optional[float] = None,
    ) -> None:
        if name not in self._agents:
            return
        stats = self._agents[name].stats
        if tokens_prompt is not None:
            stats.tokens_prompt = tokens_prompt
        if tokens_completion is not None:
            stats.tokens_completion = tokens_completion
        if cost_usd is not None:
            stats.cost_usd = cost_usd
        if self._live:
            self._refresh()

    def set_round(self, round_num: int) -> None:
        self._current_round = round_num
        self._add_log(f"=== Runda {round_num} ===")
        if self._live:
            self._refresh()

    def make_callback(self) -> Callable[..., None]:
        def _cb(agent_name: str, event: str, **kwargs: object) -> None:
            if event == "round_start":
                rnd = kwargs.get("round_num", 0)
                self.set_round(int(rnd))
                self.update_agent(agent_name, state="WRITING", round_num=int(rnd), progress_pct=10)
            elif event == "generating":
                self.update_agent(agent_name, state="WRITING", activity="Wywołanie LLM", progress_pct=40)
            elif event == "writing":
                self.update_agent(agent_name, state="WRITING", activity="Zapisuje rundę", progress_pct=80)
            elif event == "done":
                content = kwargs.get("content", "")
                self.update_agent(agent_name, state="DONE", activity="Runda zakończona ✓", progress_pct=100, content=str(content))
            elif event == "error":
                msg = kwargs.get("message", "Błąd")
                self.update_agent(agent_name, state="ERROR", activity=str(msg), progress_pct=0)
        return _cb

    # ── Export ──────────────────────────────────────────────────────────────

    def export_json(self, path: Optional[Path] = None) -> str:
        data = {
            "round": self._current_round,
            "max_rounds": self.max_rounds,
            "elapsed_seconds": round(time.time() - self._start_time, 2),
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

    def export_html(self, path: Optional[Path] = None) -> str:
        lines = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'>",
            "<title>Council Dashboard Export</title>",
            "<style>body{font-family:sans-serif;max-width:900px;margin:2em auto;}",
            ".agent{border:2px solid #ccc;padding:1em;margin:1em 0;border-radius:8px;}",
            ".done{border-color:green;}.error{border-color:red;}.writing{border-color:orange;}",
            "pre{background:#f4f4f4;padding:1em;overflow:auto;}th,td{padding:0.5em;text-align:left;}</style></head><body>",
            f"<h1>🏛️ Council Run Report</h1>",
            f"<p><strong>Runda:</strong> {self._current_round}/{self.max_rounds} | <strong>Czas:</strong> {round(time.time()-self._start_time,1)}s</p>",
            "<h2>📊 Agenci</h2>",
        ]
        for name, a in self._agents.items():
            cls = a.state.lower()
            lines.append(f'<div class="agent {cls}">')
            lines.append(f"<h3>{a.avatar} {a.display_name} — {a.state}</h3>")
            lines.append(f"<p>Progress: {a.progress_pct}% | Czas: {a.stats.duration_ms:.0f}ms | Koszt: ${a.stats.cost_usd:.4f}</p>")
            if a.last_content:
                lines.append(f"<pre>{a.last_content[:500]}</pre>")
            lines.append("</div>")
        lines.append("<h2>📋 Logi</h2><ul>")
        for log in self._logs:
            lines.append(f"<li>{log}</li>")
        lines.append("</ul></body></html>")
        html = "\n".join(lines)
        if path:
            Path(path).write_text(html, encoding="utf-8")
        return html

    # ── Context manager ─────────────────────────────────────────────────────

    def __enter__(self) -> "CouncilDashboard":
        self._start_time = time.time()
        self._refresh()
        self._live = Live(
            self._layout,
            refresh_per_second=6,
            screen=False,
            transient=False,
        )
        self._live.__enter__()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if self._live:
            self._live.__exit__(exc_type, exc_val, exc_tb)
            self._live = None
