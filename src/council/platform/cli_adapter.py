from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from council.platform.base import PlatformAdapter

if TYPE_CHECKING:
    from council.orchestration.orchestrator import AsyncOrchestrator

logger = logging.getLogger(__name__)


class CLIAdapter(PlatformAdapter):
    """Default platform adapter — runs agents locally via asyncio.

    This is the standard adapter for running the council from
    the command line on any machine with Python installed.
    """

    def get_name(self) -> str:
        return "CLI"

    async def spawn_agents(self, orchestrator: AsyncOrchestrator) -> None:
        """Run the orchestrator directly in the local asyncio event loop."""
        logger.info("Running via CLI adapter")
        await orchestrator.run()
