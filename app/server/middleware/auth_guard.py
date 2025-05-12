"""
Authentication guard middleware.

Intercepts all non-public routes to extract and validate the access token from cookies.
On success, attaches the authenticated user to the request scope for downstream access.
"""

from litestar import Request
from litestar.enums import ScopeType
from litestar.middleware import ASGIMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send

from app.config.route_registry import route_registry
from app.infrastructure.di.providers import provide_authenticate_service
from app.lib.context import set_user

__all__ = ['AuthGuardMiddleware']

from app.lib.logger import logger


class AuthGuardMiddleware(ASGIMiddleware):
    """
    Middleware that enforces authentication on all non-public endpoints.
    """

    scopes = (ScopeType.HTTP,)

    async def handle(self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp):
        """
        Intercepts the request to validate JWT and populate the user context.

        Args:
            scope: ASGI scope
            receive: ASGI receive callable
            send: ASGI send callable
            next_app: The next ASGI application in the middleware chain
        """

        if route_registry.is_public(scope['method'], scope['path']):
            await next_app(scope, receive, send)
            return

        logger.debug('\n\nAuthGuardMiddleware\n\n')
        request = Request(scope)
        auth_service = provide_authenticate_service()
        user = await auth_service.get_authenticated_user(request)
        set_user(scope, user)
        logger.debug('AuthGuard OK → user_id=%s path=%s', user.id, scope['path'])
        await next_app(scope, receive, send)
