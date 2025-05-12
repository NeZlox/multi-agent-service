"""
Dependency provider for MessageService.
Manages session service lifecycle with database connection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.services import MessageService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ['provide_message_service']


async def provide_message_service(
        db_session: AsyncSession | None = None,
) -> AsyncGenerator[MessageService, None]:
    """
    Async generator that provides MessageService instance.

    Args:
        db_session: Optional database session

    Yields:
        MessageService: Configured session service
    """

    async with MessageService.new(
            session=db_session
    ) as service:
        yield service
