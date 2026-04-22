from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from council.platform.base import PlatformAdapter

if TYPE_CHECKING:
    from council.orchestration.orchestrator import AsyncOrchestrator

logger = logging.getLogger(__name__)


class GoogleIDXAdapter(PlatformAdapter):
    """Google IDX (Project IDX) platform adapter.

    Google IDX is a cloud-based IDE with AI assistance and
    full terminal access. This adapter uses the Nix environment
    and workspace API to run the council system.

    Environment detection:
        - IDX sets ``GOOGLE_CLOUD_WORKSTATIONS`` env var
        - Workspace root is ``/home/user/[project-name]``
        - Has full ``nix`` and ``python`` support

    Usage::

        # In IDX terminal
        python -m council --config firm.json --platform idx

    Reference:
        - https://idx.dev
        - https://developers.google.com/idx
    """

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self._idx_detected = self._detect_idx()

    def get_name(self) -> str:
        return "Google IDX"

    def _detect_idx(self) -> bool:
        """Detect if running inside Google IDX environment."""
        idx_markers = [
            "GOOGLE_CLOUD_WORKSTATIONS",
            "IDX_ENVIRONMENT",
            "MONOSPACE_ENVIRONMENT",
        ]
        return any(os.environ.get(m) for m in idx_markers)

    @property
    def is_available(self) -> bool:
        """Whether the current environment is Google IDX."""
        return self._idx_detected

    async def spawn_agents(self, orchestrator: AsyncOrchestrator) -> None:
        """Run agents in the IDX workspace environment.

        IDX provides a full Linux environment — we use asyncio for
        parallelism within the single workspace, leveraging the
        existing AsyncOrchestrator directly.
        """
        if not self._idx_detected:
            logger.warning(
                "GoogleIDXAdapter: IDX environment not detected, "
                "falling back to standard asyncio execution"
            )

        logger.info(
            "Running via Google IDX adapter (workspace: %s)",
            self.workspace_root,
        )

        # IDX has generous resource limits — we can run all agents
        # in parallel within the same process using asyncio
        await orchestrator.run()

    async def preview_output(self, output_dir: Path) -> None:
        """Open the output directory in IDX's preview pane.

        IDX supports previewing generated files side-by-side
        with the editor.
        """
        preview_url = f"https://idx.google.com/{self.workspace_root.name}"
        logger.info("IDX preview available at: %s", preview_url)
        # In IDX, you can use the CLI to open preview:
        # idx preview --port 8080
