"""
Chat management API controller.

This module defines the API controller for managing chat sessions.
It provides endpoints to create, retrieve, update, and delete chats.

Endpoints are private and require appropriate developer privileges.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from advanced_alchemy.service import OffsetPagination
from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.params import Body, Dependency, Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from personal_growth_sdk.multi_agent.schemas import ChatCreateRequest, ChatResponse, ChatUpdateRequest

from app.adapters.inbound.http.urls.chat_urls import (
    DELETE_CHAT_URI,
    GET_CHAT_URI,
    GET_CHATS_URI,
    POST_CHAT_URI,
    PREFIX,
    PUT_CHAT_URI,
)
from app.application.services import ChatService
from app.infrastructure.di.providers import gateway_state_provider, provide_chat_service, role_required
from app.lib.context import GatewayState
from app.lib.security import RoleGroup

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes

__all__ = ['ChatController']


class ChatController(Controller):
    """
    Controller for chat management endpoints.

    Attributes:
        path: Base API path (/chats)
        dependencies: Required service providers
        tags: OpenAPI grouping tag
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'chat_service': Provide(provide_chat_service),
        'gw_state': Provide(gateway_state_provider, sync_to_thread=False)
    }
    tags = ['Chat']  # noqa: RUF012

    @get(
        path=GET_CHATS_URI,
        operation_id='GetChats',
        name='chats:list',
        summary='Get all chats',
        description='Retrieve a list of all chats (Private method for developers).',
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=OffsetPagination[ChatResponse],
                description='Successfully retrieved list of chats'
            )
        }
    )
    async def get_chats(
            self,
            gw_state: GatewayState,
            chat_service: ChatService,
            filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)]
    ) -> OffsetPagination[ChatResponse]:
        """
        Get paginated chat list.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            chat_service: Chat service
            filters: Query filters

        Returns:
            Paginated chat results
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        results, total = await chat_service.list_and_count(*filters)
        return chat_service.to_schema(data=results, total=total, filters=filters, schema_type=ChatResponse)

    @get(
        path=GET_CHAT_URI,
        operation_id='GetChat',
        name='chats:get_one',
        summary='Get a single chat',
        description='Retrieve a single chat by its ID (Private method for developers).',
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=ChatResponse,
                description='Successfully retrieved the chat'
            )
        }
    )
    async def get_chat(
            self,
            gw_state: GatewayState,
            chat_service: ChatService,
            chat_id: Annotated[
                int,
                Parameter(
                    title='Chat ID',
                    description='The ID of the chat to retrieve.'
                )
            ]
    ) -> ChatResponse:
        """
        Get single chat details.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            chat_service: Chat service
            chat_id: Target chat ID

        Returns:
            Detailed chat information
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        db_obj = await chat_service.get(chat_id)
        return chat_service.to_schema(db_obj, schema_type=ChatResponse)

    @post(
        path=POST_CHAT_URI,
        operation_id='CreateChat',
        name='chats:create',
        summary='Create a chat',
        description='Create a new chat with provided data (Private method for developers).',
        status_code=HTTP_201_CREATED,
        responses={
            HTTP_201_CREATED: ResponseSpec(
                data_container=ChatResponse,
                description='Successfully created a new chat'
            )
        }
    )
    async def create_chat(
            self,
            chat_service: ChatService,
            gw_state: GatewayState,
            data: Annotated[ChatCreateRequest, Body(title='Create Chat')]
    ) -> ChatResponse:
        """
        Create new chat record.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            chat_service: Chat service
            data: Chat creation data

        Returns:
            Newly created chat details
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        db_obj = await chat_service.create(data)
        return chat_service.to_schema(db_obj, schema_type=ChatResponse)

    @put(
        path=PUT_CHAT_URI,
        operation_id='UpdateChat',
        name='chats:update',
        summary='Update a chat',
        description='Update an existing chat by ID (Private method for developers).',
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=ChatResponse,
                description='Successfully updated the chat'
            )
        }
    )
    async def update_chat(
            self,
            gw_state: GatewayState,
            chat_service: ChatService,
            chat_id: Annotated[
                int,
                Parameter(
                    title='Chat ID',
                    description='The ID of the chat to update.'
                )
            ],
            data: Annotated[ChatUpdateRequest, Body(title='Update Chat')]
    ) -> ChatResponse:
        """
        Update existing chat.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            chat_service: Chat service
            chat_id: Target chat ID
            data: Chat update data

        Returns:
            Updated chat details
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        db_obj = await chat_service.update(data, chat_id)
        return chat_service.to_schema(db_obj, schema_type=ChatResponse)

    @delete(
        path=DELETE_CHAT_URI,
        operation_id='DeleteChat',
        name='chats:delete',
        summary='Delete a chat',
        description='Delete a chat by ID (Private method for developers).',
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=ChatResponse,
                description='Successfully deleted the chat'
            )
        }
    )
    async def delete_chat(
            self,
            gw_state: GatewayState,
            chat_service: ChatService,
            chat_id: Annotated[int,
            Parameter(
                title='Chat ID',
                description='The ID of the chat to delete.'
            )
            ]
    ) -> None:
        """
        Delete chat record.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            chat_service: Chat service
            chat_id: Target chat ID
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        await chat_service.delete(chat_id)
