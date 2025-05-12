"""
Dependency provider for ChatExchangeService.
Injects message and snapshot services into the chat exchange use case.
"""

from app.application.services import MessageService, SnapshotService
from app.application.use_case.chat_exchange_service import ChatExchangeService

__all__ = ['provide_chat_exchange_service']


def provide_chat_exchange_service(
        message_service: MessageService,
        snapshot_service: SnapshotService
) -> ChatExchangeService:
    """
    Synchronous provider for ChatExchangeService.

    Args:
        message_service: MessageService instance
        snapshot_service: SnapshotService instance

    Returns:
        ChatExchangeService: Initialized chat exchange service
    """
    return ChatExchangeService(
        message_service=message_service,
        snapshot_service=snapshot_service
    )
