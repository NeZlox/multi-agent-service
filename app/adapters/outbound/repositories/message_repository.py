"""
Database repository for Message model.
Provides basic CRUD operations for user sessions.
"""

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from personal_growth_sdk.multi_agent.models import Message

__all__ = ['MessageRepository']


class MessageRepository(SQLAlchemyAsyncRepository[Message]):
    """
    Async repository for Message model operations
    """

    model_type = Message  # Specifies the SQLAlchemy model class
