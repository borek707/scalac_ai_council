from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from council.platform.base import PlatformAdapter

if TYPE_CHECKING:
    from council.agents.base import BaseAgent
    from council.orchestration.orchestrator import AsyncOrchestrator

logger = logging.getLogger(__name__)


class KimiAdapter(PlatformAdapter):
    """Kimi Code platform adapter.

    Kimi Code is an AI-powered IDE with ``sessions_spawn`` API
    that allows launching parallel agent processes. This adapter
    integrates with that API for true parallel execution.

    Environment detection:
        - Kimi sets ``KIMI_SESSION_ID`` or ``KIMI_API_KEY`` env vars
        - Sessions API available via ``kimi.sessions_spawn()``

    Usage::

        # In Kimi Code terminal
        python -m council --config firm.json --platform kimi

        # Or let it auto-detect
        python -m council --config firm.json

    Parallel execution:
        Kimi Code supports true process-level parallelism via
        ``sessions_spawn``. Each agent runs in its own session
        with isolated filesystem, coordinated via the shared
        ``output/`` directory.

    Reference:
        - https://kimi.moonshot.cn
        - Kimi Code API docs (internal)
    """

    def __init__(self, session: Optional[Any] = None) -> None:
        self.session = session
        self._kimi_detected = self._detect_kimi()

    def get_name(self) -> str:
        return "Kimi Code"

    def _detect_kimi(self) -> bool:
        """Detect if running inside Kimi Code environment."""
        kimi_markers = [
            "KIMI_SESSION_ID",
            "KIMI_API_KEY",
            "KIMI_CODE_ENV",
            "KIMI_WORKSPACE",
        ]
        return any(os.environ.get(m) for m in kimi_markers)

    @property
    def is_available(self) -> bool:
        """Whether the current environment is Kimi Code."""
        return self._kimi_detected

    async def spawn_agents(self, orchestrator: AsyncOrchestrator) -> None:
        """Run agents via Kimi Code sessions_spawn API.

        If ``sessions_spawn`` is available, each agent gets its own
        parallel session. Otherwise falls back to asyncio within
        the current session.
        """
        if not self._kimi_detected:
            logger.warning(
                "KimiAdapter: Kimi Code environment not detected, "
                "falling back to standard asyncio execution"
            )
            await orchestrator.run()
            return

        # Try sessions_spawn for true parallelism
        if self._has_sessions_spawn():
            logger.info(
                "Running via Kimi Code sessions_spawn (parallel sessions)"
            )
            await self._spawn_via_sessions(orchestrator)
        else:
            logger.info(
                "Running via Kimi Code (asyncio fallback in single session)"
            )
            await orchestrator.run()

    def _has_sessions_spawn(self) -> bool:
        """Check if sessions_spawn API is available."""
        if self.session is not None:
            return hasattr(self.session, "sessions_spawn")
        # Try importing Kimi Code internal module
        try:
            import kimi  # type: ignore[import-untyped]
            return hasattr(kimi, "sessions_spawn")
        except ImportError:
            return False

    async def _spawn_via_sessions(self, orchestrator: AsyncOrchestrator) -> None:
        """Spawn each agent in its own Kimi session."""
        from council.agents.base import BaseAgent

        agents: list[BaseAgent] = orchestrator.agents
        workspace = orchestrator.workspace

        # Build spawn commands for each agent
        spawn_commands = []
        for agent in agents:
            cmd = (
                f"python -m council.agent_runner "
                f"--name {agent.name} "
                f"--workspace {workspace} "
                f"--rounds {orchestrator.max_rounds}"
            )
            spawn_commands.append({
                "name": f"council-{agent.name.lower()}",
                "command": cmd,
                "env": {
                    "COUNCIL_AGENT_NAME": agent.name,
                    "COUNCIL_WORKSPACE": str(workspace),
                    "COUNCIL_MAX_ROUNDS": str(orchestrator.max_rounds),
                },
            })

        logger.info(
            "Spawning %d parallel agent sessions via Kimi",
            len(spawn_commands),
        )

        try:
            if self.session is not None:
                self.session.sessions_spawn(spawn_commands)
            else:
                import kimi  # type: ignore[import-untyped]
                kimi.sessions_spawn(spawn_commands)

            # Wait for all agents to complete via barrier
            for round_num in range(1, orchestrator.max_rounds + 1):
                await orchestrator.barrier.wait(round_num)

        except Exception as exc:
            logger.warning(
                "sessions_spawn failed (%s), falling back to asyncio",
                exc,
            )
            await orchestrator.run()

    async def _spawn_single_agent(
        self,
        agent_name: str,
        workspace: Path,
        max_rounds: int,
    ) -> None:
        """Run a single agent in its own session (called by sessions_spawn)."""
        logger.info("Agent %s started in own session", agent_name)

        # Reconstruct the agent from environment
        # This is the entry point for spawned sessions
        agent = self._reconstruct_agent(agent_name, workspace)
        if agent is None:
            logger.error("Failed to reconstruct agent: %s", agent_name)
            return

        for round_num in range(1, max_rounds + 1):
            try:
                await agent.run_round(round_num)
            except Exception as exc:
                logger.error(
                    "Agent %s round %d failed: %s",
                    agent_name,
                    round_num,
                    exc,
                )

    def _reconstruct_agent(
        self,
        agent_name: str,
        workspace: Path,
    ) -> Any:
        """Reconstruct an agent instance in a spawned session.

        Reads configuration from the workspace to rebuild the agent.
        """
        import json

        config_path = workspace / "config.json"
        if not config_path.exists():
            logger.error("Config not found in workspace: %s", config_path)
            return None

        from council.config.loader import ConfigLoader
        from council.llm.openai_provider import OpenAIProvider

        company_config = ConfigLoader.from_json(config_path)
        provider = OpenAIProvider()

        # Import agent classes dynamically
        agent_class_name = f"{agent_name}Agent"
        module_name = agent_name.lower()
        module = __import__(
            f"council.agents.{module_name}",
            fromlist=[agent_class_name],
        )
        agent_class = getattr(module, agent_class_name)

        return agent_class(
            workspace=workspace,
            config=company_config,
            provider=provider,
        )
