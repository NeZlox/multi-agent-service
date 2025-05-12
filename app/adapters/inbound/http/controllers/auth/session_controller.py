"""
Authentication session endpoints proxy controller.

This controller provides OpenAPI documentation and routing for session-related
operations from the upstream Auth service.

Responsibilities:
- Handle user login and token generation
- Handle token refresh
- Support session revocation (single and global)

All operations are proxied via `ReverseProxyMiddleware` and use cookies for token delivery.
"""

from __future__ import annotations

from typing import Annotated

import msgspec
from litestar import Controller, delete, post, put
from litestar.datastructures import Cookie
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.params import Body
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT
from personal_growth_sdk.authorization.constants.authentication import AUTH_ACCESS_TOKEN_KEY, AUTH_REFRESH_TOKEN_KEY
from personal_growth_sdk.authorization.schemas import UserLoginRequest, UserResponse

from app.adapters.inbound.http.urls.auth.auth_session_urls import (
    DELETE_SESSIONS,
    DELETE_SESSIONS_ALL,
    POST_SESSIONS,
    PREFIX,
    PUT_SESSIONS,
)
from app.dto.user_dto import UserResponseDTO
from app.infrastructure.di.providers import gateway_state_provider
from app.lib.context import GatewayState

__all__ = ['AuthSessionsController']


class AuthSessionsController(Controller):
    """
    Proxy controller for session-based authentication operations.

    Attributes:
        path: Base API path for session routes
        dependencies: Injects gateway context
        tags: OpenAPI tags
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'gw_state': Provide(gateway_state_provider, sync_to_thread=False)
    }
    tags = ['Authentication · Session']  # noqa: RUF012

    @post(
        path=POST_SESSIONS,
        operation_id='CreateAuthToken',
        summary='User login',
        description='Authenticate user and get access/refresh token pair',
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                description='Successfully authenticated',
                data_container=UserResponse
            )
        },
        response_cookies=[
            Cookie(
                key=AUTH_ACCESS_TOKEN_KEY,
                description='Access token for authorization',
                documentation_only=True,
            ),
            Cookie(
                key=AUTH_REFRESH_TOKEN_KEY,
                description='Refresh token for renewing access',
                documentation_only=True,
            ),
        ],
        return_dto=UserResponseDTO

    )
    async def login(
            self,
            data: UserLoginRequest,  # noqa: ARG002
            gw_state: GatewayState

    ) -> Response[UserResponse]:
        """
        Authenticate user and return session cookies.

        Args:
            data: Login payload
            gw_state: Gateway response context with upstream user and cookies

        Returns:
            Response with user info and auth cookies
        """

        user = msgspec.json.decode(gw_state.upstream_raw, type=UserResponse)
        return Response(content=user, cookies=gw_state.upstream_cookies)

    @put(
        path=PUT_SESSIONS,
        operation_id='RefreshAuthToken',
        summary='Refresh access token',
        description='Get new access token using refresh token',
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=None,
                description='Token refreshed'
            )
        },
        response_cookies=[
            Cookie(
                key=AUTH_ACCESS_TOKEN_KEY,
                description='New Access token (if successfully refreshed)',
                documentation_only=True,
            ),
            Cookie(
                key=AUTH_REFRESH_TOKEN_KEY,
                description='Possibly new Refresh token (if server reissues it)',
                documentation_only=True,
            ),
        ]
    )
    async def refresh_token(
            self,
            user_id: Annotated[  # noqa: ARG002
                int,
                Body(
                    title='User ID',
                    description='The ID of the user to retrieve.'
                )

            ],
            gw_state: GatewayState
    ) -> Response[None]:
        """
        Refresh the user's session token.

        Args:
            user_id: ID of the user (used for schema consistency)
            gw_state: Gateway response context

        Returns:
            Empty response with updated cookies
        """

        return Response(content=None, cookies=gw_state.upstream_cookies)

    @delete(
        path=DELETE_SESSIONS,
        operation_id='RevokeAuthToken',
        summary='User logout',
        description='Invalidate current session and revoke tokens',
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=None,
                description='Successfully logged out'
            )
        },
        response_cookies=[
            Cookie(
                key=AUTH_ACCESS_TOKEN_KEY,
                description='Access token removed',
                documentation_only=True
            ),
            Cookie(
                key=AUTH_REFRESH_TOKEN_KEY,
                description='Refresh token removed',
                documentation_only=True
            ),
        ]
    )
    async def logout(
            self,
            gw_state: GatewayState
    ) -> Response[None]:
        """
        Logout user and revoke the current session.

        Args:
            gw_state: Gateway state with cookie context

        Returns:
            Empty response with cookies cleared
        """

        return Response(content=None, cookies=gw_state.upstream_cookies)

    @delete(
        path=DELETE_SESSIONS_ALL,
        operation_id='RevokeAllSessions',
        summary='Terminate all sessions',
        description='Invalidate all active sessions for current user',
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=None,
                description='All sessions terminated'
            )
        },
        response_cookies=[
            Cookie(
                key=AUTH_ACCESS_TOKEN_KEY,
                description='Access token removed',
                documentation_only=True
            ),
            Cookie(
                key=AUTH_REFRESH_TOKEN_KEY,
                description='Refresh token removed',
                documentation_only=True
            ),
        ]
    )
    async def terminate_all_sessions(
            self,
            gw_state: GatewayState
    ) -> Response[None]:
        """
        Revoke all user sessions (global logout).

        Args:
            gw_state: Gateway state with cookie context

        Returns:
            Empty response indicating all sessions have been revoked
        """

        return Response(content=None, cookies=gw_state.upstream_cookies)
