from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from council.platform.base import PlatformAdapter

if TYPE_CHECKING:
    from council.orchestration.orchestrator import AsyncOrchestrator

logger = logging.getLogger(__name__)


class CursorAdapter(PlatformAdapter):
    """Cursor AI IDE platform adapter.

    Cursor is a VS Code fork with built-in AI (Claude, GPT-4o).
    This adapter runs the council within Cursor's integrated terminal,
    leveraging the full Node.js/Python environment.

    Environment detection:
        - Cursor sets ``CURSOR_TRACE_ID`` and ``CURSOR_PID`` env vars
        - Full terminal access via ``Ctrl+`` ` ``
        - AI chat panel available for interactive debugging

    Usage::

        # In Cursor terminal
        python -m council --config firm.json --platform cursor

    Features:
        - Native terminal integration
        - AI chat for debugging agent outputs
        - File watching for real-time output preview

    Reference:
        - https://cursor.com
    """

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self._cursor_detected = self._detect_cursor()

    def get_name(self) -> str:
        return "Cursor"

    def _detect_cursor(self) -> bool:
        """Detect if running inside Cursor IDE."""
        cursor_markers = [
            "CURSOR_TRACE_ID",
            "CURSOR_PID",
            "CURSOR_APP_VERSION",
        ]
        return any(os.environ.get(m) for m in cursor_markers)

    @property
    def is_available(self) -> bool:
        """Whether the current environment is Cursor IDE."""
        return self._cursor_detected

    async def spawn_agents(self, orchestrator: AsyncOrchestrator) -> None:
        """Run agents within Cursor's integrated terminal.

        Cursor provides a full terminal and file system access,
        so we use the standard AsyncOrchestrator with asyncio.
        """
        if not self._cursor_detected:
            logger.warning(
                "CursorAdapter: Cursor IDE not detected, "
                "falling back to standard asyncio execution"
            )

        logger.info("Running via Cursor adapter (workspace: %s)", self.workspace_root)

        # Cursor tip: open output files side-by-side as they generate
        logger.info(
            "Tip: Open output/ folder in Cursor explorer to watch "
            "files generate in real-time"
        )

        await orchestrator.run()
