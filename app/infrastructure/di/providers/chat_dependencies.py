"""
Dependency provider for ChatService.
Manages user service lifecycle with database connection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.services import ChatService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ['provide_chat_service']


async def provide_chat_service(
        db_session: AsyncSession | None = None,
) -> AsyncGenerator[ChatService, None]:
    """
    Async generator that provides ChatService instance.

    Args:
        db_session: Optional database session

    Yields:
        ChatService: Configured user service
    """

    async with ChatService.new(
            session=db_session
    ) as service:
        yield service
