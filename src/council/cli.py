from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from council.config.loader import ConfigLoader
from council.llm.provider import LLMProvider
from council.platform.base import PlatformAdapter

logger = logging.getLogger(__name__)

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

    parser = argparse.ArgumentParser(
        description="Universal AI Marketing Council v3.2 — 4 AI agents debate and create a marketing plan for your company.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Platform auto-detection: {{ {auto_msg} }}

Quick start (pick one):
  First time here?          python -m council
  See it in action (no keys) python -m council --demo --dashboard
  Run with your company      python -m council --config firm.json
  Use Claude Code IDE        python -m council --config firm.json --provider claude-code
  Use Kimi Code IDE          python -m council --config firm.json --provider kimi-code

Common operations:
  More debate rounds         python -m council --config firm.json --rounds 5
  Live terminal dashboard    python -m council --config firm.json --dashboard
  Aggregate final proposal   python -m council --config firm.json --aggregate
  Only check status          python -m council --config firm.json --monitor

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
        choices=["openai", "anthropic", "ollama", "kimi-code", "claude-code"],
        help="LLM provider to use (default: openai)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name override",
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
        help="Aggregate final outputs into a single proposal",
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
        "--scalac-mode",
        action="store_true",
        help="Load built-in Scalac context bundle (no config needed)",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Show real-time live dashboard with agent panels (requires 'rich')",
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
    return parser.parse_args(args)


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

    if args.demo:
        await _run_demo(args, dashboard)
        return

    if not args.config:
        logger.error(
            "Missing --config. You have three options:\n"
            "  1. Run demo (no config needed):  python -m council --demo\n"
            "  2. Create a config from template: cp templates/companies/saas.json my.json\n"
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

    if args.monitor:
        _show_status(workspace)
        return

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

    if documents:
        logger.info("Total context documents: %d", len(documents))
        for d in documents:
            logger.debug("  - %s (%s, %d chars)", d.name, d.doc_type, len(d.content))
    
    # Platform adapter (auto-detected or explicit)
    adapter = _create_platform_adapter(args.platform)
    logger.info("Platform adapter: %s", adapter.get_name())

    # Initialize LLM provider
    provider = _create_provider(args.provider, args.model)

    # Create agents with optional document context
    from council.agents.base import BaseAgent
    from council.agents.marcus import MarcusAgent
    from council.agents.elena import ElenaAgent
    from council.agents.kai import KaiAgent
    from council.agents.david import DavidAgent
    from council.orchestration.orchestrator import AsyncOrchestrator

    agents: list[BaseAgent] = [
        MarcusAgent(workspace=workspace, config=company_config, provider=provider),
        ElenaAgent(workspace=workspace, config=company_config, provider=provider),
        KaiAgent(workspace=workspace, config=company_config, provider=provider),
        DavidAgent(workspace=workspace, config=company_config, provider=provider),
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

        if args.aggregate:
            proposal = orchestrator.aggregate_proposal()
            proposal_path = workspace / "FINAL_PROPOSAL.md"
            proposal_path.write_text(proposal, encoding="utf-8")
            logger.info("Aggregated proposal written to %s", proposal_path)

        _print_success_summary(workspace, args.rounds, args.aggregate)

    def _console_progress(agent_name: str, state: str, **kwargs) -> None:
        if state == "generating":
            print(f"  {agent_name} is thinking …")
        elif state == "writing":
            progress = kwargs.get("progress_pct")
            pct = f" {progress:.0f}%" if progress is not None else ""
            print(f"  {agent_name} drafting{pct}")
        elif state == "done":
            print(f"  ✓ {agent_name} done")
        elif state == "error":
            err = kwargs.get("message", kwargs.get("error", "unknown error"))
            print(f"  ✗ {agent_name} error: {err}")
        elif state == "round_start":
            round_num = kwargs.get("round_num", "?")
            print(f"\n── Round {round_num}/{args.rounds} ──")

    await _execute_council(_console_progress)


def _create_provider(provider_name: str, model: Optional[str]) -> LLMProvider:
    """Create an LLM provider based on the name."""
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
            return OpenAIProvider(model=model or "gpt-4o")
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
            return AnthropicProvider(model=model or "claude-sonnet-4-6")
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize Anthropic provider: {exc}\n"
                "  Check that ANTHROPIC_API_KEY is set and valid."
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
            return OllamaProvider(model=model or "llama3")
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize Ollama provider: {exc}\n"
                "  Check that Ollama is running (ollama serve) and the model is pulled."
            ) from exc
    elif provider_name == "kimi-code":
        from council.llm.kimi_code_provider import KimiCodeProvider
        try:
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


def _print_success_summary(workspace: Path, rounds: int, aggregated: bool) -> None:
    """Print a human-friendly summary of what was generated."""
    output_dir = workspace / "output"
    discussion_dir = workspace / "shared" / "discussion"

    output_files = list(output_dir.glob("*.md")) if output_dir.exists() else []
    round_files = list(discussion_dir.glob("*_round_*.md")) if discussion_dir.exists() else []

    print()
    print("=" * 50)
    print("✓  Council run complete")
    print("=" * 50)
    print(f"  Rounds:        {rounds}")
    print(f"  Output dir:    {workspace}")
    print(f"  Agent outputs: {len(output_files)} files")
    print(f"  Round files:   {len(round_files)} files")

    if aggregated and (workspace / "FINAL_PROPOSAL.md").exists():
        print(f"  Proposal:      {workspace / 'FINAL_PROPOSAL.md'}")

    print()
    print("What to do next:")
    if output_files:
        print(f"  • Read agent outputs:  ls {output_dir}")
    if (workspace / "FINAL_PROPOSAL.md").exists():
        print(f"  • View proposal:       cat {workspace / 'FINAL_PROPOSAL.md'}")
    print(f"  • Check discussion:    ls {discussion_dir}")
    print(f"  • Run again:           python -m council --config ...")
    print("=" * 50)


def _show_status(workspace: Path) -> None:
    """Display current discussion status."""
    discussion_dir = workspace / "shared" / "discussion"
    if not discussion_dir.exists():
        print("No discussion found.")
        return

    files = sorted(discussion_dir.glob("*_round_*.md"))
    if not files:
        print("No round files found.")
        return

    print(f"Discussion status in {discussion_dir}:")
    print(f"  Files: {len(files)}")
    for f in files:
        size = f.stat().st_size
        print(f"  - {f.name} ({size} bytes)")


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

        thread = threading.Thread(target=_council_thread, daemon=True)
        thread.start()
        dashboard.run()  # blocks in main thread (Textual requirement)
        thread.join(timeout=60.0)
        if council_exception:
            _handle_error(council_exception)
            sys.exit(1)
        return

    try:
        asyncio.run(_run_council(args))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Partial results may be in the workspace.")
        sys.exit(130)
    except FileNotFoundError as exc:
        print()
        print(f"✗  File not found: {exc}")
        sys.exit(1)
    except ImportError as exc:
        print()
        print(f"✗  Missing dependency\n\n{exc}")
        sys.exit(1)
    except RuntimeError as exc:
        print()
        print(f"✗  {exc}")
        print()
        print("Need help?")
        print("  • Demo mode (no API keys):  python -m council --demo")
        print("  • Interactive menu:         python -m council")
        print("  • Full help:                python -m council --help")
        sys.exit(1)
    except Exception as exc:
        print()
        print(f"✗  Council execution failed: {exc}")
        print()
        print("If this looks like a bug, run with --verbose and file an issue.")
        sys.exit(1)


def _handle_error(exc: Exception) -> None:
    """Print a human-friendly error message."""
    if isinstance(exc, FileNotFoundError):
        print()
        print(f"✗  File not found: {exc}")
    elif isinstance(exc, ImportError):
        print()
        print(f"✗  Missing dependency\n\n{exc}")
    elif isinstance(exc, RuntimeError):
        print()
        print(f"✗  {exc}")
        print()
        print("Need help?")
        print("  • Demo mode (no API keys):  python -m council --demo")
        print("  • Interactive menu:         python -m council")
        print("  • Full help:                python -m council --help")
    else:
        print()
        print(f"✗  Council execution failed: {exc}")
        print()
        print("If this looks like a bug, run with --verbose and file an issue.")


if __name__ == "__main__":
    main()
