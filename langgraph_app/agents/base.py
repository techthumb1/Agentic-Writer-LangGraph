# src/langgraph_app/agents/base.py
"""
Defines the Abstract Base Class (ABC) for all agents in the system.

This enforces a consistent interface for every agent, ensuring they all
have a predictable `execute` method. This is a cornerstone of the
"no fallbacks" principle, as it guarantees a uniform contract for execution.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from ..core.state import EnrichedContentState
from ..core.types import AgentType
from ..core.exceptions import StateValidationError

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract Base Class for all content generation agents.
    
    Each agent must implement the `agent_type` property and the `execute` method.
    """

    def __init__(self, agent_type: AgentType):
        """
        Initialize the base agent.
        
        Args:
            agent_type: The specific type of agent (e.g., PLANNER, RESEARCHER)
        """
        self._agent_type = agent_type
        self.logger = logging.getLogger(f"agent.{agent_type.value}")

    @property
    def agent_type(self) -> AgentType:
        """The specific type of the agent (e.g., PLANNER, RESEARCHER)."""
        return self._agent_type

    @abstractmethod
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """
        Executes the agent's primary logic.

        This method takes the current application state, performs its specific task,
        and returns the updated state. It must be a deterministic operation.

        Args:
            state: The current EnrichedContentState of the workflow.

        Returns:
            The updated EnrichedContentState after the agent's execution.
            
        Raises:
            StateValidationError: If the input state is missing required data.
            AgentExecutionError: For any internal failures during execution.
        """
        pass

    def validate_state(self, state: EnrichedContentState, required_fields: list[str]) -> None:
        """
        Validates that the state contains all required fields.
        
        Args:
            state: The state to validate
            required_fields: List of field names that must exist and be non-empty
            
        Raises:
            StateValidationError: If any required field is missing or invalid
        """
        missing_fields = []
        
        for field_name in required_fields:
            if not hasattr(state, field_name):
                missing_fields.append(field_name)
                continue
            
            value = getattr(state, field_name)
            
            # Check if value is None or empty
            if value is None:
                missing_fields.append(field_name)
            elif isinstance(value, (dict, list, str)) and not value:
                missing_fields.append(field_name)
        
        if missing_fields:
            raise StateValidationError(
                f"{self.agent_type.value} requires the following fields: {', '.join(missing_fields)}"
            )

    def log_execution_start(self, state: EnrichedContentState, metadata: Dict[str, Any] | None = None) -> None:
        """Log the start of agent execution."""
        log_data = {"status": "started"}
        if metadata:
            log_data.update(metadata)
        
        state.log_agent_execution(self.agent_type, log_data)
        self.logger.info(f"{self.agent_type.value} execution started")

    def log_execution_complete(self, state: EnrichedContentState, metadata: Dict[str, Any] | None = None) -> None:
        """Log the completion of agent execution."""
        log_data = {"status": "completed"}
        if metadata:
            log_data.update(metadata)
        
        state.log_agent_execution(self.agent_type, log_data)
        self.logger.info(f"{self.agent_type.value} execution completed")