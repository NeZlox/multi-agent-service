"""
Service layer abstraction for LLM-powered agent interactions.

This module exposes a single `AIService` class that serves as the main interface
for controllers and use-cases to request AI-generated responses without
depending on a specific implementation of an AI provider.
"""

from app.application.ai_agent_gateway import AIAgentFactory, AIAgentGatewayInterface

__all__ = ['AIService']


class AIService:
    """
    High-level interface for generating replies from an AI agent.

    This service acts as a facade, hiding the specifics of the underlying
    LLM provider. It is designed to be called by application controllers
    and domain services.
    """

    def __init__(self, agent_name: str):
        self.gateway: AIAgentGatewayInterface = AIAgentFactory.get(agent_name)

    async def generate_reply(
            self,
            chat_id: int,
            new_message: str
    ) -> str:
        """
        Generate a response from the selected AI agent.

        Args:
            chat_id: Identifier of the chat session.
            new_message: User message content to send to the AI.

        Returns:
            AI-generated response text.
        """

        return await self.gateway.generate(chat_id=chat_id, new_message=new_message)
