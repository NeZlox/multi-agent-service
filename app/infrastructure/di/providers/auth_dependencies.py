"""
Dependency provider for AuthService.

Used to inject a pre-configured instance of `AuthService` into the DI container.
"""

from app.application.services import AuthService
from app.lib.http import HttpService

__all__ = ['provide_authenticate_service']


def provide_authenticate_service() -> AuthService:
    """
    Returns a singleton-like AuthService instance, bound to a shared HttpService.

    This provider is designed to be used with dependency injection.

    Returns:
        AuthService: Auth API proxy client
    """

    return AuthService(http_service=HttpService())
