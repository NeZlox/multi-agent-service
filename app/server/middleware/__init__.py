"""
Contains application middleware configurations.
Primary purpose is request processing time logging.
"""

from .auth_guard import AuthGuardMiddleware
from .logging import create_request_processing_time_logging_middleware
from .reverse_proxy import ReverseProxyMiddleware

middlewares_list = [
    create_request_processing_time_logging_middleware,
    AuthGuardMiddleware(),
    ReverseProxyMiddleware(),
]

__all__ = ['middlewares_list']
