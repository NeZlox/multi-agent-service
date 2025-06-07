"""
Register publicly accessible routes that do not require authentication.

This includes:
- OpenAPI documentation
- Static assets
- Health endpoints
- Session login/refresh endpoints
"""

from app.config.base_settings import get_settings
from app.config.route_registry import route_registry

settings = get_settings()

# Public documentation and schema paths
for p in ('/docs', '/openapi.json', '/docs/openapi.json'):
    route_registry.add_public('*', p)

# Unauthenticated session and health routes
route_registry.add_public('POST', '/api/v1/auth/sessions')
route_registry.add_public('PUT',  '/api/v1/auth/sessions')
route_registry.add_public('POST', '/api/v1/auth/users/register')
route_registry.add_public('GET',  '/api/health/*')
