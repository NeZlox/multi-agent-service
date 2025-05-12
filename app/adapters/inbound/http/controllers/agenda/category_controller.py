"""
Agenda category endpoint proxy controller.

This controller provides OpenAPI documentation and routing for category-related
data exposed by the Agenda service.

Responsibilities:
- Expose read-only access to category list
- Proxy the `/categories` endpoint from the upstream Agenda service
- Decode results from `gw_state.upstream_raw` into `CategoryResponse` schemas

All responses are proxied via `ReverseProxyMiddleware` and decoded from
`gw_state.upstream_raw`.
"""

from __future__ import annotations

from collections.abc import Sequence

import msgspec
from litestar import Controller, get
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_200_OK
from personal_growth_sdk.agenda.schemas import CategoryResponse

from app.adapters.inbound.http.urls.agenda.category_urls import GET_CATEGORIES_URI, PREFIX
from app.infrastructure.di.providers import gateway_state_provider
from app.lib.context import GatewayState

__all__ = ['AgendaCategoriesController']


class AgendaCategoriesController(Controller):
    """
    Proxy controller for agenda category operations.

    Attributes:
        path: Base API prefix for category endpoints
        dependencies: Injects gateway state into handlers
        tags: OpenAPI tag used in documentation
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'gw_state': Provide(gateway_state_provider, sync_to_thread=False)
    }
    tags = ['Agenda · Categories']  # noqa: RUF012

    @get(
        path=GET_CATEGORIES_URI,
        operation_id='GetCategories',
        status_code=HTTP_200_OK,
        responses={HTTP_200_OK: ResponseSpec(data_container=Sequence[CategoryResponse])},
    )
    async def list_categories(
            self,
            gw_state: GatewayState
    ) -> Sequence[CategoryResponse]:
        """
        Return the list of predefined calendar categories from the Agenda service.

        Args:
            gw_state: Proxy context holding the upstream response payload

        Returns:
            List of available `CategoryResponse` objects
        """

        return msgspec.json.decode(gw_state.upstream_raw, type=list[CategoryResponse])
