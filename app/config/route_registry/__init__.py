"""
Public API for the reverse proxy route registry.

This module exposes a shared `route_registry` singleton with methods to:
- Register upstream services (`.register()`)
- Register public unauthenticated routes (`.add_public()`)
- Resolve incoming paths to upstream routes (`.resolve()`)

To populate the registry, call `init_route_registry()` once during application startup.
This will import and register all proxy route declarations via `load_all()`.
"""

from __future__ import annotations

from functools import lru_cache

from .core import HTTPMethod, RewriteRule, RouteRegistry
from .loader import load_all

# Singleton instance of RouteRegistry used across the application
route_registry = RouteRegistry()


# Load all proxy route declarations on import
@lru_cache(maxsize=1)
def init_route_registry() -> None:
    """
    Initialize the global proxy route registry once.

    This function uses LRU cache to ensure it's executed only once,
    regardless of how many times it's called.
    """
    load_all()


__all__ = ['HTTPMethod', 'RewriteRule', 'RouteRegistry', 'init_route_registry', 'route_registry']
