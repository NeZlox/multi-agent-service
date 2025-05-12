"""
Register reverse-proxy routing for the Auth microservice.

This module configures:
- Proxy prefix for Auth service
- Rewrite rules for user registration and profile endpoints

These rules allow the gateway to rewrite and forward requests correctly.
"""

import re

from app.config.base_settings import get_settings
from app.config.route_registry import HTTPMethod, RewriteRule, route_registry

settings = get_settings()

route_registry.register(
    prefix='/api/v1/auth',
    upstream_base=settings.app.AUTH_SERVICE_URL,
    rules=[
        RewriteRule(HTTPMethod.POST, re.compile(r'^/users/'), '/api/v1/users/register'),
        RewriteRule(HTTPMethod.GET, re.compile(r'^/users/me'), '/api/v1/users/me')
    ],
)
