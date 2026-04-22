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
        description="Universal AI Marketing Council v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Platform auto-detection: {{ {auto_msg} }}

Examples:
  python -m council --config firm.json
  python -m council --config firm.json --platform kimi
  python -m council --config firm.json --provider anthropic --rounds 5
  python -m council --config firm.json --output ./results --monitor

Supported platforms:
  cli       Local terminal (default)
  kimi      Kimi Code IDE (sessions_spawn)
  idx       Google IDX / Project IDX
  cursor    Cursor AI IDE
  copilot   GitHub Copilot / Codespaces
  web       Bolt.new / Lovable.dev / Replit
        """,
    )
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="Path to company JSON config file",
    )
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "anthropic", "ollama", "kimi-code"],
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


async def _run_council(args: argparse.Namespace) -> None:
    """Execute the council with parsed arguments."""
    setup_logging(args.verbose)

    config_path = Path(args.config)
    if not config_path.exists():
        logger.error("Config file not found: %s", config_path)
        sys.exit(1)

    logger.info("Loading configuration from %s", config_path)
    company_config = ConfigLoader.from_json(config_path)
    logger.info(
        "Loaded config for company: %s (%s)",
        company_config.name,
        company_config.product,
    )

    workspace = Path(args.output)
    workspace.mkdir(parents=True, exist_ok=True)

    config_save_path = workspace / "config.json"
    config_save_path.write_text(
        company_config.model_dump_json(indent=2),
        encoding="utf-8",
    )
    logger.info("Saved runtime company config to %s", config_save_path)

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

    orchestrator = AsyncOrchestrator(
        agents=agents,
        config=company_config,
        provider=provider,
        provider_name=args.provider,
        provider_model=args.model,
        max_rounds=args.rounds,
        round_timeout=args.timeout,
        workspace=workspace,
    )

    await adapter.spawn_agents(orchestrator)

    if args.aggregate:
        proposal = orchestrator.aggregate_proposal()
        proposal_path = workspace / "FINAL_PROPOSAL.md"
        proposal_path.write_text(proposal, encoding="utf-8")
        logger.info("Aggregated proposal written to %s", proposal_path)

    logger.info("Council run complete.")


def _create_provider(provider_name: str, model: Optional[str]) -> LLMProvider:
    """Create an LLM provider based on the name."""
    if provider_name == "openai":
        try:
            from council.llm.openai_provider import OpenAIProvider
        except ImportError as exc:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            ) from exc
        return OpenAIProvider(model=model or "gpt-4o")
    elif provider_name == "anthropic":
        try:
            from council.llm.anthropic_provider import AnthropicProvider
        except ImportError as exc:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            ) from exc
        return AnthropicProvider(model=model or "claude-sonnet-4-6")
    elif provider_name == "ollama":
        try:
            from council.llm.ollama_provider import OllamaProvider
        except ImportError as exc:
            raise ImportError(
                "aiohttp not installed. Install with: pip install aiohttp"
            ) from exc
        return OllamaProvider(model=model or "llama3")
    elif provider_name == "kimi-code":
        from council.llm.kimi_code_provider import KimiCodeProvider
        return KimiCodeProvider(model=model or "kimi-for-coding")
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def _show_status(workspace: Path) -> None:
    """Display current discussion status."""
    discussion_dir = workspace / "shared" / "discussion"
    if not discussion_dir.exists():
        print("No discussion found.")
        return

    files = sorted(discussion_dir.glob("round_*_*.md"))
    if not files:
        print("No round files found.")
        return

    print(f"Discussion status in {discussion_dir}:")
    print(f"  Files: {len(files)}")
    for f in files:
        size = f.stat().st_size
        print(f"  - {f.name} ({size} bytes)")


def main() -> None:
    """CLI entry point for the Universal AI Marketing Council."""
    args = parse_args()
    try:
        asyncio.run(_run_council(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        sys.exit(130)
    except Exception as exc:
        logger.error("Council execution failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
