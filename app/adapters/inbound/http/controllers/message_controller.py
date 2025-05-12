"""
Chat-message API controller.

This module defines the API controller for managing chat messages.
It provides endpoints to create, retrieve, update, and delete chat messages.

Endpoints are private and require appropriate developer privileges.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from advanced_alchemy.service import OffsetPagination
from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.openapi import ResponseSpec
from litestar.params import Body, Dependency, Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from personal_growth_sdk.multi_agent.schemas import MessageCreateRequest, MessageResponse, MessageUpdateRequest

from app.adapters.inbound.http.urls.message_urls import (
    DELETE_MESSAGE_URI,
    GET_MESSAGE_URI,
    GET_MESSAGES_URI,
    POST_EXCHANGE_URI,
    POST_MESSAGE_URI,
    PREFIX,
    PUT_MESSAGE_URI,
)
from app.application.services import MessageService
from app.infrastructure.di.providers import (
    gateway_state_provider,
    provide_chat_exchange_service,
    provide_message_service,
    provide_snapshot_service,
    role_required,
)
from app.lib.context import GatewayState
from app.lib.security import RoleGroup

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes

__all__ = ['MessageController']


class MessageController(Controller):
    """
    Controller for chat message management.

    Attributes:
        path: Base API path (/messages)
        dependencies: Required service providers
        tags: OpenAPI grouping tag
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'message_service': Provide(provide_message_service),
        'gw_state': Provide(gateway_state_provider, sync_to_thread=False)
    }
    tags = ['Message']  # noqa: RUF012

    @get(
        path=GET_MESSAGES_URI,
        operation_id='GetMessages',
        name='messages:list',
        summary='Get all messages',
        description='Retrieve a list of all chat messages (Private method for developers).',
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=OffsetPagination[MessageResponse],
                description='Successfully retrieved list of chat messages'
            )
        }
    )
    async def get_messages(
            self,
            gw_state: GatewayState,
            message_service: MessageService,
            filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)]
    ) -> OffsetPagination[MessageResponse]:
        """
        Get paginated message list.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            message_service: Message service
            filters: Query filters

        Returns:
            Paginated message results
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        results, total = await message_service.list_and_count(*filters)
        return message_service.to_schema(
            data=results,
            total=total,
            filters=filters,
            schema_type=MessageResponse
        )

    @get(
        path=GET_MESSAGE_URI,
        operation_id='GetMessage',
        name='messages:get_one',
        summary='Get a single message',
        description='Retrieve a single chat message by its ID (Private method for developers).',
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=MessageResponse,
                description='Successfully retrieved the chat message'
            )
        }
    )
    async def get_message(
            self,
            gw_state: GatewayState,
            message_service: MessageService,
            message_id: Annotated[
                int,
                Parameter(
                    title='Message ID',
                    description='The ID of the message to retrieve.'
                )
            ]
    ) -> MessageResponse:
        """
        Get single message details.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            message_service: Message service
            message_id: Target message ID

        Returns:
            Detailed message information
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        db_obj = await message_service.get(message_id)
        return message_service.to_schema(db_obj, schema_type=MessageResponse)

    @post(
        path=POST_MESSAGE_URI,
        operation_id='CreateMessage',
        name='messages:create',
        summary='Create a message',
        description='Create a new chat message with provided data (Private method for developers).',
        status_code=HTTP_201_CREATED,
        responses={
            HTTP_201_CREATED: ResponseSpec(
                data_container=MessageResponse,
                description='Successfully created a new chat message'
            )
        }
    )
    async def create_message(
            self,
            gw_state: GatewayState,
            message_service: MessageService,
            data: Annotated[MessageCreateRequest, Body(title='Create Message')]
    ) -> MessageResponse:
        """
        Create new message record.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            message_service: Message service
            data: Message creation data

        Returns:
            Newly created message details
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        db_obj = await message_service.create(data)
        return message_service.to_schema(db_obj, schema_type=MessageResponse)

    @put(
        path=PUT_MESSAGE_URI,
        operation_id='UpdateMessage',
        name='messages:update',
        summary='Update a message',
        description='Update an existing chat message by ID (Private method for developers).',
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=MessageResponse,
                description='Successfully updated the chat message'
            )
        }
    )
    async def update_message(
            self,
            gw_state: GatewayState,
            message_service: MessageService,
            message_id: Annotated[
                int,
                Parameter(
                    title='Message ID',
                    description='The ID of the message to update.'
                )
            ],
            data: Annotated[MessageUpdateRequest, Body(title='Update Message')]
    ) -> MessageResponse:
        """
        Update existing message.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            message_service: Message service
            message_id: Target message ID
            data: Message update data

        Returns:
            Updated message details
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        db_obj = await message_service.update(data, message_id)
        return message_service.to_schema(db_obj, schema_type=MessageResponse)

    @delete(
        path=DELETE_MESSAGE_URI,
        operation_id='DeleteMessage',
        name='messages:delete',
        summary='Delete a message',
        description='Delete a chat message by ID (Private method for developers).',
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=None,
                description='Successfully deleted the chat message'
            )
        }
    )
    async def delete_message(
            self,
            gw_state: GatewayState,
            message_service: MessageService,
            message_id: Annotated[
                int,
                Parameter(
                    title='Message ID',
                    description='The ID of the message to delete.'
                )
            ]
    ) -> None:
        """
        Delete message record.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            message_service: Message service
            message_id: Target message ID
        """

        await role_required(RoleGroup.PRIVATE)(gw_state)
        await message_service.delete(message_id)

    @post(
        path=POST_EXCHANGE_URI,
        operation_id='ChatExchange',
        name='messages:exchange',
        summary='Send a message and receive the assistant`s reply',
        description='Sends a user message to a chat and returns both the saved user message '
                    'and the assistant`s generated response.',
        status_code=HTTP_201_CREATED,
        responses={
            HTTP_201_CREATED: ResponseSpec(
                data_container=list[MessageResponse],
                description='Returns a list containing the user message and the assistant`s reply.'
            )
        },
    )
    async def exchange(
            self,
            gw_state: GatewayState,
            chat_id: int,
            data: Annotated[MessageCreateRequest, Body(title='User message')],
            message_service: MessageService
    ) -> list[MessageResponse]:
        """
        Send a user message and receive an assistant response.

        Args:
            gw_state: GatewayState containing request authentication and user session information.
            chat_id: ID of the chat where the message is being sent.
            data: User message content to send.
            message_service: Service responsible for message operations.

        Returns:
            A response containing both the user message and the assistant's generated reply.
        """

        await role_required(RoleGroup.COMMON)(gw_state)
        if chat_id != data.chat_id:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)

        chat_exchange_service = provide_chat_exchange_service(
            message_service=message_service,
            snapshot_service=await provide_snapshot_service()
        )
        result = await chat_exchange_service.exchange(
            user_id=gw_state.auth_user.id,
            chat_id=data.chat_id,
            message=data.content
        )

        return result
