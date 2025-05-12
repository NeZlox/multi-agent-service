import time

from litestar.types import ASGIApp, Receive, Scope, Send

from app.lib.logger import logger

__all__ = ['create_request_processing_time_logging_middleware']


def create_request_processing_time_logging_middleware(app: ASGIApp):
    """
    Middleware to log request processing time.
    """

    async def request_processing_time_logging_middleware(scope: Scope, receive: Receive, send: Send):
        start_time = time.perf_counter()
        await app(scope, receive, send)
        end_time = time.perf_counter()

        processing_time = (end_time - start_time) * 1000
        processing_time = f'{processing_time:.2f}ms'

        logger.info(
            'Request processing time',
            processing_time=processing_time,
            request_path=scope['path'],
            method=scope['method'].upper(),
        )

    return request_processing_time_logging_middleware
