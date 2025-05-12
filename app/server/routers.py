from litestar import Router
from litestar.types import ControllerRouterHandler

from app.adapters.inbound.http.controllers import (
    AgendaCalendarsController,
    AgendaCategoriesController,
    AgendaComponentsController,
    AuthSessionsController,
    AuthUsersController,
    ChatController,
    HealthController,
    MessageController,
)
from app.config.constants import API_BASE_PATH

# API v1 endpoints
v1_route_handlers: list[ControllerRouterHandler] = [
    AuthSessionsController, AuthUsersController,
    AgendaCalendarsController, AgendaComponentsController, AgendaCategoriesController,
    ChatController, MessageController
]
api_v1_router = Router(path=f'{API_BASE_PATH}/v1', route_handlers=v1_route_handlers)

# Health check endpoint
api_health_router = Router(path=f'{API_BASE_PATH}/health', route_handlers=[HealthController])

# Main routers collection
routers_list: list[Router] = [
    api_v1_router,
    api_health_router
]
