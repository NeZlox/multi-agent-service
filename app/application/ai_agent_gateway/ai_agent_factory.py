"""
Factory and route_registry for AI agent backends.

Provides a singleton interface to retrieve, register, and health-check available agents.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.lib.errors.exceptions import UnsupportedAgentError
from app.lib.singleton import SingletonMeta

from .ai_agent_interface import AIAgentGatewayInterface
from .utils import discover_agents

if TYPE_CHECKING:
    from personal_growth_sdk.lib.schemas.health_check_schema import DependencyHealth

__all__ = ['AIAgentFactory']


class AIAgentFactory(metaclass=SingletonMeta):
    """
    Singleton factory and route_registry for AI agents.

    Automatically discovers and registers all available agent backends.

    Attributes:
        _agents: A dictionary mapping agent names to their instances.
    """
    _agents: dict[str, AIAgentGatewayInterface] = discover_agents()

    @classmethod
    async def ping_agents(
            cls, only: list[str] | None = None
    ) -> list[DependencyHealth]:
        """
        Performs health checks for all registered agents (or selected ones).

        Args:
            only: Optional list of agent names to check. If None, all agents are checked.

        Returns:
            List of DependencyHealth objects for each checked agent.
        """
        results: list[DependencyHealth] = []
        for name, agent_cls in cls._agents.items():
            if (only is None) or (name in only):
                results.append(await agent_cls.ping())
        return results

    @classmethod
    def get(cls, name: str) -> AIAgentGatewayInterface:
        """
        Retrieve a registered AI agent by name.

        Args:
            name: The name of the agent.

        Returns:
            The corresponding AIAgentGatewayInterface instance.

        Raises:
            UnsupportedAgentError: If the agent is not registered.
        """
        try:
            return cls._agents[name.lower()]
        except KeyError as exc:
            raise UnsupportedAgentError(name) from exc

    @classmethod
    def register(cls, name: str, agent_cls: AIAgentGatewayInterface) -> None:
        """
        Manually register an AI agent under a given name.

        Args:
            name: The name to register the agent under.
            agent_cls: The agent instance to register.
        """
        cls._agents[name.lower()] = agent_cls
