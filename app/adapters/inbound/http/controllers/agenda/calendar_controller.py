"""
Agenda calendar endpoints proxy controller.

This controller provides OpenAPI documentation and routing for calendar-related
operations from the upstream Agenda service.

Responsibilities:
- Define CRUD operations for calendars
- Proxy responses from the remote Agenda service
- Allow filtering, reading, creating, updating, and deleting calendar entities

All responses are proxied via `ReverseProxyMiddleware` and decoded from
`gw_state.upstream_raw`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Annotated

import msgspec
from advanced_alchemy.service import OffsetPagination
from litestar import Controller, delete, get, patch, post
from litestar._kwargs.dependencies import Dependency
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.params import Body, Parameter
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from personal_growth_sdk.agenda.schemas import (
    CalendarCreateRequest,
    CalendarPatchRequest,
    CalendarResponse,
)

from app.adapters.inbound.http.urls.agenda.calendar_urls import (
    DELETE_CALENDAR_URI,
    GET_CALENDAR_URI,
    GET_CALENDARS_URI,
    PATCH_CALENDAR_URI,
    POST_CALENDAR_URI,
    PREFIX,
)
from app.infrastructure.di.providers import gateway_state_provider
from app.lib.context import GatewayState

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
__all__ = ['AgendaCalendarsController']


class AgendaCalendarsController(Controller):
    """
    Proxy controller for calendar operations from the Agenda microservice.

    Attributes:
        path: Base API prefix for calendar endpoints
        dependencies: Injects gateway state into handlers
        tags: OpenAPI grouping for docs
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'gw_state': Provide(gateway_state_provider, sync_to_thread=False)
    }
    tags = ['Agenda · Calendars']  # noqa: RUF012

    @get(
        path=GET_CALENDARS_URI,
        operation_id='GetCalendars',
        summary='List calendars',
        description='Return every calendar visible to the caller.',
        status_code=HTTP_200_OK,
        responses={HTTP_200_OK: ResponseSpec(data_container=Sequence[CalendarResponse])},
    )
    async def list_calendars(
            self,
            gw_state: GatewayState,
            filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)]  # noqa: ARG002
    ) -> OffsetPagination[CalendarResponse]:
        """
        Return a list of calendars visible to the authenticated user.

        Args:
            gw_state: Proxy context holding upstream response
            filters: Optional filters for pagination/searching

        Returns:
            Paginated list of calendar records
        """

        return msgspec.json.decode(gw_state.upstream_raw, type=OffsetPagination[CalendarResponse])

    @get(
        path=GET_CALENDAR_URI,
        operation_id='GetCalendar',
        summary='Get calendar',
        description='Return a single calendar by its id.',
        status_code=HTTP_200_OK,
        responses={HTTP_200_OK: ResponseSpec(data_container=CalendarResponse)},
    )
    async def get_calendar(
            self,
            calendar_id: Annotated[int, Parameter(description='Target calendar id')],  # noqa: ARG002
            gw_state: GatewayState,
    ) -> CalendarResponse:
        """
        Retrieve a single calendar by its unique identifier.

        Args:
            calendar_id: Target calendar ID
            gw_state: Proxy context holding upstream response

        Returns:
            The requested calendar object
        """

        return msgspec.json.decode(gw_state.upstream_raw, type=CalendarResponse)

    @post(
        path=POST_CALENDAR_URI,
        operation_id='CreateCalendar',
        summary='Create calendar',
        description='Create a new calendar and return it.',
        status_code=HTTP_201_CREATED,
        responses={HTTP_201_CREATED: ResponseSpec(data_container=CalendarResponse)},
    )
    async def create_calendar(
            self,
            data: Annotated[CalendarCreateRequest, Body(title='Calendar data')],  # noqa: ARG002
            gw_state: GatewayState,
    ) -> Response[CalendarResponse]:
        """
        Create a new calendar entry in the Agenda system.

        Args:
            data: New calendar creation payload
            gw_state: Proxy context holding upstream response

        Returns:
            Response containing the created calendar object
        """

        obj = msgspec.json.decode(gw_state.upstream_raw, type=CalendarResponse)
        return Response(content=obj)

    @patch(
        path=PATCH_CALENDAR_URI,
        operation_id='PatchCalendar',
        summary='Update calendar partially',
        description='Apply partial updates to a calendar.',
        status_code=HTTP_200_OK,
        responses={HTTP_200_OK: ResponseSpec(data_container=CalendarResponse)},
    )
    async def patch_calendar(
            self,
            calendar_id: Annotated[int, Parameter(description='Target calendar id')],  # noqa: ARG002
            data: Annotated[CalendarPatchRequest, Body(title='Patch data')],  # noqa: ARG002
            gw_state: GatewayState,
    ) -> CalendarResponse:
        """
        Apply partial updates to an existing calendar.

        Args:
            calendar_id: Target calendar ID
            data: Fields to update
            gw_state: Proxy context holding upstream response

        Returns:
            Updated calendar object
        """

        return msgspec.json.decode(gw_state.upstream_raw, type=CalendarResponse)

    @delete(
        path=DELETE_CALENDAR_URI,
        operation_id='DeleteCalendar',
        summary='Delete calendar',
        description='Remove a calendar permanently.',
        status_code=HTTP_204_NO_CONTENT,
    )
    async def delete_calendar(
            self,
            calendar_id: Annotated[int, Parameter(description='Target calendar id')]  # noqa: ARG002
    ) -> None:
        """
        Delete an existing calendar by ID.

        Args:
            calendar_id: ID of the calendar to delete
            # gw_state: Proxy context used only to comply with middleware contract

        Returns:
            None
        """

        return None
