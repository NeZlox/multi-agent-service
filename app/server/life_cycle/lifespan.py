"""
Manages core application lifecycle events.
Handles startup/shutdown logging and hooks.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from litestar import Litestar

from app.application.ai_agent_gateway import AIAgentFactory
from app.config.base_settings import get_settings
from app.config.route_registry import init_route_registry
from app.lib.errors.exceptions import InitializationError
from app.lib.http import HttpService
from app.lib.logger import logger

__all__ = ['provide_lifespan_service']

settings = get_settings()


@asynccontextmanager
async def provide_lifespan_service(app: Litestar) -> AsyncGenerator[None, None]:
    """
    Main lifespan manager for application events.
    """

    await logger.ainfo('Initializing application resources')

    try:
        init_route_registry()
        await logger.ainfo('Proxy route registry loaded')
    except Exception as exc:
        await logger.aerror('Failed to load proxy route registry: %s', str(exc))
        raise InitializationError('Could not initialize route registry') from exc

    try:
        new_http_service = HttpService()
        await new_http_service.initialize_resources()
        app.state.base_service = new_http_service
        await logger.ainfo('HttpService initialized successfully.')
    except Exception as exc:
        await logger.aerror('Failed to initialize HttpService: %s', str(exc))
        raise InitializationError('Could not initialize HttpService') from exc

    try:
        new_agent_factory = AIAgentFactory()
        app.state.gateways_factory = new_agent_factory
        await logger.ainfo('AI Agent Factory initialized successfully')
    except Exception as exc:
        await logger.aerror('Failed to initialize AI Agent Factory: %s', str(exc))
        raise InitializationError('Could not initialize AI Agent Factory') from exc

    await logger.ainfo('Server is starting')
    try:
        yield
    finally:
        await logger.ainfo('Cleaning up application resources')
        await HttpService.cleanup_resources()
        await logger.ainfo('Server is shutting down')
