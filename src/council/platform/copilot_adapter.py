from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from council.platform.base import PlatformAdapter

if TYPE_CHECKING:
    from council.orchestration.orchestrator import AsyncOrchestrator

logger = logging.getLogger(__name__)


class GitHubCopilotAdapter(PlatformAdapter):
    """GitHub Copilot Workspace platform adapter.

    GitHub Copilot provides AI assistance within VS Code, JetBrains,
    and Neovim. This adapter runs the council in Copilot's terminal
    or via GitHub Codespaces.

    Environment detection:
        - GitHub Codespaces sets ``CODESPACES`` env var
        - Copilot sets ``GITHUB_COPILOT`` and ``COPILOT_AGENT"`` vars
        - Codespaces have full Linux environment

    Usage::

        # In GitHub Codespaces terminal
        python -m council --config firm.json --platform copilot

        # Or with Copilot CLI
        gh copilot suggest "run marketing council for my company"

    Reference:
        - https://github.com/features/copilot
        - https://github.com/features/codespaces
    """

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self._codespaces = os.environ.get("CODESPACES") == "true"
        self._copilot = any(
            os.environ.get(v)
            for v in ["GITHUB_COPILOT", "COPILOT_AGENT", "COPILOT_TOKEN"]
        )

    def get_name(self) -> str:
        if self._codespaces:
            return "GitHub Copilot (Codespaces)"
        return "GitHub Copilot"

    @property
    def is_available(self) -> bool:
        """Whether Copilot or Codespaces environment is detected."""
        return self._codespaces or self._copilot

    async def spawn_agents(self, orchestrator: AsyncOrchestrator) -> None:
        """Run agents in Copilot/Codespaces environment.

        Codespaces provides a full containerized Linux environment
        with persistent storage and port forwarding.
        """
        if not self.is_available:
            logger.warning(
                "GitHubCopilotAdapter: Neither Copilot nor Codespaces "
                "detected, falling back to standard execution"
            )

        if self._codespaces:
            logger.info(
                "Running via GitHub Codespaces (workspace: %s)",
                self.workspace_root,
            )
            logger.info(
                "Output will be saved to Codespaces persistent storage"
            )
        else:
            logger.info(
                "Running via GitHub Copilot adapter (workspace: %s)",
                self.workspace_root,
            )

        await orchestrator.run()
