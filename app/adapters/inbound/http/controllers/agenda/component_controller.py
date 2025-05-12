"""
Agenda component endpoint proxy controller.

This controller provides OpenAPI documentation and routing for component-related
operations (e.g., events, tasks) from the upstream Agenda service.

Responsibilities:
- Define CRUD operations for calendar components
- Proxy requests and responses from the Agenda microservice
- Decode JSON payloads from `gw_state.upstream_raw` into structured response models

All responses are proxied via `ReverseProxyMiddleware` and decoded from
`gw_state.upstream_raw`.
"""
from __future__ import annotations

import datetime  # noqa: TC003
from collections.abc import Sequence
from typing import Annotated

import msgspec
from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.params import Body, Parameter
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from personal_growth_sdk.agenda.schemas import (
    ComponentCreateRequest,
    ComponentPatchRequest,
    ComponentResponse,
)

from app.adapters.inbound.http.urls.agenda.component_urls import (
    DELETE_COMPONENT_URI,
    GET_COMPONENT_URI,
    GET_COMPONENTS_BY_RANGE_URI,
    PATCH_COMPONENT_URI,
    POST_COMPONENT_URI,
    PREFIX,
)
from app.infrastructure.di.providers import gateway_state_provider
from app.lib.context import GatewayState

__all__ = ['AgendaComponentsController']


class AgendaComponentsController(Controller):
    """
    Proxy controller for calendar components from the Agenda service.

    Attributes:
        path: API base path for components
        dependencies: Injects upstream response context
        tags: Used for OpenAPI grouping
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'gw_state': Provide(gateway_state_provider, sync_to_thread=False)
    }
    tags = ['Agenda · Components']  # noqa: RUF012

    @post(
        path=POST_COMPONENT_URI,
        operation_id='CreateComponent',
        status_code=HTTP_201_CREATED,
        responses={HTTP_201_CREATED: ResponseSpec(data_container=ComponentResponse)},
    )
    async def create_component(
            self,
            data: Annotated[ComponentCreateRequest, Body(title='Component data')],  # noqa: ARG002
            gw_state: GatewayState,
    ) -> Response[ComponentResponse]:
        """
        Create a new calendar component in Agenda.

        Args:
            data: New component creation data
            gw_state: Proxy context with upstream response

        Returns:
            Created component object
        """

        return Response(
            content=msgspec.json.decode(gw_state.upstream_raw, type=ComponentResponse)
        )

    @get(
        path=GET_COMPONENT_URI,
        operation_id='GetComponent',
        status_code=HTTP_200_OK,
        responses={HTTP_200_OK: ResponseSpec(data_container=ComponentResponse)},
    )
    async def get_component(
            self,
            component_id: Annotated[int, Parameter(description='Component id')],  # noqa: ARG002
            gw_state: GatewayState,
    ) -> ComponentResponse:
        """
        Get a single calendar component by its ID.

        Args:
            component_id: Target component ID
            gw_state: Proxy context with upstream response

        Returns:
            Component object
        """

        return msgspec.json.decode(gw_state.upstream_raw, type=ComponentResponse)

    @patch(
        path=PATCH_COMPONENT_URI,
        operation_id='PatchComponent',
        status_code=HTTP_200_OK,
        responses={HTTP_200_OK: ResponseSpec(data_container=ComponentResponse)},
    )
    async def patch_component(
            self,
            component_id: Annotated[  # noqa: ARG002
                int,
                Parameter(
                    description='Component id'
                ),
            ],
            data: Annotated[ComponentPatchRequest, Body(title='Patch data')],  # noqa: ARG002
            gw_state: GatewayState,
    ) -> ComponentResponse:
        """
        Apply partial update to a calendar component.

        Args:
            component_id: ID of the component to patch
            data: Patch fields
            gw_state: Proxy context with upstream response

        Returns:
            Updated component
        """

        return msgspec.json.decode(gw_state.upstream_raw, type=ComponentResponse)

    @delete(
        path=DELETE_COMPONENT_URI,
        operation_id='DeleteComponent',
        status_code=HTTP_204_NO_CONTENT,
    )
    async def delete_component(
            self,
            component_id: Annotated[int, Parameter(description='Component id')]  # noqa: ARG002
    ) -> None:
        """
        Delete a calendar component by ID.

        Args:
            component_id: ID of the component to delete

        Returns:
            None
        """

        return None

    @get(
        path=GET_COMPONENTS_BY_RANGE_URI,
        operation_id='GetComponentsByRange',
        summary='List components in a time-range',
        status_code=HTTP_200_OK,
        responses={HTTP_200_OK: ResponseSpec(data_container=Sequence[ComponentResponse])},
    )
    async def list_by_range(
            self,
            start_date: Annotated[datetime.datetime, Parameter(description='RFC3339 start timestamp')],  # noqa: ARG002
            end_date: Annotated[datetime.datetime, Parameter(description='RFC3339 end timestamp')],  # noqa: ARG002
            gw_state: GatewayState
    ) -> Sequence[ComponentResponse]:
        """
        List calendar components between two timestamps.

        Args:
            start_date: Start timestamp (RFC3339)
            end_date: End timestamp (RFC3339)
            gw_state: Proxy context with upstream response

        Returns:
            List of components in the specified range
        """

        return msgspec.json.decode(gw_state.upstream_raw, type=list[ComponentResponse])
