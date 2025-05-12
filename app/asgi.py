"""
Main application configuration file.
Creates and configures the Litestar application instance.
"""
from litestar import Litestar
from litestar.config.cors import CORSConfig

from app.config.app_settings import get_settings
from app.lib.errors.handlers import collect_exception_handlers
from app.server import openapi, plugins, routers
from app.server.life_cycle import provide_lifespan_service, shutdown_callables_list, startup_callables_list
from app.server.middleware import middlewares_list
from app.server.query_dependencies import create_collection_dependencies

settings = get_settings()


def create_app():
    """
    Factory function for application instance creation.

    Returns:
        Litestar: Configured application instance with:
        - Route handlers
        - OpenAPI docs
        - Exception handling
        - Database plugins
        - Lifecycle hooks
    """

    cors_config = CORSConfig(
        allow_credentials=True
    )
    dependencies = create_collection_dependencies()

    return Litestar(
        route_handlers=routers.routers_list,
        openapi_config=openapi.config if settings.app.MODE != 'PROD' else None,
        debug=settings.app.DEBUG,
        cors_config=cors_config,
        middleware=middlewares_list,
        exception_handlers=collect_exception_handlers(),
        plugins=[
            plugins.alchemy,
            plugins.structlog,
            plugins.granian,
        ],
        lifespan=[provide_lifespan_service],
        dependencies=dependencies,
        on_startup=startup_callables_list,
        on_shutdown=shutdown_callables_list

    )


app = create_app()
