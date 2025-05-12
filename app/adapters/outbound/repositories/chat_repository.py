"""
Database repository for Chat model.
Handles basic database operations for user entities.
"""

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from personal_growth_sdk.multi_agent.models import Chat

__all__ = ['ChatRepository']


class ChatRepository(SQLAlchemyAsyncRepository[Chat]):
    """
    Async repository for Chat model operations
    """

    model_type = Chat  # Specifies the SQLAlchemy model class
