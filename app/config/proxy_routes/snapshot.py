"""
Register reverse-proxy routing for the Snapshot microservice.

This module configures:
- Proxy prefix for the Snapshot service

Allows requests targeting /api/v1/snapshot to be proxied to the corresponding backend.
"""

from app.config.base_settings import get_settings
from app.config.route_registry import route_registry

settings = get_settings()

route_registry.register(
    prefix='/api/v1/snapshot',
    upstream_base=settings.app.SNAPSHOT_SERVICE_URL
)
