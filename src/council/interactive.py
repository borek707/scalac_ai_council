"""Interactive TUI menu for the AI Marketing Council.

Provides a rich-text menu for choosing modes, scenarios, and options
without memorising CLI flags. Includes a first-run onboarding wizard.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from council.demo import list_scenarios

console = Console()

_ONBOARDING_FLAG = Path.home() / ".config" / "council" / "onboarding_done"


def _is_onboarding_done() -> bool:
    """Check if the user has already completed onboarding."""
    return _ONBOARDING_FLAG.exists()


def _mark_onboarding_done() -> None:
    """Mark onboarding as completed."""
    _ONBOARDING_FLAG.parent.mkdir(parents=True, exist_ok=True)
    _ONBOARDING_FLAG.touch(exist_ok=True)


def _header() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]🤖 Universal AI Marketing Council[/bold cyan]\n"
            "[dim]v3.2 — AI-powered marketing strategy for B2B[/dim]",
            border_style="cyan",
        )
    )


def _onboarding_flow() -> argparse.Namespace:
    """First-run onboarding wizard for new users.

    Returns:
        argparse.Namespace ready to run.
    """
    console.print()
    console.print(
        Panel(
            "[bold]Welcome![/bold] This tool runs [cyan]4 AI marketing specialists[/cyan] who\n"
            "debate in rounds and produce a complete marketing plan for your company.\n\n"
            "[dim]No templates. No hardcoded data. Real LLM debate.[/dim]",
            title="👋 First Run",
            border_style="green",
        )
    )

    console.print()
    console.print(
        "[bold]The Four Agents:[/bold]\n"
        "  🏗️  [cyan]Marcus[/cyan] — Offer Architect (pricing, positioning, packaging)\n"
        "  🎯  [magenta]Elena[/magenta] — Funnel Architect (pipeline, conversion, velocity)\n"
        "  ✍️  [green]Kai[/green] — Copywriter (landing pages, emails, ads)\n"
        "  🎣  [yellow]David[/yellow] — Lead Strategist (ABM, accounts, outreach)\n"
    )
    console.print(
        "[dim]Each round they read each other's work, criticise, and improve.\n"
        "After 2-3 rounds you get a polished, multi-perspective plan.[/dim]"
    )
    console.print()

    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column()
    table.add_row("[1]", "🎮  Quick Demo — see it in action, no setup needed")
    table.add_row("[2]", "⚙️   Real Run — I have a company JSON config")
    table.add_row("[3]", "📊  Dashboard Demo — watch the live terminal dashboard")
    table.add_row("[4]", "💻  How to use in my IDE — VS Code, Cursor, Kimi, Claude")
    table.add_row("[5]", "📖  Help — how the debate works")
    table.add_row("[s]", "⏭️   Skip — go to main menu")
    console.print(table)
    console.print()

    choice = Prompt.ask(
        "What would you like to do first",
        choices=["1", "2", "3", "4", "5", "s"],
        show_choices=False,
        default="1",
    )

    if choice == "5":
        console.print()
        console.print(
            Panel(
                "[bold]How the debate works[/bold]\n\n"
                "1. [cyan]Round 1[/cyan]: Each agent writes their specialised output\n"
                "   (Marcus → offer, Elena → funnel, Kai → copy, David → ABM)\n\n"
                "2. [cyan]Round 2[/cyan]: Agents read each other's work and critique it\n"
                "   Marcus might say: 'Elena, at this price your funnel breaks'\n\n"
                "3. [cyan]Round 3[/cyan]: Final outputs incorporating all feedback\n\n"
                "[dim]The result is a plan that survived criticism from 4 experts.[/dim]",
                border_style="blue",
            )
        )
        console.print()
        if Confirm.ask("Run a quick demo now", default=True):
            _mark_onboarding_done()
            return _demo_menu(dashboard_default=True)
        else:
            _mark_onboarding_done()
            return _choose_mode_and_run()

    if choice == "4":
        _show_ide_help()
        _mark_onboarding_done()
        return _choose_mode_and_run()

    if choice == "3":
        _mark_onboarding_done()
        return _demo_menu(dashboard_default=True)

    if choice == "1":
        _mark_onboarding_done()
        return _demo_menu(dashboard_default=False)

    if choice == "2":
        _mark_onboarding_done()
        return _real_menu()

    # "s" skip
    _mark_onboarding_done()
    return _choose_mode_and_run()


def _show_ide_help() -> None:
    """Display help for running in various IDEs."""
    console.print()
    console.print(
        Panel(
            "[bold]💻 Using the Council in your IDE[/bold]\n\n"
            "[cyan]VS Code / Cursor / Windsurf:[/cyan]\n"
            "  1. Open the integrated terminal (Ctrl+`)\n"
            "  2. Run: [bold]python -m council[/bold]\n"
            "  3. Files appear in the output/ folder — refresh explorer to see them\n\n"
            "[cyan]Kimi Code IDE:[/cyan]\n"
            "  1. Open terminal in Kimi Code\n"
            "  2. Run: [bold]python -m council --provider kimi-code[/bold]\n"
            "  3. No API key needed — uses your logged-in Kimi session\n\n"
            "[cyan]Claude Code IDE:[/cyan]\n"
            "  1. Open terminal in Claude Code\n"
            "  2. Run: [bold]python -m council --provider claude-code[/bold]\n"
            "  3. No API key needed — reads OAuth from ~/.claude/.credentials.json\n\n"
            "[cyan]GitHub Codespaces:[/cyan]\n"
            "  1. Open terminal in Codespaces\n"
            "  2. Run: [bold]python -m council --platform copilot[/bold]\n\n"
            "[dim]All platforms auto-detect. Just run 'python -m council' and it figures it out.[/dim]",
            border_style="magenta",
        )
    )
    console.print()


def _show_auth_hint(provider: str) -> None:
    """Show authentication hint for the selected provider."""
    hints = {
        "openai": (
            "[yellow]Authentication:[/yellow] Set your OpenAI key\n"
            "  export OPENAI_API_KEY='sk-...'\n"
            "  Get one at: https://platform.openai.com/api-keys"
        ),
        "anthropic": (
            "[yellow]Authentication:[/yellow] Set your Anthropic key\n"
            "  export ANTHROPIC_API_KEY='sk-ant-...'\n"
            "  Get one at: https://console.anthropic.com/settings/keys"
        ),
        "ollama": (
            "[green]Authentication:[/green] No key needed!\n"
            "  Just ensure Ollama is running:\n"
            "  ollama run llama3"
        ),
        "kimi-code": (
            "[green]Authentication:[/green] No key needed!\n"
            "  Kimi Code provider auto-detects your IDE session.\n"
            "  It runs 'kimi --quiet --yolo --prompt ...' as a subprocess."
        ),
        "claude-code": (
            "[green]Authentication:[/green] No key needed!\n"
            "  Claude Code provider reads OAuth token from:\n"
            "  ~/.claude/.credentials.json\n"
            "  Or uses the 'claude -p' CLI if installed."
        ),
    }
    hint = hints.get(provider, "")
    if hint:
        console.print()
        console.print(Panel(hint, border_style="yellow"))
        console.print()


def _choose_mode_and_run() -> argparse.Namespace:
    """Show main menu and return configured Namespace."""
    console.print()
    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column()
    table.add_row("[1]", "🎮  Demo Mode — pre-built scenarios, no API keys")
    table.add_row("[2]", "📂  Run from Template — use a built-in company config")
    table.add_row("[3]", "▶️   Real Council Run — your own config + LLM provider")
    table.add_row("[q]", "🚪  Quit")
    console.print(table)
    console.print()

    choice = Prompt.ask(
        "Select",
        choices=["1", "2", "3", "q"],
        show_choices=False,
    )

    if choice == "q":
        console.print("[dim]Goodbye![/dim]")
        sys.exit(0)
    elif choice == "1":
        return _demo_menu()
    elif choice == "2":
        return _template_menu()
    else:
        return _real_menu()


def _demo_menu(dashboard_default: bool = True) -> argparse.Namespace:
    """Interactive demo-mode configuration."""
    console.print()
    console.print("[bold green]Demo Mode[/bold green] — no API keys needed\n")

    scenarios = list_scenarios()
    table = Table(title="Choose a scenario", show_header=False, box=None)
    table.add_column(style="bold cyan")
    table.add_column(style="bold")
    table.add_column()
    for idx, s in enumerate(scenarios, 1):
        table.add_row(f"[{idx}]", s.name, f"[dim]{s.description}[/dim]")
    console.print(table)
    console.print()

    scenario_idx = IntPrompt.ask(
        "Scenario",
        choices=[str(i) for i in range(1, len(scenarios) + 1)],
        default=1,
    )
    scenario = scenarios[scenario_idx - 1]

    rounds = IntPrompt.ask("How many rounds", default=3)
    dashboard = Confirm.ask("Enable live dashboard", default=dashboard_default)

    return argparse.Namespace(
        config=None,
        provider="openai",
        model=None,
        platform="cli",
        rounds=rounds,
        timeout=300.0,
        output="./output",
        monitor=False,
        aggregate=False,
        verbose=False,
        documents=None,
        documents_dir=None,
        scalac_mode=False,
        dashboard=dashboard,
        demo=True,
        scenario=scenario.key,
        template=None,
    )


def _template_menu() -> argparse.Namespace:
    """Interactive template selection and run."""
    from pathlib import Path

    template_dir = Path(__file__).parent.parent / "templates" / "companies"
    templates = sorted(p.stem for p in template_dir.glob("*.json") if p.is_file())

    console.print()
    console.print("[bold blue]Run from Template[/bold blue] — built-in company configs\n")

    table = Table(title="Choose a company template", show_header=False, box=None)
    table.add_column(style="bold cyan")
    table.add_column(style="bold")
    table.add_column()
    for idx, name in enumerate(templates, 1):
        table.add_row(f"[{idx}]", name, f"[dim]templates/companies/{name}.json[/dim]")
    console.print(table)
    console.print()

    choice = IntPrompt.ask(
        "Template",
        choices=[str(i) for i in range(1, len(templates) + 1)],
        default=1,
    )
    template = templates[choice - 1]

    console.print()
    providers = {
        "1": ("openai", "OpenAI (GPT-4o)"),
        "2": ("anthropic", "Anthropic (Claude)"),
        "3": ("ollama", "Ollama (local)"),
        "4": ("kimi-code", "Kimi Code CLI"),
        "5": ("claude-code", "Claude Code CLI / IDE"),
    }
    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column()
    for k, (_, name) in providers.items():
        table.add_row(f"[{k}]", name)
    console.print(table)
    provider_choice = Prompt.ask(
        "LLM Provider",
        choices=list(providers.keys()),
        default="1",
    )
    provider, _ = providers[provider_choice]

    _show_auth_hint(provider)

    model: Optional[str] = None
    if provider == "openai":
        model = Prompt.ask("Model", default="gpt-4o")
    elif provider == "anthropic":
        model = Prompt.ask("Model", default="claude-sonnet-4-6")
    elif provider == "ollama":
        model = Prompt.ask("Model", default="llama3")
    elif provider == "kimi-code":
        model = Prompt.ask("Model", default="kimi-for-coding")
    elif provider == "claude-code":
        model = Prompt.ask("Model", default="claude-sonnet-4-6")

    rounds = IntPrompt.ask("How many rounds", default=3)
    dashboard = Confirm.ask("Enable live dashboard", default=True)
    output = Prompt.ask("Output directory", default="./output")

    return argparse.Namespace(
        config=None,
        provider=provider,
        model=model if model else None,
        platform="cli",
        rounds=rounds,
        timeout=300.0,
        output=output,
        monitor=False,
        aggregate=False,
        verbose=False,
        documents=None,
        documents_dir=None,
        scalac_mode=False,
        dashboard=dashboard,
        demo=False,
        scenario="saas-launch",
        template=template,
    )


def _real_menu() -> argparse.Namespace:
    """Interactive real-run configuration."""
    console.print()
    console.print("[bold blue]Real Council Run[/bold blue] — requires config + LLM keys\n")

    config_path = Prompt.ask("Path to company JSON config")
    while not config_path.strip():
        console.print("[red]Config path is required.[/red]")
        config_path = Prompt.ask("Path to company JSON config")

    console.print()
    providers = {
        "1": ("openai", "OpenAI (GPT-4o)"),
        "2": ("anthropic", "Anthropic (Claude)"),
        "3": ("ollama", "Ollama (local)"),
        "4": ("kimi-code", "Kimi Code CLI"),
        "5": ("claude-code", "Claude Code CLI / IDE"),
    }
    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column()
    for k, (_, name) in providers.items():
        table.add_row(f"[{k}]", name)
    console.print(table)
    provider_choice = Prompt.ask(
        "LLM Provider",
        choices=list(providers.keys()),
        default="1",
    )
    provider, _ = providers[provider_choice]

    _show_auth_hint(provider)

    model: Optional[str] = None
    if provider == "openai":
        model = Prompt.ask("Model", default="gpt-4o")
    elif provider == "anthropic":
        model = Prompt.ask("Model", default="claude-sonnet-4-6")
    elif provider == "ollama":
        model = Prompt.ask("Model", default="llama3")
    elif provider == "kimi-code":
        model = Prompt.ask("Model", default="kimi-for-coding")
    elif provider == "claude-code":
        model = Prompt.ask("Model", default="claude-sonnet-4-6")

    rounds = IntPrompt.ask("How many rounds", default=3)
    dashboard = Confirm.ask("Enable live dashboard", default=True)
    output = Prompt.ask("Output directory", default="./output")

    return argparse.Namespace(
        config=config_path.strip(),
        provider=provider,
        model=model if model else None,
        platform="cli",
        rounds=rounds,
        timeout=300.0,
        output=output,
        monitor=False,
        aggregate=False,
        verbose=False,
        documents=None,
        documents_dir=None,
        scalac_mode=False,
        dashboard=dashboard,
        demo=False,
        scenario="saas-launch",
        template=None,
    )


def prompt_for_args(force_onboarding: bool = False) -> argparse.Namespace:
    """Run the interactive menu and return a populated Namespace.

    On first run (or when force_onboarding=True) shows an onboarding
    wizard that explains the system and recommends a quick demo.

    Args:
        force_onboarding: Show onboarding even if already completed.

    Returns:
        argparse.Namespace compatible with council.cli._run_council.
    """
    _header()

    if force_onboarding or not _is_onboarding_done():
        return _onboarding_flow()

    return _choose_mode_and_run()
