"""
Exception handlers for different error types.
Provides consistent error responses across the application.
"""

import advanced_alchemy.exceptions
import msgspec
from litestar import Request, Response
from litestar.exceptions import HTTPException, NotFoundException, ValidationException

from app.config.base_settings import get_settings
from app.lib.errors import AppException, JWTException, UserException

__all__ = ['collect_exception_handlers']

from app.lib.errors.exceptions import HttpServiceException

settings = get_settings()


def get_error_details(exception):
    """
    Returns error details only in non-production environments.
    """

    return exception.details if settings.app.MODE != 'PROD' or settings.app.DEBUG else None


def default_exception_handler(request: Request, exception: HTTPException) -> Response:  # noqa: ARG001
    """
    Default handler for HTTP exceptions.
    """

    return Response(
        status_code=exception.status_code,
        content={
            'type': type(exception).__name__,
            'message': 'Bad client_info',
            'details': exception.detail,
        }
    )


def http_service_exception_handler(request, exception: HttpServiceException) -> Response:  # noqa: ARG001
    """
    Handler for http requests errors.
    """

    return Response(
        status_code=exception.status_code,
        content={
            'type': type(exception).__name__,
            'message': exception.message,
            'details': get_error_details(exception),
        }
    )


def jwt_exception_handler(request: Request, exception: JWTException) -> Response:  # noqa: ARG001
    """
    Handler for JWT authentication errors.
    """

    return Response(
        status_code=exception.status_code,
        content={
            'type': type(exception).__name__,
            'message': exception.message,
            'details': get_error_details(exception),
        }
    )


def user_exception_handler(request: Request, exception: UserException) -> Response:  # noqa: ARG001
    """
    Handler for user-related errors.
    """

    return Response(
        status_code=exception.status_code,
        content={
            'type': type(exception).__name__,
            'message': exception.message,
            'details': get_error_details(exception),
        }
    )


def app_exception_handler(request: Request, exception: AppException) -> Response:  # noqa: ARG001
    """
    Fallback handler for custom AppExceptions.
    """

    return Response(
        status_code=500,
        content={
            'type': type(exception).__name__,
            'message': exception.message,
            'details': get_error_details(exception),
        }
    )


def validation_exception_handler(request: Request, exception: ValidationException) -> Response:  # noqa: ARG001
    """
    Handler for request validation errors.
    """

    return Response(
        status_code=400,
        content={
            'type': type(exception).__name__,
            'message': exception.detail,
            'details': exception.extra
        }
    )


def msgspec_validation_exception_handler(
        request: Request,  # noqa: ARG001
        exception: msgspec.ValidationError
) -> Response:
    """
    Handler for msgspec validation errors.
    """

    return Response(
        status_code=400,
        content={
            'type': type(exception).__name__,
            'message': exception.__str__(),
            'details': None,
        }
    )


def advanced_alchemy_exception_handler(
        request: Request,  # noqa: ARG001
        exception: advanced_alchemy.exceptions.RepositoryError
) -> Response:
    """
    Handler for database repository errors.
    """

    return Response(
        status_code=500,
        content={
            'type': type(exception).__name__,
            'message': 'Internal server error',
            'details': None,
        }
    )


def litestar_not_found_exception_handler(request: Request, exception: NotFoundException) -> Response:  # noqa: ARG001
    """
    Handler for 404 Not Found errors.
    """

    return Response(
        status_code=404,
        content={
            'type': type(exception).__name__,
            'message': exception.detail,
            'details': None
        }
    )


def collect_exception_handlers():
    """
    Collects all exception handlers into a single mapping.
    """

    return {
        ValidationException: validation_exception_handler,
        HTTPException: default_exception_handler,
        msgspec.ValidationError: msgspec_validation_exception_handler,
        advanced_alchemy.exceptions.RepositoryError: advanced_alchemy_exception_handler,
        NotFoundException: litestar_not_found_exception_handler,
        HttpServiceException: http_service_exception_handler,
        JWTException: jwt_exception_handler,
        UserException: user_exception_handler,
        AppException: app_exception_handler,
    }
