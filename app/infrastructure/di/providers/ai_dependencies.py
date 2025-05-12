"""
Dependency provider for AIService.

Creates and returns an AIService instance configured with the specified agent.
"""

from __future__ import annotations

from app.application.services import AIService

__all__ = ['provide_ai_service']


def provide_ai_service(
        agent_name: str,
) -> AIService:
    """
    Provides an instance of AIService configured with the given agent.

    Args:
        agent_name: The name of the agent to be used by the service.

    Returns:
        AIService: Configured AI service instance.
    """

    return AIService(agent_name=agent_name)
