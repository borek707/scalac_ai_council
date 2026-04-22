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
        choices=["openai", "anthropic", "ollama"],
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

    if args.monitor:
        _show_status(workspace)
        return

    # Platform adapter (auto-detected or explicit)
    adapter = _create_platform_adapter(args.platform)
    logger.info("Platform adapter: %s", adapter.get_name())

    # Initialize LLM provider
    provider = _create_provider(args.provider, args.model)

    # Create agents
    from council.agents.base import BaseAgent
    from council.agents.marcus import MarcusAgent
    from council.agents.elena import ElenaAgent
    from council.agents.kai import KaiAgent
    from council.agents.david import DavidAgent

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
        return AnthropicProvider(model=model or "claude-3-sonnet-20240229")
    elif provider_name == "ollama":
        try:
            from council.llm.ollama_provider import OllamaProvider
        except ImportError as exc:
            raise ImportError(
                "aiohttp not installed. Install with: pip install aiohttp"
            ) from exc
        return OllamaProvider(model=model or "llama3")
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
