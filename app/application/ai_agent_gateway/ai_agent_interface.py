"""
Defines a common interface for AI agent backends.

Each agent must inherit from `AIAgentGatewayInterface` and implement `generate()` and `_get_health_status()`.
Ensures a consistent contract for message generation and health monitoring across all agents.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from personal_growth_sdk.lib.schemas.health_check_schema import (
    DependencyHealth,
    DependencyType,
    HealthStatus,
)

__all__ = ['AIAgentGatewayInterface']


class AIAgentGatewayInterface(ABC):
    """
    Abstract base class for AI/LLM agent backends.

    Attributes:
        name (str): Human-readable name of the agent (used in logs and health checks).
    """

    name: str | None = None

    def __init_subclass__(cls, **kwargs):
        """
        Ensures that all subclasses define required attributes.
        Currently, validates that `name` is set.
        """

        super().__init_subclass__(**kwargs)

        required = ('name',)
        for attr in required:
            if getattr(cls, attr, None) in (None, ''):
                raise TypeError(f'{cls.__name__}: attribute `{attr}` must be set.')

    @classmethod
    async def ping(cls) -> DependencyHealth:
        """
        Performs a health check for the current agent implementation.

        Returns:
            DependencyHealth: The result of the health check, including status and optional error details.
        """
        gateway_dependency = DependencyHealth(
            type=DependencyType.HTTP,
            name=f'Agent: {cls.name}',
            status=HealthStatus.OK,
            details=None
        )
        try:
            status, details = await cls._get_health_status()
            gateway_dependency.status = status
            gateway_dependency.details = details
        except Exception as e:
            gateway_dependency.status = HealthStatus.ERROR
            gateway_dependency.details = {'error': str(e)}

        return gateway_dependency

    @classmethod
    @abstractmethod
    async def _get_health_status(cls, **kwargs) -> tuple[HealthStatus, dict[str, Any] | None]:
        """
        Checks the backend service's health status.

        Args:
            **kwargs: Optional parameters for checking connectivity or credentials.

        Returns:
            A tuple containing health status and optional diagnostic details.
        """
        pass

    @classmethod
    @abstractmethod
    async def generate(
            cls,
            chat_id: int,
            new_message: str
    ) -> str:
        """
        Generates a response from the assistant based on the given message.

        This method must encapsulate networking, retries, and error handling internally.

        Args:
            chat_id: Identifier for the conversation.
            new_message: User message to respond to.

        Returns:
            The assistant's generated reply as a string.
        """
        pass
