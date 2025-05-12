"""
Service for health check monitoring.
Provides system status and dependency health information.
"""

from typing import TYPE_CHECKING

from personal_growth_sdk.lib.schemas.health_check_schema import (
    DependencyHealth,
    DependencyType,
    HealthSchema,
    HealthStatus,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ai_agent_gateway import AIAgentFactory
from app.config.app_settings import get_settings
from app.lib.logger import logger

if TYPE_CHECKING:
    from app.application.services import AuthService, SnapshotService

settings = get_settings()

__all__ = ['HealthService']


class HealthService:
    """
    Central health monitoring service.

    Performs liveness checks for core system components, including:
    - PostgresSQL schema access
    - Authentication backend
    - Snapshot (ML) service
    - AI agent routing services

    Attributes:
        db_session: Async database session used for connectivity testing.
        ai_gateways_service: AI backend gateway factory.
        auth_service: Wrapper for Auth microservice.
        snapshot_service: Wrapper for Snapshot analysis microservice.
    """

    def __init__(
            self,
            db_session: AsyncSession,
            ai_gateways_service: AIAgentFactory,
            auth_service: 'AuthService',
            snapshot_service: 'SnapshotService',
    ):
        self.db_session = db_session
        self.ai_gateways_service = ai_gateways_service
        self.auth_service = auth_service
        self.snapshot_service = snapshot_service

    async def get_health(self) -> HealthSchema:
        """
        Perform a full health scan of system dependencies.

        Components checked:
        - PostgresSQL (via schema probe)
        - Authentication API (via `/ping`)
        - Snapshot API (via `/ping`)
        - AI agent endpoints

        Returns:
            HealthSchema: Overall system status with component breakdown
        """

        db_dependency = DependencyHealth(
            name=f'PostgresSQL: schema `{settings.postgres.SCHEMA}`',
            status=HealthStatus.OK,
            type=DependencyType.POSTGRES,
            details=None
        )

        try:
            # Basic database connectivity test
            result = await self.db_session.execute(
                text("""
                        SELECT schema_name
                        FROM information_schema.schemata
                        WHERE schema_name = :schema
                    """),
                {'schema': settings.postgres.SCHEMA}
            )
            if result.scalar() != settings.postgres.SCHEMA:
                db_dependency.status = HealthStatus.ERROR
                db_dependency.details = {'error': f'Schema `{settings.postgres.SCHEMA}` not found'}
        except Exception as e:
            await logger.aerror(f'[HealthCheck] Database health check failed: {e}')
            db_dependency.status = HealthStatus.ERROR
            db_dependency.details = {'error': str(e)}

        auth_dependency = DependencyHealth(
            name='Authentication Service',
            status=HealthStatus.OK,
            type=DependencyType.HTTP,
            details=None
        )
        try:
            await self.auth_service.ping()

        except Exception as e:
            await logger.aerror(f'[HealthCheck] Authentication service check failed: {e}')
            auth_dependency.status = HealthStatus.ERROR
            auth_dependency.details = {'error': str(e)}

        snapshot_dependency = DependencyHealth(
            name='SnapShot Service',
            status=HealthStatus.OK,
            type=DependencyType.HTTP,
            details=None
        )
        try:
            await self.snapshot_service.ping()

        except Exception as e:
            await logger.aerror(f'[HealthCheck] SnapShot service check failed: {e}')
            snapshot_dependency.status = HealthStatus.ERROR
            snapshot_dependency.details = {'error': str(e)}

        try:
            ai_gateways_service_dependencies = await self.ai_gateways_service.ping_agents()
        except Exception as e:
            logger.error(f'[HealthCheck] AI gateways check failed: {e}')
            ai_gateways_service_dependencies = [DependencyHealth(
                name='All AI GateWays',
                status=HealthStatus.ERROR,
                type=DependencyType.HTTP,
                details={'error': str(e)}
            )]

        deps = [db_dependency, auth_dependency, snapshot_dependency]
        deps.extend(ai_gateways_service_dependencies)

        status = HealthStatus.OK if all(dep.status == HealthStatus.OK for dep in deps) else HealthStatus.ERROR

        return HealthSchema(
            status=status,
            deps=deps
        )
