from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from council.orchestration.orchestrator import AsyncOrchestrator


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific adapters.

    Platform adapters handle how the orchestrator is executed
    on different platforms (local CLI, Kimi Code, etc.).
    """

    @abstractmethod
    async def spawn_agents(self, orchestrator: AsyncOrchestrator) -> None:
        """Spawn and run agents on the target platform."""
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return the display name of this platform adapter."""
        ...
