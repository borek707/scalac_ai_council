from __future__ import annotations

import logging
from typing import Optional

from council.config.schema import AgentState

logger = logging.getLogger(__name__)


# Valid state transitions: from_state -> {allowed to_states}
_VALID_TRANSITIONS: dict[AgentState, set[AgentState]] = {
    AgentState.PENDING: {AgentState.WRITING, AgentState.ERROR},
    AgentState.WRITING: {AgentState.WAITING, AgentState.DONE, AgentState.ERROR},
    AgentState.WAITING: {AgentState.WRITING, AgentState.DONE, AgentState.ERROR},
    AgentState.DONE: {AgentState.WRITING, AgentState.PENDING, AgentState.ERROR},
    AgentState.ERROR: {AgentState.PENDING, AgentState.WRITING},
}


class AgentStateMachine:
    """Thread-safe (asyncio-based) state machine for tracking agent states."""

    def __init__(self) -> None:
        self._states: dict[str, AgentState] = {}

    def register(self, agent: str) -> None:
        """Register an agent with PENDING state."""
        if agent not in self._states:
            self._states[agent] = AgentState.PENDING

    def transition(
        self,
        agent: str,
        from_state: AgentState,
        to_state: AgentState,
    ) -> bool:
        """Attempt a state transition for an agent.

        Args:
            agent: The agent name.
            from_state: The expected current state.
            to_state: The desired target state.

        Returns:
            True if the transition was successful, False otherwise.
        """
        current = self._states.get(agent)
        if current is None:
            logger.warning("Agent %s not registered in state machine", agent)
            return False
        if current != from_state:
            logger.warning(
                "Agent %s: expected state %s, got %s",
                agent,
                from_state.name,
                current.name,
            )
            return False
        allowed = _VALID_TRANSITIONS.get(from_state, set())
        if to_state not in allowed:
            logger.warning(
                "Agent %s: invalid transition %s -> %s",
                agent,
                from_state.name,
                to_state.name,
            )
            return False
        self._states[agent] = to_state
        logger.debug(
            "Agent %s: %s -> %s",
            agent,
            from_state.name,
            to_state.name,
        )
        return True

    def force_state(self, agent: str, state: AgentState) -> None:
        """Forcefully set an agent's state (bypass validation)."""
        self._states[agent] = state

    def get_state(self, agent: str) -> AgentState:
        """Get the current state of an agent."""
        return self._states.get(agent, AgentState.PENDING)

    def all_in_state(self, state: AgentState) -> bool:
        """Check if all registered agents are in the given state."""
        if not self._states:
            return False
        return all(s == state for s in self._states.values())

    def any_in_state(self, state: AgentState) -> bool:
        """Check if any registered agent is in the given state."""
        return any(s == state for s in self._states.values())

    def agents_in_state(self, state: AgentState) -> list[str]:
        """Return list of agent names in the given state."""
        return [name for name, s in self._states.items() if s == state]

    def get_snapshot(self) -> dict[str, AgentState]:
        """Return a snapshot of all agent states."""
        return dict(self._states)
