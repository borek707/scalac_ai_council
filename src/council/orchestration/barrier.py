from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FilesystemBarrier:
    """Barrier synchronizing agents via filesystem polling.

    All agents write their round files to a shared discussion directory.
    The barrier polls until all expected files are present or timeout.
    """

    def __init__(
        self,
        discussion_dir: Path,
        expected_agents: list[str],
        timeout: float = 300.0,
        poll_interval: float = 1.0,
    ) -> None:
        self.discussion_dir = discussion_dir
        self.expected_agents = list(expected_agents)
        self.timeout = timeout
        self.poll_interval = poll_interval

    def _round_file(self, round_num: int, agent: str) -> Path:
        """Get the expected file path for an agent's round output."""
        return self.discussion_dir / f"{agent.lower()}_round_{round_num}.md"

    def is_complete(self, round_num: int) -> bool:
        """Check if all agents have written their round file."""
        for agent in self.expected_agents:
            if not self._round_file(round_num, agent).exists():
                return False
        return True

    def get_status(self, round_num: int) -> dict[str, bool]:
        """Get completion status per agent."""
        return {
            agent: self._round_file(round_num, agent).exists()
            for agent in self.expected_agents
        }

    def _collect_files(self, round_num: int) -> dict[str, Path]:
        """Collect all agent file paths for a round."""
        result: dict[str, Path] = {}
        for agent in self.expected_agents:
            path = self._round_file(round_num, agent)
            if path.exists():
                result[agent] = path
        return result

    async def wait(self, round_num: int) -> dict[str, Path]:
        """Wait until all agents have written their round file.

        Polls the filesystem every `poll_interval` seconds until all
        expected files are present or the timeout is reached.

        Args:
            round_num: The round number to wait for.

        Returns:
            Mapping of agent_name -> file_path for all agents.

        Raises:
            TimeoutError: If not all files are present after `timeout` seconds.
        """
        elapsed = 0.0
        while elapsed < self.timeout:
            if self.is_complete(round_num):
                result = self._collect_files(round_num)
                logger.info(
                    "Barrier: round %d complete with %d/%d agents",
                    round_num,
                    len(result),
                    len(self.expected_agents),
                )
                return result

            status = self.get_status(round_num)
            ready = sum(1 for v in status.values() if v)
            logger.debug(
                "Barrier round %d: %d/%d ready (elapsed %.1fs)",
                round_num,
                ready,
                len(self.expected_agents),
                elapsed,
            )
            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval

        status = self.get_status(round_num)
        missing = [a for a, ready in status.items() if not ready]
        raise TimeoutError(
            f"Barrier timeout for round {round_num} after {self.timeout}s. "
            f"Missing agents: {missing}"
        )
