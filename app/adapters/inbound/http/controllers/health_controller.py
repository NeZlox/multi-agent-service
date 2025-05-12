"""
Health check API controller.
Provides system monitoring endpoints.
"""

from __future__ import annotations

from litestar import Controller, get
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT
from personal_growth_sdk.lib.schemas.health_check_schema import HealthSchema

from app.adapters.inbound.http.urls.health_urls import GET_HEALTH, GET_PING, PREFIX
from app.application.services import HealthService
from app.infrastructure.di.providers import provide_health_service

__all__ = ['HealthController']


class HealthController(Controller):
    """
    Controller for health check endpoints.

    Attributes:
        path: Base API path (root)
        dependencies: Required service providers
        tags: OpenAPI grouping tag
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'health_service': Provide(provide_health_service, sync_to_thread=False)
    }
    tags = ['Health']  # noqa: RUF012

    @get(
        path=GET_HEALTH,
        operation_id='GetServiceHealth',
        summary='Get service health status',
        description='Comprehensive health check of service components and dependencies',
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=HealthSchema,
                description='Service health status with component details'
            )
        }
    )
    async def get_health(
            self,
            health_service: HealthService,
    ) -> HealthSchema:
        """
        Comprehensive system health check.

        Args:
            health_service: Health monitoring service

        Returns:
            Detailed health status report
        """

        return await health_service.get_health()

    @get(
        path=GET_PING,
        operation_id='ServicePing',
        summary='Service liveness check',
        description='Basic endpoint to verify service is running and responsive',
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=None,
                description='Service is alive and responding'
            )
        }
    )
    async def get_ping(
            self,
    ) -> None:
        """
        Basic liveness check endpoint.

        Returns:
            Empty response (204) if service is alive
        """

        return None
