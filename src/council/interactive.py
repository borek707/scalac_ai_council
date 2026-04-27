"""Interactive TUI menu for the AI Marketing Council — Textual-based.

Provides a navigable multi-screen menu with:
- Arrow-key navigation (↑↓) + Enter to select
- Escape to go back
- Mouse click support
- Breadcrumb-style screen transitions
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Center, Grid, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    Input,
    Label,
    OptionList,
    Rule,
    Static,
    Switch,
)
from textual.widgets.option_list import Option

from council.demo import list_scenarios

_ONBOARDING_FLAG = Path.home() / ".config" / "council" / "onboarding_done"

_PROVIDERS = [
    ("openai", "OpenAI (GPT-4o)", "gpt-4o"),
    ("anthropic", "Anthropic (Claude)", "claude-sonnet-4-6"),
    ("openrouter", "OpenRouter (universal)", "anthropic/claude-sonnet-4"),
    ("ollama", "Ollama (local)", "llama3"),
    ("kimi-code", "Kimi Code CLI", "kimi-for-coding"),
    ("claude-code", "Claude Code CLI / IDE", "claude-sonnet-4-6"),
]


def _is_onboarding_done() -> bool:
    return _ONBOARDING_FLAG.exists()


def _mark_onboarding_done() -> None:
    _ONBOARDING_FLAG.parent.mkdir(parents=True, exist_ok=True)
    _ONBOARDING_FLAG.touch(exist_ok=True)


# ── Screens ─────────────────────────────────────────────────────────────────

class WelcomeScreen(Screen):
    """First-run onboarding screen."""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(classes="menu-container"):
                yield Static(
                    "\uf0e8  Universal AI Marketing Council",
                    classes="title",
                )
                yield Static("v3.2 — AI-powered marketing strategy", classes="subtitle")
                yield Rule()
                yield Static("[bold]The Four Agents[/bold]", classes="section-title")
                yield Static(
                    "\uf0ad  [cyan]Marcus[/cyan]  — Offer Architect\n"
                    "\uf140  [magenta]Elena[/magenta] — Funnel Architect\n"
                    "\uf040  [green]Kai[/green]   — Copywriter\n"
                    "\uf201  [yellow]David[/yellow] — Lead Strategist",
                    classes="agents-list",
                )
                yield Static(
                    "[dim]Each round they read, critique, and improve each other's work."
                    "\nAfter 2-3 rounds you get a polished multi-perspective plan.[/dim]",
                    classes="description",
                )
                yield Rule()
                with Horizontal(classes="button-row"):
                    yield Button("Skip →", variant="default", id="skip")
                    yield Button("Start →", variant="primary", id="start")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in ("start", "skip"):
            _mark_onboarding_done()
            self.app.push_screen("main")


class MainMenuScreen(Screen):
    """Primary navigation hub."""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(classes="menu-container"):
                yield Static("\uf0e8  Main Menu", classes="title")
                yield Static("Choose how to run the council", classes="subtitle")
                yield OptionList(
                    Option("\uf11b  Demo Mode — pre-built scenarios, no API keys", id="demo"),
                    Option("\uf115  Run from Template — built-in company configs", id="template"),
                    Option("\uf0c5  Real Council Run — your own config + LLM", id="real"),
                    Option("\uf108  IDE Help — VS Code, Cursor, Kimi, Claude", id="ide"),
                    Option("\uf128  How it Works — the debate explained", id="help"),
                    Option("\uf00d  Quit", id="quit"),
                )
                yield Static("[dim]↑↓ navigate · Enter select · q quit[/dim]", classes="hint")

    def on_mount(self) -> None:
        ol = self.query_one(OptionList)
        ol.highlighted = 0
        ol.focus()

    def on_option_list_option_selected(self, event) -> None:
        choice = event.option.id
        if choice == "demo":
            self.app.push_screen("demo")
        elif choice == "template":
            self.app.push_screen("template")
        elif choice == "real":
            self.app.push_screen("config")
        elif choice == "ide":
            self.app.push_screen("ide")
        elif choice == "help":
            self.app.push_screen("help")
        elif choice == "quit":
            self.app.push_screen("quit_confirm")


class DemoScreen(Screen):
    """Demo mode configuration."""

    def compose(self) -> ComposeResult:
        scenarios = list_scenarios()
        self.app.state["scenarios"] = scenarios
        with Center():
            with Vertical(classes="menu-container"):
                yield Static("\uf11b  Demo Mode", classes="title")
                yield Static("Pre-built scenarios — no API keys needed", classes="subtitle")
                yield OptionList(
                    *[
                        Option(f"{s.name} — {s.description}", id=s.key)
                        for s in scenarios
                    ],
                )
                yield Rule()
                yield Static("Rounds:", classes="field-label")
                yield Input(value="3", placeholder="3", id="rounds-input")
                yield Static("Dashboard:", classes="field-label")
                with Horizontal(classes="switch-row"):
                    yield Switch(value=True, id="dashboard-switch")
                    yield Label("Enable live terminal dashboard")
                yield Static("[dim]↑↓ navigate · Tab next field · Enter confirm · Esc back[/dim]", classes="hint")
                with Horizontal(classes="button-row"):
                    yield Button("← Back", variant="default", id="back")
                    yield Button("Next →", variant="primary", id="next")

    def _go_next(self) -> None:
        ol = self.query_one(OptionList)
        sel = ol.highlighted
        scenarios = self.app.state.get("scenarios", [])
        scenario = scenarios[sel].key if scenarios and sel is not None else "saas-launch"
        rounds_str = self.query_one("#rounds-input", Input).value or "3"
        dashboard = self.query_one("#dashboard-switch", Switch).value
        self.app.state.update(
            demo=True,
            scenario=scenario,
            rounds=int(rounds_str),
            dashboard=dashboard,
            provider="openai",
            model=None,
            config=None,
            template=None,
            output="./output",
        )
        self.app.push_screen("confirm")

    def on_mount(self) -> None:
        self.query_one(OptionList).focus()

    def on_option_list_option_selected(self, event) -> None:
        self._go_next()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "rounds-input":
            self._go_next()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            self._go_next()


class TemplateScreen(Screen):
    """Template selection screen with live previews."""

    def compose(self) -> ComposeResult:
        template_dir = Path(__file__).parent.parent.parent / "templates" / "companies"
        templates = sorted(p.stem for p in template_dir.glob("*.json") if p.is_file())
        self.app.state["templates"] = templates
        self.app.state["template_dir"] = str(template_dir)

        # Load rich previews from JSON files
        previews: dict[str, dict[str, str]] = {}
        for t in templates:
            try:
                data = json.loads((template_dir / f"{t}.json").read_text(encoding="utf-8"))
                previews[t] = {
                    "name": data.get("name", t),
                    "product": data.get("product", ""),
                    "segment": data.get("target", {}).get("segment", ""),
                    "value": data.get("value_proposition", "")[:60] + "…" if len(data.get("value_proposition", "")) > 60 else data.get("value_proposition", ""),
                }
            except Exception:
                previews[t] = {"name": t, "product": "", "segment": "", "value": ""}
        self.app.state["template_previews"] = previews

        with Center():
            with Vertical(classes="menu-container"):
                yield Static("\uf115  Run from Template", classes="title")
                yield Static("Built-in company configurations", classes="subtitle")
                yield OptionList(
                    *[
                        Option(
                            f"[bold]{previews[t]['name']}[/bold]  [dim]({t})[/dim]\n"
                            f"[italic]{previews[t]['product']}[/italic]\n"
                            f"[dim]{previews[t]['segment']}[/dim]",
                            id=t,
                        )
                        for t in templates
                    ],
                )
                yield Static("[dim]↑↓ navigate · Enter select · Esc back[/dim]", classes="hint")
                with Horizontal(classes="button-row"):
                    yield Button("← Back", variant="default", id="back")
                    yield Button("Next →", variant="primary", id="next")

    def on_mount(self) -> None:
        ol = self.query_one(OptionList)
        ol.highlighted = 0
        ol.focus()

    def _go_next(self) -> None:
        ol = self.query_one(OptionList)
        sel = ol.highlighted
        templates = self.app.state.get("templates", [])
        if not templates:
            self.notify("No templates found — check templates/companies/ directory", severity="error")
            return
        template = templates[sel] if sel is not None else templates[0]
        self.app.state["template"] = template
        # Pre-load preview for ConfirmScreen
        previews = self.app.state.get("template_previews", {})
        self.app.state["template_preview"] = previews.get(template, {})
        self.app.push_screen("provider")

    def on_option_list_option_selected(self, event) -> None:
        self._go_next()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            self._go_next()


class ConfigScreen(Screen):
    """Custom config path input."""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(classes="menu-container"):
                yield Static("\uf0c5  Real Council Run", classes="title")
                yield Static("Enter path to your company JSON config", classes="subtitle")
                yield Input(placeholder="e.g. ./my-company.json", id="config-input")
                yield Static("[dim]Tip: copy from templates/companies/ as a starting point[/dim]", classes="hint")
                yield Static("[dim]↑↓ navigate · Tab next field · Enter confirm · Esc back[/dim]", classes="hint")
                with Horizontal(classes="button-row"):
                    yield Button("← Back", variant="default", id="back")
                    yield Button("Next →", variant="primary", id="next")

    def _go_next(self) -> None:
        path = self.query_one("#config-input", Input).value.strip()
        if not path:
            self.notify("Config path is required", severity="error")
            return
        p = Path(path)
        if not p.exists():
            self.notify(f"File not found: {path}", severity="error")
            return
        if not p.suffix.lower() == ".json":
            self.notify("Config must be a .json file", severity="warning")
        self.app.state["config"] = path
        self.app.state["template"] = None
        self.app.push_screen("provider")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "config-input":
            self._go_next()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            self._go_next()


class ProviderScreen(Screen):
    """LLM provider selection."""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(classes="menu-container"):
                yield Static("\uf233  LLM Provider", classes="title")
                yield Static("Choose who powers the agents", classes="subtitle")
                yield OptionList(
                    *[
                        Option(f"{name}  [dim](default: {default_model})[/dim]", id=key)
                        for key, name, default_model in _PROVIDERS
                    ],
                    classes="provider-options",
                )
                yield Rule()
                yield Static("API Key (optional — overrides env):", classes="field-label")
                yield Input(placeholder="leave empty to use env variable", id="api-key-input")
                yield Static("Model override (optional):", classes="field-label")
                yield Input(placeholder="leave empty — OpenRouter auto-picks a free model", id="model-input")
                yield Rule()
                yield Static("Rounds:", classes="field-label")
                yield Input(value="3", placeholder="3", id="rounds-input")
                yield Static("Dashboard:", classes="field-label")
                with Horizontal(classes="switch-row"):
                    yield Switch(value=True, id="dashboard-switch")
                    yield Label("Enable live terminal dashboard")
                yield Static("Output directory:", classes="field-label")
                yield Input(value="./output", placeholder="./output", id="output-input")
                with Horizontal(classes="button-row"):
                    yield Button("← Back", variant="default", id="back")
                    yield Button("Next →", variant="primary", id="next")

    def on_mount(self) -> None:
        ol = self.query_one(OptionList)
        ol.highlighted = 0
        ol.focus()

    def _go_next(self) -> None:
        ol = self.query_one(OptionList)
        sel = ol.highlighted
        provider = _PROVIDERS[sel][0] if sel is not None else "openai"
        api_key = self.query_one("#api-key-input", Input).value.strip() or None
        model = self.query_one("#model-input", Input).value.strip() or None
        rounds_str = self.query_one("#rounds-input", Input).value or "3"
        try:
            rounds = int(rounds_str)
            if rounds < 1 or rounds > 20:
                raise ValueError
        except ValueError:
            self.notify("Rounds must be a number between 1 and 20", severity="error")
            return
        dashboard = self.query_one("#dashboard-switch", Switch).value
        output = self.query_one("#output-input", Input).value.strip() or "./output"
        self.app.state.update(
            provider=provider,
            api_key=api_key,
            model=model,
            rounds=rounds,
            dashboard=dashboard,
            output=output,
        )
        self.app.push_screen("confirm")

    def on_option_list_option_selected(self, event) -> None:
        self._go_next()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "model-input":
            self.query_one("#rounds-input", Input).focus()
        elif event.input.id in ("rounds-input", "output-input"):
            self._go_next()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            self._go_next()


class ConfirmScreen(Screen):
    """Final review before execution with rich preview."""

    def compose(self) -> ComposeResult:
        st = self.app.state
        lines: list[str] = []
        preview = st.get("template_preview", {})

        if st.get("demo"):
            lines.append("[bold cyan]Mode:[/bold cyan]      Demo")
            lines.append(f"[bold]Scenario:[/bold]  {st.get('scenario', '?')}")
        elif st.get("template"):
            lines.append("[bold cyan]Mode:[/bold cyan]      Template")
            lines.append(f"[bold]Company:[/bold]   {preview.get('name', st.get('template', '?'))}")
            if preview.get('product'):
                lines.append(f"[bold]Product:[/bold]   {preview['product']}")
            if preview.get('segment'):
                lines.append(f"[bold]Target:[/bold]    {preview['segment']}")
        else:
            lines.append("[bold cyan]Mode:[/bold cyan]      Real Run")
            lines.append(f"[bold]Config:[/bold]    {st.get('config', '?')}")

        lines.append(f"[bold]Provider:[/bold]  {st.get('provider', '?').upper()}")
        lines.append(f"[bold]API Key:[/bold]   {'[green]••••••••[/green]' if st.get('api_key') else '[dim]env[/dim]'}")
        model_display = st.get('model') or ('[green]auto (free)[/green]' if st.get('provider') == 'openrouter' else 'default')
        lines.append(f"[bold]Model:[/bold]     {model_display}")
        lines.append(f"[bold]Rounds:[/bold]    {st.get('rounds', 3)}")
        lines.append(f"[bold]Dashboard:[/bold] {'[green]Yes[/green]' if st.get('dashboard') else '[dim]No[/dim]'}")
        lines.append(f"[bold]Output:[/bold]    {st.get('output', './output')}")

        with Center():
            with Vertical(classes="menu-container"):
                yield Static("\uf00c  Ready to Run", classes="title")
                yield Static("Review your settings before launch", classes="subtitle")
                yield Rule()
                yield Static("\n".join(lines), classes="summary")
                yield Rule()
                with Horizontal(classes="button-row"):
                    yield Button("← Back", variant="default", id="back")
                    yield Button("▶ Run", variant="success", id="run")

    def on_mount(self) -> None:
        self.query_one("#run", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "run":
            st = self.app.state
            ns = argparse.Namespace(
                config=st.get("config"),
                provider=st.get("provider", "openai"),
                api_key=st.get("api_key"),
                model=st.get("model"),
                platform="cli",
                rounds=st.get("rounds", 3),
                timeout=300.0,
                output=st.get("output", "./output"),
                monitor=False,
                aggregate=False,
                verbose=False,
                documents=None,
                documents_dir=None,
                scalac_mode=False,
                dashboard=st.get("dashboard", False),
                demo=st.get("demo", False),
                scenario=st.get("scenario", "saas-launch"),
                template=st.get("template"),
            )
            self.app.exit(ns)


class QuitConfirmScreen(Screen):
    """Confirm before exiting."""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(classes="menu-container"):
                yield Static("\uf128  Quit?", classes="title")
                yield Static("Any running council will be cancelled.", classes="subtitle")
                yield Rule()
                with Horizontal(classes="button-row"):
                    yield Button("← Back", variant="default", id="back")
                    yield Button("Quit", variant="error", id="quit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "quit":
            self.app.exit(None)


class HelpScreen(Screen):
    """How the debate works."""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(classes="menu-container"):
                yield Static("\uf128  How the Debate Works", classes="title")
                yield Static(
                    "[bold]Round 1:[/bold] Each agent writes their specialised output\n"
                    "  Marcus → offer, Elena → funnel, Kai → copy, David → ABM\n\n"
                    "[bold]Round 2:[/bold] Agents read and critique each other\n"
                    "  Marcus might say: 'Elena, at this price your funnel breaks'\n\n"
                    "[bold]Round 3:[/bold] Final outputs with all feedback incorporated\n\n"
                    "[dim]The result is a plan that survived criticism from 4 experts.[/dim]",
                    classes="description",
                )
                with Center():
                    yield Button("← Back", variant="default", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()


class IDEScreen(Screen):
    """IDE setup help."""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(classes="menu-container"):
                yield Static("\uf108  IDE Setup", classes="title")
                yield Static(
                    "[bold]VS Code / Cursor / Windsurf[/bold]\n"
                    "  Open integrated terminal (Ctrl+`)\n"
                    "  Run: python -m council\n\n"
                    "[bold]Kimi Code IDE[/bold]\n"
                    "  Run: python -m council --provider kimi-code\n"
                    "  No API key — uses your logged-in Kimi session\n\n"
                    "[bold]Claude Code IDE[/bold]\n"
                    "  Run: python -m council --provider claude-code\n"
                    "  Reads OAuth from ~/.claude/.credentials.json\n\n"
                    "[bold]GitHub Codespaces[/bold]\n"
                    "  Run: python -m council --platform copilot\n\n"
                    "[dim]All platforms auto-detect.[/dim]",
                    classes="description",
                )
                with Center():
                    yield Button("← Back", variant="default", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()


# ── App ─────────────────────────────────────────────────────────────────────

class CouncilMenuApp(App):
    """Textual interactive menu for the AI Marketing Council."""

    CSS = """
    Screen { align: center middle; }

    .menu-container {
        width: 70;
        height: auto;
        max-height: 90%;
        border: solid $primary-darken-2;
        padding: 1 2;
        background: $surface-darken-1 40%;
    }

    .title {
        text-style: bold;
        width: 100%;
        content-align: center middle;
        height: auto;
        padding: 1 0;
        color: $text;
    }

    .subtitle {
        color: $text-muted;
        width: 100%;
        content-align: center middle;
        height: auto;
        padding-bottom: 1;
    }

    .section-title {
        text-style: bold;
        width: 100%;
        content-align: center middle;
        height: auto;
        padding: 1 0;
    }

    .agents-list {
        width: 100%;
        content-align: center middle;
        height: auto;
        padding: 1 0;
    }

    .description {
        color: $text-muted;
        width: 100%;
        content-align: center middle;
        height: auto;
        padding: 1 0;
    }

    .hint {
        color: $text-muted;
        width: 100%;
        content-align: center middle;
        height: auto;
        padding-top: 1;
    }

    .field-label {
        text-style: bold;
        padding-top: 1;
        height: auto;
    }

    .switch-row {
        height: auto;
        padding: 1 0;
    }

    .button-row {
        height: auto;
        content-align: center middle;
        padding-top: 1;
    }

    .button-row Button {
        margin: 0 1;
    }

    .summary {
        width: 100%;
        height: auto;
        padding: 1 2;
    }

    OptionList {
        width: 100%;
        height: auto;
        max-height: 20;
        border: solid $surface-lighten-1;
        padding: 0 1;
    }

    .provider-options {
        max-height: 6;
    }

    OptionList:focus {
        border: solid $primary;
    }

    Input {
        width: 100%;
        margin: 1 0;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, start_screen: str = "main", **kwargs) -> None:
        super().__init__(**kwargs)
        self.state: dict = {}
        self._start_screen = start_screen

    def on_mount(self) -> None:
        self.install_screen(WelcomeScreen(), "welcome")
        self.install_screen(MainMenuScreen(), "main")
        self.install_screen(DemoScreen(), "demo")
        self.install_screen(TemplateScreen(), "template")
        self.install_screen(ProviderScreen(), "provider")
        self.install_screen(ConfigScreen(), "config")
        self.install_screen(ConfirmScreen(), "confirm")
        self.install_screen(HelpScreen(), "help")
        self.install_screen(IDEScreen(), "ide")
        self.install_screen(QuitConfirmScreen(), "quit_confirm")
        self.push_screen(self._start_screen)

    def action_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()
        else:
            self.exit(None)

    def action_quit(self) -> None:
        self.exit(None)


# ── Public API ──────────────────────────────────────────────────────────────

def prompt_for_args(force_onboarding: bool = False) -> Optional[argparse.Namespace]:
    """Run the interactive menu and return a populated Namespace.

    On first run (or when force_onboarding=True) shows an onboarding
    wizard that explains the system and recommends a quick demo.
    """
    start = "welcome" if (force_onboarding or not _is_onboarding_done()) else "main"
    app = CouncilMenuApp(start_screen=start)
    result = app.run()
    if result is None:
        sys.exit(0)
    return result
