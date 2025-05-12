"""
Request-scoped state management utilities for the gateway.

This module defines the `GatewayState` structure and helper functions for storing and retrieving
request-local metadata in `scope.state`.

Used by middlewares (e.g., AuthGuard, ReverseProxy) to persist:
- authenticated user (`auth_user`)
- raw upstream response payload (`upstream_raw`)
- response cookies (`upstream_cookies`)
- response headers (`upstream_headers`)

This enables consistent downstream access to upstream responses, headers, and authentication
without tightly coupling controllers to middleware logic.
"""

from litestar import Request
from litestar.datastructures import Cookie
from litestar.types import Scope
from msgspec import Struct
from personal_growth_sdk.authorization.schemas import UserResponse

__all__ = [
    'GatewayState',
    'gather_state',
    'get_cookies',
    'get_upstream',
    'get_user',
    'set_cookies',
    'set_upstream',
    'set_user',
]

_USER_KEY = 'auth_user'
_RESP_KEY = 'upstream_raw'
_COOKIE_KEY = 'upstream_cookies'
_HDR_KEY = 'upstream_headers'


class GatewayState(Struct, frozen=True):
    """
    Everything middleware saved into ``scope.state`` for a request.
    """

    auth_user: UserResponse | None = None
    upstream_raw: bytes | None = None
    upstream_cookies: list[Cookie] | None = None
    upstream_headers: dict[str, str] | None = None


def _state(scope: Scope) -> Scope:
    """
    Internal helper to access or create the `scope.state` dictionary.

    Args:
        scope: ASGI request scope.

    Returns:
        Mutable dictionary representing the request-local state.
    """

    return scope.setdefault('state', {})


def set_user(scope: Scope, user: UserResponse) -> None:
    """
    Stores the authenticated user object into the request state.

    Args:
        scope: ASGI request scope.
        user: Authenticated user information.
    """

    _state(scope)[_USER_KEY] = user


def get_user(request) -> UserResponse | None:
    """
    Retrieves the authenticated user from request state.

    Args:
        request: Incoming request object.

    Returns:
        UserResponse if available, else None.
    """

    return request.state.get(_USER_KEY)


def set_upstream(scope: Scope, raw: bytes) -> None:
    """
    Stores raw upstream response payload into request state.

    Args:
        scope: ASGI request scope.
        raw: Response content in bytes.
    """

    _state(scope)[_RESP_KEY] = raw


def get_upstream(request: Request) -> bytes:
    """
    Fetches previously stored raw upstream response body.

    Args:
        request: Incoming request object.

    Returns:
        Raw response content.
    """

    return request.state.get(_RESP_KEY)


def set_cookies(scope: Scope, cookies: list[Cookie]) -> None:
    """
    Stores cookies parsed from upstream response.

    Args:
        scope: ASGI request scope.
        cookies: List of `Cookie` instances.
    """

    _state(scope)[_COOKIE_KEY] = cookies


def get_cookies(request: Request) -> list[Cookie]:
    """
    Retrieves the stored upstream cookies.

    Args:
        request: Incoming request object.

    Returns:
        List of `Cookie` instances or empty list.
    """

    return request.state.get(_COOKIE_KEY)


def set_headers(scope: Scope, hdrs: dict[str, str]) -> None:
    """
    Stores custom headers from upstream response for use in downstream response.

    Args:
        scope: ASGI request scope.
        hdrs: Dictionary of headers.
    """

    _state(scope)[_HDR_KEY] = hdrs


def get_headers(request: Request) -> dict[str, str] | None:
    """
    Retrieves upstream headers saved during proxy processing.

    Args:
        request: Incoming request object.

    Returns:
        Dictionary of headers or None.
    """
    return request.state.get(_HDR_KEY)


def gather_state(request) -> GatewayState:
    """
    Aggregates all proxy-related request state into an immutable data object.

    Args:
        request: Incoming request object.

    Returns:
        GatewayState: Consolidated snapshot of all request metadata from middleware.
    """

    return GatewayState(
        auth_user=get_user(request),
        upstream_raw=get_upstream(request),
        upstream_cookies=get_cookies(request),
        upstream_headers=get_headers(request),
    )
