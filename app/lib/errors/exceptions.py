"""
Application-specific exception classes.
Organized by error categories with proper HTTP status codes.
"""

from typing import Any

from litestar.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
)

__all__ = [  # noqa:  RUF022
    # base
    'AppException',
    'InitializationError',
    # JWT
    'JWTException',
    'JWTAbsentException',
    'JWTCannotDecodeException',
    'JWTExpiredException',
    'JWTInvalidException',
    # users
    'UserException',
    'UserAccessDeniedException',
    # HTTP
    'HttpServiceException',
    'HttpRequestTimeoutError',
    'HttpClientError',
    'HttpServerError',
    # AI
    'AIAgentError',
    'UnsupportedAgentError',
]


class AppException(Exception):  # noqa: N818 - сохранено для обратной совместимости
    """
    Base exception class for application errors.
    """

    def __init__(self, message: str = '', details: Any = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)


class InitializationError(AppException):
    """Raised when a class or another cannot be configured in lifespan."""

    def __init__(self, message: str | None = None, details: Any = None):
        message = message or getattr(self, 'message', '')
        super().__init__(message=message, details=details)


# Authentication/Authorization Exceptions
class JWTException(AppException):
    """
    Base JWT-related exception.
    """

    status_code = HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str | None = None, details: Any = None):
        message = message or getattr(self, 'message', '')
        super().__init__(message=message, details=details)


class JWTAbsentException(JWTException):
    """
    Raised when JWT token is missing.
    """

    status_code = HTTP_401_UNAUTHORIZED
    message = 'Authorization token is missing'


class JWTCannotDecodeException(JWTException):
    """
    Raised when JWT decoding fails.
    """

    message = 'Failed to decode JWT token'


class JWTExpiredException(JWTException):
    """
    Raised when JWT token has expired.
    """

    status_code = HTTP_401_UNAUTHORIZED
    message = 'Token has expired'


class JWTInvalidException(JWTException):
    """
    Raised when JWT token is invalid.
    """

    status_code = HTTP_401_UNAUTHORIZED
    message = 'Invalid token'


# User-related Exceptions
class UserException(AppException):
    """
    Base user-related exception.
    """

    status_code = HTTP_400_BAD_REQUEST
    message = 'Ошибка пользователя'

    def __init__(self, message: str | None = None, details: Any = None):
        message = message or getattr(self, 'message', '')
        super().__init__(message=message, details=details)


class UserAccessDeniedException(UserException):
    """
    Raised when user lacks permissions.
    """

    status_code = HTTP_403_FORBIDDEN
    message = 'Insufficient permissions'


# HTTP Service exception
class HttpServiceException(AppException):
    """
    Base exception class for HTTP service errors.
    """

    status_code: int = HTTP_400_BAD_REQUEST
    message: str = 'HTTP Service Error'

    def __init__(self, message: str | None = None, details: Any = None):
        message = message or getattr(self, 'message', '')
        super().__init__(message=message, details=details)


class HttpRequestTimeoutError(HttpServiceException):
    """
    Exception raised when HTTP request times out.
    """

    status_code = HTTP_504_GATEWAY_TIMEOUT
    message = 'Request timed out'


class HttpClientError(HttpServiceException):
    """
    Exception for client-related HTTP errors
    """

    status_code = HTTP_400_BAD_REQUEST
    message = 'Bad request'


class HttpServerError(HttpServiceException):
    """
    Exception for server-related HTTP errors.
    """

    status_code = HTTP_503_SERVICE_UNAVAILABLE
    message = 'Service unavailable'


# AI Agent Exceptions
class AIAgentError(AppException):
    """
    Generic AI gateway exception.
    """

    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    message = 'AI Agent error'


class UnsupportedAgentError(AIAgentError):
    """
    The requested AI gateway name is not registered in the factory.
    """

    def __init__(self, message: str | None = None, details: Any = None):
        message = message or getattr(self, 'message', '')
        super().__init__(message=f'Gateway `{message}` is not supported.', details=details)
