from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from council.config.loader import ConfigLoader
from council.llm.provider import LLMProvider
from council.platform.base import PlatformAdapter

logger = logging.getLogger(__name__)
console = Console()

# Supported platforms with their display names and env detection
PLATFORM_REGISTRY: dict[str, tuple[str, list[str]]] = {
    "cli": ("CLI (local)", []),
    "kimi": ("Kimi Code", ["KIMI_SESSION_ID", "KIMI_API_KEY"]),
    "idx": ("Google IDX", ["GOOGLE_CLOUD_WORKSTATIONS", "IDX_ENVIRONMENT"]),
    "cursor": ("Cursor", ["CURSOR_TRACE_ID", "CURSOR_PID"]),
    "copilot": ("GitHub Copilot / Codespaces", ["CODESPACES", "GITHUB_COPILOT"]),
    "web": ("Web Platform (Bolt/Lovable/Replit)", ["BOLT_ENV", "LOVABLE_ENV", "REPL_ID"]),
}


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the council."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def auto_detect_platform() -> str:
    """Auto-detect the current AI IDE / platform environment.

    Checks environment variables specific to each platform and
    returns the best matching platform key.
    """
    for key, (_, env_vars) in PLATFORM_REGISTRY.items():
        if key == "cli":
            continue
        for env_var in env_vars:
            if os.environ.get(env_var):
                return key
    return "cli"


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    auto_platform = auto_detect_platform()
    auto_msg = f"auto-detected: {auto_platform}" if auto_platform != "cli" else "default"

    # Discover available templates
    template_dir = _resolve_template_dir()
    available_templates = []
    if template_dir.exists():
        available_templates = sorted(
            p.stem for p in template_dir.glob("*.json") if p.is_file()
        )

    parser = argparse.ArgumentParser(
        description="Universal AI Marketing Council v3.2 — 4 AI agents debate and create a marketing plan for your company.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Platform auto-detection: {{ {auto_msg} }}

Quick start (pick one):
  First time here?          python -m council
  See it in action (no keys) python -m council --demo --dashboard
  Run with a template        python -m council --template saas --dashboard
  Run with your company      python -m council --config firm.json
  Use Claude Code IDE        python -m council --config firm.json --provider claude-code
  Use Kimi Code IDE          python -m council --config firm.json --provider kimi-code

Common operations:
  More debate rounds         python -m council --template saas --rounds 5
  Live terminal dashboard    python -m council --template saas --dashboard
  Aggregate final proposal   python -m council --template saas --aggregate
  Only check status          python -m council --config firm.json --monitor

Built-in templates:
{chr(10).join(f"  {t:12} templates/companies/{t}.json" for t in available_templates)}

Supported platforms:
  cli       Local terminal (default)
  kimi      Kimi Code IDE (sessions_spawn)
  idx       Google IDX / Project IDX
  cursor    Cursor AI IDE
  copilot   GitHub Copilot / Codespaces
  web       Bolt.new / Lovable.dev / Replit

Need more help? Read README.md or run: python -m council --interactive
        """,
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help="Path to company JSON config file (not needed in --demo mode)",
    )
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "anthropic", "ollama", "openrouter", "kimi-code", "claude-code"],
        help="LLM provider to use (default: openai)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name override",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key for the selected provider (overrides env variable)",
    )
    parser.add_argument(
        "--platform",
        default=auto_platform,
        choices=list(PLATFORM_REGISTRY.keys()),
        help=f"Target platform/IDE (default: {auto_platform})",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=3,
        help="Maximum number of debate rounds (default: 3)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="Round timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--output", "-o",
        default="./output",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Only show status without running",
    )
    parser.add_argument(
        "--aggregate",
        action="store_true",
        help="(deprecated, artifacts are always written) kept for backwards compatibility",
    )
    parser.add_argument(
        "--review",
        metavar="DIR",
        default=None,
        help="Review a previous run from the given output directory",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--documents", "-d",
        nargs="+",
        default=None,
        help="Markdown/text files to inject as agent context "
             "(e.g. -d brief.md research.md)",
    )
    parser.add_argument(
        "--documents-dir",
        default=None,
        help="Directory with .md/.txt files to load as context",
    )
    parser.add_argument(
        "--template",
        default=None,
        choices=available_templates or None,
        metavar="NAME",
        help="Use a built-in company template (e.g. saas, fintech, ecommerce). "
             "Ignores --config. Run without value to see available templates.",
    )
    parser.add_argument(
        "--scalac-mode",
        action="store_true",
        help="Load built-in Scalac context bundle (no config needed)",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Show real-time live dashboard with agent panels (requires 'textual')",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with pre-built scenarios (no LLM keys needed)",
    )
    parser.add_argument(
        "--scenario",
        default="saas-launch",
        choices=["saas-launch", "ecommerce-rebrand", "fintech-scale", "healthcare-app"],
        help="Demo scenario to run (default: saas-launch)",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Launch interactive menu (no flags needed)",
    )
    parser.add_argument(
        "--onboarding",
        action="store_true",
        help="Force the first-run onboarding wizard",
    )
    parser.add_argument(
        "--brief",
        default=None,
        help="Custom campaign brief / prompt (e.g. 'ABM campaign for CFOs in fintech')",
    )
    parser.add_argument(
        "--free-tier",
        action="store_true",
        help="Use OpenRouter free-tier model fallback (fetches current free models)",
    )
    return parser.parse_args(args)


def _resolve_template_dir() -> Path:
    """Find the built-in company templates directory.

    Tries several resolution strategies so that templates are found
    whether the code runs from source, an editable install, or a
    packaged wheel.
    """
    # Strategy 1: relative to this source file (development / editable)
    src_dir = Path(__file__).parent.parent.parent / "templates" / "companies"
    if src_dir.exists():
        return src_dir

    # Strategy 2: relative to current working directory
    cwd_dir = Path.cwd() / "templates" / "companies"
    if cwd_dir.exists():
        return cwd_dir

    # Strategy 3: absolute path from project root env hint
    if root := os.environ.get("COUNCIL_ROOT"):
        env_dir = Path(root) / "templates" / "companies"
        if env_dir.exists():
            return env_dir

    # Fallback — return the source-derived path so the caller can
    # produce a meaningful "not found" error.
    return src_dir


def _create_platform_adapter(platform: str) -> PlatformAdapter:
    """Create the appropriate platform adapter."""
    from council.platform.cli_adapter import CLIAdapter

    if platform == "kimi":
        from council.platform.kimi_adapter import KimiAdapter
        return KimiAdapter()
    elif platform == "idx":
        from council.platform.idx_adapter import GoogleIDXAdapter
        return GoogleIDXAdapter()
    elif platform == "cursor":
        from council.platform.cursor_adapter import CursorAdapter
        return CursorAdapter()
    elif platform == "copilot":
        from council.platform.copilot_adapter import GitHubCopilotAdapter
        return GitHubCopilotAdapter()
    elif platform == "web":
        from council.platform.web_adapter import WebPlatformAdapter
        return WebPlatformAdapter()
    else:
        return CLIAdapter()


async def _run_demo(args: argparse.Namespace, dashboard=None) -> None:
    """Run a pre-built demo scenario without LLM keys."""
    from council.demo import get_scenario, run_demo

    workspace = Path(args.output)
    workspace.mkdir(parents=True, exist_ok=True)

    scenario = get_scenario(args.scenario)
    logger.info("Demo mode: scenario='%s' (%s), rounds=%d", scenario.key, scenario.name, args.rounds)

    progress_callback = dashboard.make_callback() if dashboard else None
    await run_demo(
        scenario_key=args.scenario,
        rounds=args.rounds,
        workspace=workspace,
        progress_callback=progress_callback,
    )

    logger.info("Demo run complete. Output: %s", workspace)
    _print_success_summary(workspace, args.rounds, False)


async def _run_council(args: argparse.Namespace, dashboard=None) -> None:
    """Execute the council with parsed arguments."""
    setup_logging(args.verbose)

    if getattr(args, "review", None):
        _review_run(Path(args.review))
        return

    if args.demo:
        await _run_demo(args, dashboard)
        return

    # Resolve --template to a config path
    if getattr(args, "template", None):
        template_dir = _resolve_template_dir()
        template_path = template_dir / f"{args.template}.json"
        if template_path.exists():
            args.config = str(template_path)
            logger.info("Using template: %s", args.template)
        else:
            available = sorted(p.stem for p in template_dir.glob("*.json")) if template_dir.exists() else []
            raise FileNotFoundError(
                f"Template not found: {args.template}\n"
                f"  Looked in: {template_dir}\n"
                f"  Available: {', '.join(available) or '(none)'}"
            )

    # Issue #22: short-circuit before config loading when --monitor is requested.
    if args.monitor:
        _show_status(Path(args.output))
        return

    if not args.config:
        logger.error(
            "Missing --config. You have three options:\n"
            "  1. Run demo (no config needed):  python -m council --demo\n"
            "  2. Use a built-in template:       python -m council --template saas\n"
            "  3. Run interactive menu:          python -m council --interactive"
        )
        sys.exit(1)

    config_path = Path(args.config)
    if not config_path.exists():
        raise FileNotFoundError(
            f"{config_path}\n\n"
            "What to do:\n"
            f"  • Check the path is correct: ls -la {config_path.parent}\n"
            f"  • Copy a template: cp templates/companies/saas.json {config_path}\n"
            "  • Or run demo instead: python -m council --demo"
        )

    logger.info("Loading configuration from %s", config_path)
    company_config = ConfigLoader.from_json(config_path)
    logger.info(
        "Loaded config for company: %s (%s)",
        company_config.name,
        company_config.product,
    )

    workspace = Path(args.output)
    # Confirmation if output directory already has content
    if workspace.exists() and any(workspace.iterdir()):
        logger.warning(
            "Output directory %s already exists and contains files.\n"
            "New outputs may overwrite previous results.",
            workspace,
        )

    workspace.mkdir(parents=True, exist_ok=True)

    # Save custom brief if provided
    if getattr(args, "brief", None):
        brief_path = workspace / "shared" / "brief.md"
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(args.brief, encoding="utf-8")
        logger.info("Saved campaign brief to %s", brief_path)

    # Set API key if provided
    # Issue #4: ollama and kimi-code don't use API keys — warn and skip instead.
    _NO_API_KEY_PROVIDERS = {"ollama", "kimi-code"}
    if getattr(args, "api_key", None):
        if args.provider in _NO_API_KEY_PROVIDERS:
            logger.warning(
                "Provider '%s' does not use an API key — --api-key will be ignored.",
                args.provider,
            )
        else:
            env_map = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "claude-code": "ANTHROPIC_API_KEY",
                "openrouter": "OPENROUTER_API_KEY",
            }
            if args.provider not in env_map:
                raise ValueError(
                    f"Unknown provider '{args.provider}': cannot determine which env var to set for --api-key.\n"
                    f"  Supported providers: {', '.join(sorted(env_map))}"
                )
            env_var = env_map[args.provider]
            os.environ[env_var] = args.api_key
            logger.info("API key set from command line for provider %s", args.provider)

    config_save_path = workspace / "config.json"
    config_save_path.write_text(
        company_config.model_dump_json(indent=2),
        encoding="utf-8",
    )
    logger.info("Saved runtime company config to %s", config_save_path)

    # Explicit defaults logging (Principle 7)
    logger.info(
        "Settings: provider=%s, model=%s, rounds=%d, platform=%s, timeout=%.0fs",
        args.provider,
        args.model or "default",
        args.rounds,
        args.platform,
        args.timeout,
    )

    # Load documents (markdown context for agents)
    from council.config.documents import DocumentLoader
    doc_loader = DocumentLoader()
    documents: list = []

    if args.scalac_mode:
        logger.info("Scalac mode: loading built-in context bundle")
        documents = doc_loader.load_scalac_bundle()
        # Auto-generate Scalac config if no --config provided
        if args.config == "scalac.json" or not Path(args.config).exists():
            from council.config.schema import (
                CompanyConfig, Competitor, Constraints, TargetSegment,
            )
            company_config = CompanyConfig(
                name="Scalac",
                product="Software development (Scala, Blockchain, ML, Data)",
                pricing_tier="Team Extension EUR 6-8K/engineer/month",
                value_proposition="Europe's largest Scala team (150+ engineers) with blockchain & ML expertise",
                competitors=[
                    Competitor(name="VirtusLab", threat="HIGH", pricing="PLN 800-1200/day", weakness="Smaller blockchain practice", clients=["Comcast", "Hazelcast"]),
                    Competitor(name="SoftwareMill", threat="MEDIUM", pricing="PLN 700-1000/day", weakness="No ML/blockchain focus", clients=["Virgin"]),
                    Competitor(name="EPAM", threat="HIGH", pricing="$50-80/h", weakness="Generalist, not Scala-focused", clients=["Google", "Microsoft"]),
                ],
                target=TargetSegment(
                    segment="Series A-C startups & enterprises adopting Scala/blockchain",
                    decision_maker="CTO / VP Engineering",
                    pain_points=["Can't hire Scala talent", "Blockchain projects stall", "Need to scale engineering fast"],
                    budget_range="EUR 50-500K/year",
                    geo_focus=["EU", "UK", "US East Coast"],
                ),
                constraints=Constraints(
                    timeline_days=90,
                    team_size=4,
                    focus_areas=["lead generation", "brand awareness", "case studies"],
                ),
                differentiators=[
                    "Largest Scala team in Europe (150+)",
                    "Deep blockchain expertise (Substrate, EVM)",
                    "ML & Data Engineering practice",
                    "Functional programming pedigree since 2014",
                ],
                case_studies=[
                    {"client": "SwissBorg", "result": "30+ engineers, 3 years, $4.5B AUM"},
                    {"client": "Colossus", "result": "NFT marketplace, 20 engineers, 18 months"},
                    {"client": "Billie", "result": "BNPL fintech migration, 10 engineers, 12 months"},
                ],
            )
            logger.info("Generated Scalac company config from built-in bundle")
            args.config = str(workspace / "scalac_config.json")
            # Save config for agents to reference
            config_save_path = Path(args.config)
            config_save_path.write_text(
                company_config.model_dump_json(indent=2), encoding="utf-8"
            )

    if args.documents:
        loaded = doc_loader.load_files([Path(f) for f in args.documents])
        documents.extend(loaded)
        logger.info("Loaded %d explicit documents", len(loaded))

    if args.documents_dir:
        loaded = doc_loader.load_directory(Path(args.documents_dir))
        documents.extend(loaded)
        logger.info("Loaded %d documents from %s", len(loaded), args.documents_dir)

    # Auto-load Scalac data bundle when running for Scalac
    if company_config.name and company_config.name.lower() == "scalac":
        scalac_data_dir = _resolve_template_dir().parent / "scalac_data"
        if scalac_data_dir.is_dir():
            loaded = doc_loader.load_directory(scalac_data_dir, doc_type="strategy")
            documents.extend(loaded)
            logger.info(
                "Loaded Scalac data bundle: %d documents from %s",
                len(loaded),
                scalac_data_dir,
            )
        else:
            logger.warning("Scalac data directory not found at %s", scalac_data_dir)

    if documents:
        logger.info("Total context documents: %d", len(documents))
        for d in documents:
            logger.debug("  - %s (%s, %d chars)", d.name, d.doc_type, len(d.content))

    # Platform adapter (auto-detected or explicit)
    adapter = _create_platform_adapter(args.platform)
    logger.info("Platform adapter: %s", adapter.get_name())

    # Initialize LLM provider
    provider = _create_provider(
        args.provider,
        args.model,
        getattr(args, "free_tier", False),
        api_key=getattr(args, "api_key", None),
    )

    # Create agents with optional document context
    from council.agents.base import BaseAgent
    from council.agents.marcus import MarcusAgent
    from council.agents.elena import ElenaAgent
    from council.agents.kai import KaiAgent
    from council.agents.david import DavidAgent
    from council.orchestration.orchestrator import AsyncOrchestrator

    agents: list[BaseAgent] = [
        MarcusAgent(workspace=workspace, config=company_config, provider=provider, documents=documents),
        ElenaAgent(workspace=workspace, config=company_config, provider=provider, documents=documents),
        KaiAgent(workspace=workspace, config=company_config, provider=provider, documents=documents),
        DavidAgent(workspace=workspace, config=company_config, provider=provider, documents=documents),
    ]

    async def _execute_council(progress_callback=None):
        orchestrator = AsyncOrchestrator(
            agents=agents,
            config=company_config,
            provider=provider,
            provider_name=args.provider,
            provider_model=args.model,
            max_rounds=args.rounds,
            round_timeout=args.timeout,
            workspace=workspace,
            progress_callback=progress_callback,
        )
        await adapter.spawn_agents(orchestrator)

        artifacts = orchestrator.write_artifacts(workspace / "output")
        _print_success_summary(workspace, args.rounds, artifacts)

    def _console_progress(agent_name: str, state: str, **kwargs) -> None:
        _AGENT_COLORS = {
            "Marcus": "cyan",
            "Elena": "magenta",
            "Kai": "green",
            "David": "yellow",
        }
        color = _AGENT_COLORS.get(agent_name, "white")
        if state == "generating":
            console.print(f"  [bold {color}]{agent_name}[/bold {color}] [dim]is thinking…[/dim]")
        elif state == "writing":
            progress = kwargs.get("progress_pct")
            pct = f" {progress:.0f}%" if progress is not None else ""
            console.print(f"  [bold {color}]{agent_name}[/bold {color}] drafting[pct]{pct}[/pct]")
        elif state == "done":
            console.print(f"  [bold green]✓[/bold green] [bold {color}]{agent_name}[/bold {color}] [green]done[/green]")
        elif state == "error":
            err = kwargs.get("message", kwargs.get("error", "unknown error"))
            console.print(f"  [bold red]✗[/bold red] [bold {color}]{agent_name}[/bold {color}] [red]error: {err}[/red]")
        elif state == "round_start":
            round_num = kwargs.get("round_num", "?")
            console.print()
            console.print(Rule(title=f"[bold blue]Round {round_num}/{args.rounds}[/bold blue]", style="blue"))

    await _execute_council(_console_progress)


def _create_provider(
    provider_name: str,
    model: Optional[str],
    free_tier: bool = False,
    api_key: Optional[str] = None,
) -> LLMProvider:
    """Create an LLM provider based on the name.

    Parameters
    ----------
    provider_name:
        One of the supported provider identifiers.
    model:
        Optional model name override.
    free_tier:
        Use the OpenRouter free-tier model fallback when True.
    api_key:
        API key passed directly via --api-key.  Forwarded to provider
        constructors that accept it; ignored for providers that don't
        use API keys (ollama, kimi-code, claude-code).
    """
    if provider_name == "openai":
        try:
            from council.llm.openai_provider import OpenAIProvider
        except ImportError as exc:
            raise ImportError(
                "OpenAI package not installed.\n"
                "  Fix: pip install openai\n"
                "  Then: export OPENAI_API_KEY=sk-..."
            ) from exc
        try:
            return OpenAIProvider(model=model or "gpt-4o", api_key=api_key)
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize OpenAI provider: {exc}\n"
                "  Check that OPENAI_API_KEY is set and valid."
            ) from exc
    elif provider_name == "anthropic":
        try:
            from council.llm.anthropic_provider import AnthropicProvider
        except ImportError as exc:
            raise ImportError(
                "Anthropic package not installed.\n"
                "  Fix: pip install anthropic\n"
                "  Then: export ANTHROPIC_API_KEY=sk-ant-..."
            ) from exc
        try:
            return AnthropicProvider(model=model or "claude-sonnet-4-6", api_key=api_key)
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize Anthropic provider: {exc}\n"
                "  Check that ANTHROPIC_API_KEY is set and valid."
            ) from exc
    elif provider_name == "openrouter":
        try:
            from council.llm.openrouter_provider import OpenRouterProvider
        except ImportError as exc:
            raise ImportError(
                "OpenAI package not installed (needed for OpenRouter).\n"
                "  Fix: pip install openai\n"
                "  Then: export OPENROUTER_API_KEY=sk-or-..."
            ) from exc
        try:
            return OpenRouterProvider(
                model=model or "anthropic/claude-sonnet-4",
                free_tier=free_tier,
                api_key=api_key,
            )
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize OpenRouter provider: {exc}\n"
                "  Check that OPENROUTER_API_KEY is set and valid."
            ) from exc
    elif provider_name == "ollama":
        try:
            from council.llm.ollama_provider import OllamaProvider
        except ImportError as exc:
            raise ImportError(
                "aiohttp not installed (needed for Ollama).\n"
                "  Fix: pip install aiohttp\n"
                "  Also ensure Ollama is running: ollama serve"
            ) from exc
        try:
            # Ollama connects to localhost — no API key is used.
            return OllamaProvider(model=model or "llama3")
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize Ollama provider: {exc}\n"
                "  Check that Ollama is running (ollama serve) and the model is pulled."
            ) from exc
    elif provider_name == "kimi-code":
        from council.llm.kimi_code_provider import KimiCodeProvider
        try:
            # Kimi Code uses subprocess/session — no API key is used.
            return KimiCodeProvider(model=model or "kimi-for-coding")
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize Kimi Code provider: {exc}\n"
                "  Make sure you are running inside the Kimi Code IDE,\n"
                "  or that ~/.kimi/credentials/kimi-code.json exists."
            ) from exc
    elif provider_name == "claude-code":
        from council.llm.claude_code_provider import ClaudeCodeProvider
        try:
            # Claude Code uses the local 'claude' CLI — no API key is used.
            return ClaudeCodeProvider(model=model or "claude-sonnet-4-6")
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize Claude Code provider: {exc}\n"
                "  Make sure you are running inside Claude Code IDE,\n"
                "  or that the 'claude' CLI is installed (npm install -g @anthropic-ai/claude-code),\n"
                "  or that ~/.claude/.credentials.json exists."
            ) from exc
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def _print_success_summary(workspace: Path, rounds: int, artifacts: dict) -> None:
    """Print a rich, human-friendly summary of what was generated."""
    output_dir = workspace / "output"
    discussion_dir = workspace / "shared" / "discussion"

    round_files = list(discussion_dir.glob("*_round_*.md")) if discussion_dir.exists() else []
    proposal_path: Optional[Path] = artifacts.get("proposal")

    table = Table(title="Council Run Complete", show_header=False, border_style="green")
    table.add_column("Key", style="bold cyan", width=16)
    table.add_column("Value", style="white")
    table.add_row("Rounds", str(rounds))
    table.add_row("Output dir", str(workspace))
    table.add_row("Round files", f"{len(round_files)} files")
    if proposal_path and proposal_path.exists():
        table.add_row("Proposal", str(proposal_path))
        table.add_row("Manifest", str(artifacts.get("manifest", "")))

    console.print()
    console.print(table)

    if proposal_path and proposal_path.exists():
        preview_lines = proposal_path.read_text(encoding="utf-8").splitlines()[:20]
        console.print()
        console.print(Panel(
            "\n".join(preview_lines) + ("\n…" if len(proposal_path.read_text(encoding="utf-8").splitlines()) > 20 else ""),
            title="[bold green]Proposal preview[/bold green]",
            border_style="green",
        ))

    tips = Table(show_header=False, border_style="dim")
    tips.add_column(style="bold yellow")
    tips.add_column(style="dim")
    if proposal_path and proposal_path.exists():
        tips.add_row("• View proposal", f"cat {proposal_path}")
        tips.add_row("• Review run", f"python -m council --review {workspace}")
    tips.add_row("• Check discussion", f"ls {discussion_dir}")
    tips.add_row("• Run again", "python -m council --config ...")
    console.print(tips)


def _review_run(workspace: Path) -> None:
    """Display a summary of a previous council run from its manifest."""
    import json as _json

    manifest_path = workspace / "output" / "manifest.json"
    if not manifest_path.exists():
        console.print(Panel(
            f"[red]No manifest found in {workspace / 'output'}[/red]\n"
            "Run the council first to generate artifacts.",
            title="Review",
            border_style="red",
        ))
        return

    manifest = _json.loads(manifest_path.read_text(encoding="utf-8"))

    table = Table(title="Previous Run", show_header=False, border_style="blue")
    table.add_column("Key", style="bold cyan", width=20)
    table.add_column("Value", style="white")
    table.add_row("Generated", manifest.get("generated_at", "unknown"))
    table.add_row("Company", manifest.get("company", "unknown"))
    table.add_row("Product", manifest.get("product", "unknown"))
    table.add_row("Provider", f"{manifest.get('provider', '?')} / {manifest.get('model', '?')}")
    table.add_row("Rounds completed", f"{manifest.get('rounds_completed', '?')} / {manifest.get('max_rounds', '?')}")
    table.add_row("Agents", ", ".join(manifest.get("agents", [])))

    files = manifest.get("files", {})
    proposal_path = Path(files.get("proposal", ""))
    if proposal_path.exists():
        table.add_row("Proposal", str(proposal_path))

    console.print()
    console.print(table)

    if proposal_path.exists():
        preview_lines = proposal_path.read_text(encoding="utf-8").splitlines()[:20]
        console.print()
        console.print(Panel(
            "\n".join(preview_lines) + "\n…",
            title="[bold blue]Proposal preview[/bold blue]",
            border_style="blue",
        ))


def _show_status(workspace: Path) -> None:
    """Display current discussion status."""
    discussion_dir = workspace / "shared" / "discussion"
    if not discussion_dir.exists():
        console.print(Panel("[dim]No discussion found.[/dim]", title="Status", border_style="yellow"))
        return

    files = sorted(discussion_dir.glob("*_round_*.md"))
    if not files:
        console.print(Panel("[dim]No round files found.[/dim]", title="Status", border_style="yellow"))
        return

    table = Table(title=f"Discussion in {discussion_dir}", border_style="blue")
    table.add_column("File", style="cyan")
    table.add_column("Size", justify="right", style="dim")
    for f in files:
        size = f.stat().st_size
        table.add_row(f.name, f"{size:,} bytes")
    console.print(table)


def _run_async_in_thread(coro) -> Exception:
    """Run an async coroutine in a new event loop inside the current thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coro)
    except Exception as exc:
        return exc
    finally:
        loop.close()
    return None


def main() -> None:
    """CLI entry point for the Universal AI Marketing Council."""
    argv = sys.argv[1:]
    interactive_requested = "--interactive" in argv or "-i" in argv
    onboarding_requested = "--onboarding" in argv
    wants_help = "--help" in argv or "-h" in argv

    if (not argv or interactive_requested or onboarding_requested) and not wants_help:
        from council.interactive import prompt_for_args

        args = prompt_for_args(force_onboarding=onboarding_requested)
    else:
        args = parse_args()

    dashboard = None
    if args.dashboard:
        try:
            from council.vis.dashboard import CouncilDashboard
        except ImportError as exc:
            logger.warning("Dashboard requires 'textual'. Install: pip install textual (%s)", exc)
        else:
            dashboard = CouncilDashboard(
                agent_names=["Marcus", "Elena", "Kai", "David"],
                max_rounds=args.rounds,
                workspace=Path(args.output),
            )

    if dashboard:
        import threading

        council_exception: Optional[Exception] = None

        def _council_thread() -> None:
            nonlocal council_exception
            exc = _run_async_in_thread(_run_council(args, dashboard))
            if exc:
                council_exception = exc
                dashboard.stop()
            else:
                # Notify user that work is done; they can browse files and press q to exit
                dashboard.log("✓ Council run complete — browse files and press q to exit")

        thread = threading.Thread(target=_council_thread, daemon=True)
        thread.start()
        dashboard.run()  # blocks in main thread (Textual requirement)
        thread.join(timeout=60.0)
        # Issue #19: exit with an error if the council thread is still running
        # after the dashboard has closed.
        if thread.is_alive():
            logger.error(
                "Council thread did not finish within 60 seconds after dashboard closed."
            )
            sys.exit(1)
        if council_exception:
            _handle_error(council_exception)
            sys.exit(1)
        return

    try:
        asyncio.run(_run_council(args))
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user. Partial results may be in the workspace.[/yellow]")
        sys.exit(130)
    except FileNotFoundError as exc:
        console.print()
        console.print(Panel(f"[bold red]File not found[/bold red]\n{exc}", border_style="red"))
        sys.exit(1)
    except ImportError as exc:
        console.print()
        console.print(Panel(f"[bold red]Missing dependency[/bold red]\n{exc}", border_style="red"))
        sys.exit(1)
    except RuntimeError as exc:
        console.print()
        console.print(Panel(f"[bold red]{exc}[/bold red]", border_style="red"))
        console.print()
        console.print("[bold]Need help?[/bold]")
        console.print("  • Demo mode (no API keys):  [cyan]python -m council --demo[/cyan]")
        console.print("  • Interactive menu:         [cyan]python -m council[/cyan]")
        console.print("  • Full help:                [cyan]python -m council --help[/cyan]")
        sys.exit(1)
    except Exception as exc:
        console.print()
        console.print(Panel(f"[bold red]Council execution failed[/bold red]\n{exc}", border_style="red"))
        console.print()
        console.print("[dim]If this looks like a bug, run with --verbose and file an issue.[/dim]")
        sys.exit(1)


def _handle_error(exc: Exception) -> None:
    """Print a human-friendly error message."""
    if isinstance(exc, FileNotFoundError):
        console.print(Panel(f"[bold red]File not found[/bold red]\n{exc}", border_style="red"))
    elif isinstance(exc, ImportError):
        console.print(Panel(f"[bold red]Missing dependency[/bold red]\n{exc}", border_style="red"))
    elif isinstance(exc, RuntimeError):
        console.print(Panel(f"[bold red]{exc}[/bold red]", border_style="red"))
        console.print()
        console.print("[bold]Need help?[/bold]")
        console.print("  • Demo mode (no API keys):  [cyan]python -m council --demo[/cyan]")
        console.print("  • Interactive menu:         [cyan]python -m council[/cyan]")
        console.print("  • Full help:                [cyan]python -m council --help[/cyan]")
    else:
        console.print(Panel(f"[bold red]Council execution failed[/bold red]\n{exc}", border_style="red"))
        console.print("[dim]If this looks like a bug, run with --verbose and file an issue.[/dim]")


if __name__ == "__main__":
    main()
