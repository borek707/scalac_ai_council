from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from council.platform.base import PlatformAdapter

if TYPE_CHECKING:
    from council.orchestration.orchestrator import AsyncOrchestrator

logger = logging.getLogger(__name__)


class WebPlatformAdapter(PlatformAdapter):
    """Adapter for web-based AI platforms (Bolt.new, Lovable, Replit).

    These platforms run Python in browser containers or VMs.
    This adapter detects the environment and configures execution
    accordingly.

    Supported platforms:
        - **Bolt.new** — Full-stack web IDE with AI
        - **Lovable.dev** — AI-powered app builder
        - **Replit Agent** — Cloud IDE with AI agent
        - **StackBlitz** — Web containers

    Environment detection:
        - Bolt: ``BOLT_ENV``, ``BOLT_PROJECT_ID``
        - Lovable: ``LOVABLE_ENV``, ``LOVABLE_PROJECT_ID``
        - Replit: ``REPL_ID``, ``REPL_OWNER``, ``REPL_SLUG``
        - StackBlitz: ``WEBCONTAINER``

    Usage::

        # Detected automatically on supported platforms
        python -m council --config firm.json --platform web

    Note:
        Web platforms may have file system restrictions.
        Output is written to the workspace if writable,
        otherwise to ``/tmp/council_output/``.
    """

    PLATFORM_NAMES = {
        "BOLT_ENV": "Bolt.new",
        "BOLT_PROJECT_ID": "Bolt.new",
        "LOVABLE_ENV": "Lovable.dev",
        "LOVABLE_PROJECT_ID": "Lovable.dev",
        "REPL_ID": "Replit",
        "REPL_OWNER": "Replit",
        "WEBCONTAINER": "StackBlitz",
    }

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self._detected_platform = self._detect_platform()
        self.workspace_root = self._resolve_workspace(workspace_root)

    def get_name(self) -> str:
        if self._detected_platform:
            return self._detected_platform
        return "Web Platform (generic)"

    def _detect_platform(self) -> Optional[str]:
        """Auto-detect which web platform we're running on."""
        for env_var, platform_name in self.PLATFORM_NAMES.items():
            if os.environ.get(env_var):
                return platform_name
        return None

    def _resolve_workspace(self, workspace_root: Optional[str]) -> Path:
        """Find a writable directory for output."""
        if workspace_root:
            return Path(workspace_root)

        # Try common writable paths on web platforms
        candidates = [
            Path.home() / "workspace",
            Path("/home/user"),
            Path("/tmp"),
            Path.cwd(),
        ]
        for candidate in candidates:
            try:
                candidate.mkdir(parents=True, exist_ok=True)
                test_file = candidate / ".write_test"
                test_file.write_text("ok")
                test_file.unlink()
                return candidate
            except OSError:
                continue

        return Path.cwd()

    @property
    def is_available(self) -> bool:
        """Whether a known web platform is detected."""
        return self._detected_platform is not None

    async def spawn_agents(self, orchestrator: AsyncOrchestrator) -> None:
        """Run agents in the web platform environment.

        Web containers may have limited resources, so we run
        agents sequentially rather than in parallel.
        """
        if self._detected_platform:
            logger.info(
                "Running via %s adapter (workspace: %s)",
                self._detected_platform,
                self.workspace_root,
            )
        else:
            logger.warning(
                "WebPlatformAdapter: No known web platform detected, "
                "using generic web container mode"
            )

        # On web platforms, check if we have enough resources
        # for parallel execution; fall back to sequential if not
        try:
            import asyncio
            # Test: can we create multiple tasks?
            await asyncio.wait_for(
                self._test_parallelism(), timeout=5.0
            )
            logger.info("Parallel execution available")
            await orchestrator.run()
        except Exception:
            logger.warning(
                "Limited resources detected — running agents sequentially"
            )
            await self._run_sequential(orchestrator)

    async def _test_parallelism(self) -> None:
        """Quick test if parallel asyncio tasks work."""
        import asyncio

        async def dummy() -> str:
            await asyncio.sleep(0.1)
            return "ok"

        results = await asyncio.gather(dummy(), dummy(), dummy())
        assert all(r == "ok" for r in results)

    async def _run_sequential(self, orchestrator: AsyncOrchestrator) -> None:
        """Fallback: run one agent at a time."""
        for agent in orchestrator.agents:
            logger.info("Running agent: %s", agent.name)
            for round_num in range(1, orchestrator.max_rounds + 1):
                await agent.run_round(round_num)
                await orchestrator.barrier.wait(round_num)
