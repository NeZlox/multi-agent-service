"""
Dependency provider for HealthService.
Provides health monitoring service with database session.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.ai_agent_gateway import AIAgentFactory
from app.application.services import HealthService
from app.config.base_settings import get_settings
from app.infrastructure.di.providers.auth_dependencies import provide_authenticate_service
from app.infrastructure.di.providers.snapshot_dependencies import provide_snapshot_service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ['provide_health_service']

settings = get_settings()


def provide_health_service(
        db_session: AsyncSession | None = None
) -> HealthService:
    """
    Factory function that creates HealthService instance.

    Args:
        db_session: Optional database session

    Returns:
        HealthService: Configured health monitoring service
    """

    return HealthService(
        db_session=db_session,
        ai_gateways_service=AIAgentFactory(),
        auth_service=provide_authenticate_service(),
        snapshot_service=provide_snapshot_service(),
    )
