from __future__ import annotations

from council.platform.base import PlatformAdapter
from council.platform.cli_adapter import CLIAdapter
from council.platform.cursor_adapter import CursorAdapter
from council.platform.copilot_adapter import GitHubCopilotAdapter
from council.platform.idx_adapter import GoogleIDXAdapter
from council.platform.kimi_adapter import KimiAdapter
from council.platform.web_adapter import WebPlatformAdapter

__all__ = [
    "PlatformAdapter",
    "CLIAdapter",
    "CursorAdapter",
    "GitHubCopilotAdapter",
    "GoogleIDXAdapter",
    "KimiAdapter",
    "WebPlatformAdapter",
]
