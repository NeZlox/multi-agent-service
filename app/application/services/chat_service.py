"""
Business logic service for Chat management.
"""

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from personal_growth_sdk.multi_agent.models import Chat

from app.adapters.outbound.repositories import ChatRepository

__all__ = ['ChatService']


class ChatService(SQLAlchemyAsyncRepositoryService[Chat]):
    """
    Service layer for Chat operations
    """

    repository_type = ChatRepository  # Associated repository
