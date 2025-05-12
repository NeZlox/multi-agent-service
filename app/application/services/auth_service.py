"""
Auth service — proxies access token introspection requests to the external
authorization system (Auth microservice).

Primarily used to:
- Verify access tokens (via cookie)
- Retrieve the current user from the upstream Auth API

Can also be pinged as a health check.

Note:
    This service is stateless and can be safely used as a singleton.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from personal_growth_sdk.authorization.constants.authentication import AUTH_ACCESS_TOKEN_KEY
from personal_growth_sdk.authorization.schemas import UserResponse

from app.config.base_settings import get_settings
from app.lib.errors.exceptions import JWTAbsentException, JWTInvalidException
from app.lib.http.http_service import HttpService
from app.lib.security import PublicJWTManager
from app.lib.singleton import SingletonMeta

if TYPE_CHECKING:
    from litestar import Request

__all__ = ['AuthService']

settings = get_settings()


class AuthService(metaclass=SingletonMeta):
    """
    Lightweight wrapper around the external authorization (Auth) service.

    Exposes utility methods for validating tokens and fetching the authenticated user.
    """

    def __init__(self, http_service: HttpService):
        self.http_service = http_service

    async def ping(self) -> None:
        """
        Perform a lightweight health check to the Auth service.

        Raises:
            HttpClientError / HttpServerError: On request failure
        """

        url = f'{settings.app.AUTH_SERVICE_URL}/api/health/ping'
        await self.http_service.make_request(url=url, method='GET')

    async def get_authenticated_user(self, request: Request) -> UserResponse:
        """
        Retrieve the currently authenticated user based on access token in cookies.

        Internally:
        - Extracts token from cookies
        - Validates token locally using PublicJWTManager
        - Calls `/api/v1/users/me` from the Auth service to fetch full user info

        Args:
            request: Incoming HTTP request (used to access cookies)

        Returns:
            Parsed `UserResponse` representing the authenticated user.

        Raises:
            JWTAbsentException: If no token is provided
            JWTInvalidException: If the token is expired or malformed
        """

        token = request.cookies.get(AUTH_ACCESS_TOKEN_KEY)
        if token is None:
            raise JWTAbsentException

        try:
            PublicJWTManager.decode_access_token(token)
        except Exception as exc:
            raise JWTInvalidException(details=str(exc)) from exc

        return await self.http_service.make_json_request(
            f'{settings.app.AUTH_SERVICE_URL}/api/v1/users/me',
            method='GET',
            cookies=request.cookies,
            response_type=UserResponse,
        )
