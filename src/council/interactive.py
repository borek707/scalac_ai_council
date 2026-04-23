"""Interactive TUI menu for the AI Marketing Council.

Provides a rich-text menu for choosing modes, scenarios, and options
without memorising CLI flags.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from council.demo import list_scenarios

console = Console()


def _header() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]🤖 Universal AI Marketing Council[/bold cyan]\n"
            "[dim]v3.1 — AI-powered marketing strategy for B2B[/dim]",
            border_style="cyan",
        )
    )


def _choose_mode() -> str:
    """Ask user to choose between demo and real run."""
    console.print()
    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column()
    table.add_row("[1]", "🎮  Demo Mode — pre-built scenarios, no API keys")
    table.add_row("[2]", "▶️   Real Council Run — your config + LLM provider")
    table.add_row("[q]", "🚪  Quit")
    console.print(table)
    console.print()

    choice = Prompt.ask(
        "Select",
        choices=["1", "2", "q"],
        show_choices=False,
    )
    return choice


def _demo_menu() -> argparse.Namespace:
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
    dashboard = Confirm.ask("Enable live dashboard", default=True)

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

    model: Optional[str] = None
    if provider == "openai":
        model = Prompt.ask("Model", default="gpt-4o")
    elif provider == "anthropic":
        model = Prompt.ask("Model", default="claude-sonnet-4-6")
    elif provider == "ollama":
        model = Prompt.ask("Model", default="llama3")
    elif provider == "kimi-code":
        model = Prompt.ask("Model", default="kimi-for-coding")

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
    )


def prompt_for_args() -> argparse.Namespace:
    """Run the interactive menu and return a populated Namespace.

    Returns:
        argparse.Namespace compatible with council.cli._run_council.
    """
    _header()
    choice = _choose_mode()

    if choice == "q":
        console.print("[dim]Goodbye![/dim]")
        sys.exit(0)
    elif choice == "1":
        return _demo_menu()
    else:
        return _real_menu()
