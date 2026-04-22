from __future__ import annotations

import argparse
import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Optional

from council.config.loader import ConfigLoader
from council.cli import _create_provider

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a single council agent in a Kimi Code session."
    )
    parser.add_argument("--name", required=True, help="Agent name (Marcus, Elena, Kai, David)")
    parser.add_argument("--workspace", required=True, help="Workspace directory")
    parser.add_argument("--rounds", type=int, default=3, help="Maximum number of rounds")
    return parser.parse_args()


def _reconstruct_agent(
    agent_name: str,
    workspace: Path,
    provider_name: str,
    provider_model: Optional[str],
) -> Any:
    from council.agents.base import BaseAgent

    config_path = workspace / "config.json"
    if not config_path.exists():
        logger.error("Config file not found in workspace: %s", config_path)
        return None

    from council.config.loader import ConfigLoader
    from council.cli import _create_provider

    company_config = ConfigLoader.from_json(config_path)
    provider = _create_provider(provider_name, provider_model)

    agent_class_name = f"{agent_name}Agent"
    module_name = agent_name.lower()
    module = __import__(f"council.agents.{module_name}", fromlist=[agent_class_name])
    agent_class = getattr(module, agent_class_name)

    return agent_class(
        workspace=workspace,
        config=company_config,
        provider=provider,
    )


async def main() -> None:
    args = parse_args()
    workspace = Path(args.workspace)

    provider_name = os.environ.get("COUNCIL_PROVIDER", "openai")
    provider_model = os.environ.get("COUNCIL_PROVIDER_MODEL") or None

    logger.info(
        "Kimi agent runner starting %s with provider=%s model=%s",
        args.name,
        provider_name,
        provider_model,
    )

    agent = _reconstruct_agent(args.name, workspace, provider_name, provider_model)
    if agent is None:
        raise SystemExit(1)

    for round_num in range(1, args.rounds + 1):
        try:
            await agent.run_round(round_num)
        except Exception as exc:
            logger.error("Agent %s failed in round %d: %s", args.name, round_num, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Kimi agent runner interrupted by user.")
