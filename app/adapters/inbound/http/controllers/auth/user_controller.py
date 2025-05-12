"""
Authentication user endpoints proxy controller.

This controller provides OpenAPI documentation and routing for user-related
authentication operations from the upstream Auth service.

Responsibilities:
- Register new users
- Retrieve current authenticated user profile

All responses are proxied via `ReverseProxyMiddleware` and decoded from
`gw_state.upstream_raw`.
"""

from __future__ import annotations

from typing import Annotated

import msgspec
from litestar import Controller, Request, get, post
from litestar.di import Provide
from litestar.dto import DTOConfig, MsgspecDTO
from litestar.openapi import ResponseSpec
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from personal_growth_sdk.authorization.schemas import UserCreateRequest, UserResponse

from app.adapters.inbound.http.urls.auth.auth_user_urls import GET_CURRENT_USER_URI, POST_REGISTER_USER_URI, PREFIX

__all__ = ['AuthUsersController']

from app.infrastructure.di.providers import gateway_state_provider, role_required
from app.lib.context import GatewayState
from app.lib.security import RoleGroup


class AuthUsersController(Controller):
    """
    Proxy controller for user authentication operations.

    Attributes:
        path: Base API path for user-related routes
        dependencies: Injects gateway context
        tags: OpenAPI tags
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'gw_state': Provide(gateway_state_provider, sync_to_thread=False)
    }
    tags = ['Authentication · Users']  # noqa: RUF012

    @post(
        path=POST_REGISTER_USER_URI,
        operation_id='RegisterUser',
        name='users:register',
        summary='Register new user',
        description='Public user registration endpoint with email verification',
        status_code=HTTP_201_CREATED,
        responses={
            HTTP_201_CREATED: ResponseSpec(
                data_container=UserResponse,
                description='Successfully registered new user'
            )
        }
    )
    async def register_user(
            self,
            data: Annotated[UserCreateRequest, Body(title='Register User')],  # noqa: ARG002
            request: Request
    ) -> UserResponse:
        """
        Register a new user account.

        Args:
            data: Registration payload
            request: Incoming request (used to extract upstream response)

        Returns:
            The created user profile
        """

        user = msgspec.json.decode(request.state.resp, type=UserResponse)
        return user

    @get(
        path=GET_CURRENT_USER_URI,
        operation_id='GetCurrentUser',
        name='users:me',
        summary='Get current user profile',
        description='Retrieve authenticated user profile information',
        dependencies={'_': Provide(role_required(RoleGroup.COMMON))},
        status_code=HTTP_200_OK,
        return_dto=MsgspecDTO[Annotated[UserResponse, DTOConfig(exclude={'active_sessions'})]],
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=UserResponse,
                description='Successfully retrieved user profile'
            )
        }
    )
    async def get_me(
            self,
            gw_state: GatewayState,
            _: None
    ) -> UserResponse:
        """
        Return the currently authenticated user's profile.

        Args:
            gw_state: Gateway context including authenticated user.

        Returns:
            UserResponse: The authenticated user's data.
        """

        return gw_state.auth_user
