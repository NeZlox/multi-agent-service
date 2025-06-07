"""
ChatExchangeService coordinates a full message exchange workflow.

This service acts as an orchestrator for the "user sends a message, AI replies" use-case,
combining snapshot capturing, message persistence, and LLM-based response generation.
"""

from __future__ import annotations

from personal_growth_sdk.multi_agent.models.enums import ChatRole
from personal_growth_sdk.multi_agent.schemas import (
    MessageCreateRequest,
    MessageResponse,
)

from app.application.services import MessageService, SnapshotService
from app.infrastructure.di.providers import provide_ai_service

__all__ = ['ChatExchangeService']


class ChatExchangeService:
    """
    High-level service for handling a complete chat exchange session.

    Combines message persistence, snapshot capture, and AI-driven reply generation.
    Used by controller layers to coordinate user input and assistant output.
    """

    def __init__(
            self,
            message_service: MessageService,
            snapshot_service: SnapshotService,
    ) -> None:
        self.message_service = message_service
        self.snapshot_service = snapshot_service

    async def exchange(
            self,
            user_id: int,
            chat_id: int,
            message: str,
    ) -> list[MessageResponse]:
        """
        Perform the message exchange workflow:
        - Save snapshot of the user and input message.
        - Create the user message.
        - Generate assistant reply using an AI agent.
        - Create the assistant message.
        - Return both messages as MessageResponse objects.

        Args:
            user_id: External user identifier.
            chat_id: Chat session ID to attach messages to.
            message: Text content sent by the user.

        Returns:
            Sequence containing the user message and the assistant's reply.
        """

        await self.snapshot_service.capture(user_id=user_id, message=message)
        ai_service = provide_ai_service(agent_name='agenda')

        user_msg = await self.message_service.create(
            MessageCreateRequest(
                chat_id=chat_id,
                role=ChatRole.USER,
                content=message,
            )
        )

        assistant_text = await ai_service.generate_reply(
            chat_id=chat_id,
            new_message=message,
        )

        assistant_msg = await self.message_service.create(
            MessageCreateRequest(
                chat_id=chat_id,
                role=ChatRole.ASSISTANT,
                content=assistant_text,
            )
        )

        return [
            self.message_service.to_schema(user_msg, schema_type=MessageResponse),
            self.message_service.to_schema(assistant_msg, schema_type=MessageResponse),
        ]
