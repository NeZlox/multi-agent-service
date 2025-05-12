"""
Register reverse-proxy routing for the Agenda microservice.

This module configures:
- Proxy prefix for the Agenda service
- Optional URL prefix stripping

Used by the `RouteRegistry` to determine where and how to forward Agenda-related requests.
"""

from app.config.base_settings import get_settings
from app.config.route_registry import route_registry

settings = get_settings()

route_registry.register(
    prefix='/api/v1/agenda',
    strip_url=r'/agenda',
    upstream_base=settings.app.AGENDA_SERVICE_URL
)
