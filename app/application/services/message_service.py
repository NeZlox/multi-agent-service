"""
Business logic service for Message management.
"""

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from personal_growth_sdk.multi_agent.models import Message

from app.adapters.outbound.repositories import MessageRepository

__all__ = ['MessageService']


class MessageService(SQLAlchemyAsyncRepositoryService[Message]):
    """
    Service layer for Message operations
    """

    repository_type = MessageRepository  # Associated repository
