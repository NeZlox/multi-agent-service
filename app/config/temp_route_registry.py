"""
Central route_registry for reverse proxy routing rules and public routes.

This module allows:
- Declaring upstream services and route prefixes for proxying.
- Registering rewrite rules for dynamic path translation.
- Marking specific routes as public (bypassing authentication).
- Resolving incoming request paths to their respective upstream targets.

Used primarily by middleware to determine whether a request should be
proxied, rewritten, or passed to local controllers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from re import Pattern

from app.config.base_settings import get_settings
from app.lib.singleton import SingletonMeta

settings = get_settings()

__all__ = ['RouteRegistry']


class HTTPMethod(StrEnum):
    """
    Enumeration of supported HTTP methods with wildcard support.
    """

    ANY = '*'
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'

    @classmethod
    def normalize(cls, value: str) -> HTTPMethod:
        """
        Normalize a string to an HTTPMethod enum.

        Accepts any case-insensitive string (e.g., 'get', 'POST').
        Returns '*' as-is.

        Args:
            value: HTTP method string.

        Returns:
            Normalized HTTPMethod.

        Raises:
            ValueError: If the method is unsupported.
        """

        if value == '*':
            return cls.ANY
        try:
            return cls[value.upper()]
        except KeyError as exc:
            raise ValueError(f'Unsupported HTTP method: {value}') from exc


# ------------------------------------------------------------------ #
#  Re-write rules                                                    #
# ------------------------------------------------------------------ #
@dataclass(frozen=True, slots=True)
class RewriteRule:
    """
    Rule for rewriting request paths based on method and regex match.
    """

    method: HTTPMethod
    pattern: Pattern[str]
    replace: str

    def matches(self, method: str, tail: str) -> bool:
        """
        Determine whether the rule matches a given method and path tail.

        Args:
            method: HTTP method.
            tail: Remaining part of the path after the prefix.

        Returns:
            True if the rule matches, else False.
        """

        m = HTTPMethod.normalize(method)
        return (self.method is HTTPMethod.ANY or self.method is m) and self.pattern.match(tail)


# ------------------------------------------------------------------ #
#  Public (unauthenticated) routes                                   #
# ------------------------------------------------------------------ #
@dataclass(frozen=True, slots=True)
class PublicRoute:
    """
    Route definition that does not require authentication.
    """

    method: HTTPMethod
    prefix: str

    def allows(self, method: str, path: str) -> bool:
        """
        Check if the given method and path match this public route.

        Args:
            method: HTTP method.
            path: Full request path.

        Returns:
            True if route is publicly accessible.
        """

        m = HTTPMethod.normalize(method)
        return (self.method is HTTPMethod.ANY or self.method is m) and (
                path == self.prefix or path.startswith(self.prefix.rstrip('*'))
        )


@dataclass(slots=True)
class ServiceRoutes:
    """
    Container for proxy rules and rewrite options for an upstream service.
    """

    upstream_base: str
    rules: list[RewriteRule] = field(default_factory=list)
    strip_url: str | Pattern[str] | None = None

    def rewrite_tail(self, method: str, tail: str) -> tuple[str, bool]:
        """
        Apply rewrite rules to the tail of the request path.

        Args:
            method: HTTP method.
            tail: Path after the service prefix.

        Returns:
            A tuple of (new path, match flag).
        """

        for rule in self.rules:
            if rule.matches(method, tail):
                return rule.replace, True
        return tail, False

    def rewrite_upstream(self, path: str) -> str:
        """
        Strip prefix from path before forwarding to upstream.

        Args:
            path: Full request path.

        Returns:
            Modified path with prefix removed if applicable.
        """

        if not self.strip_url:
            return path

        if isinstance(self.strip_url, str):
            return path.replace(self.strip_url, '', 1)

        # compiled re-pattern - remove exactly one match
        return self.strip_url.sub('', path, count=1)


class RouteRegistry(metaclass=SingletonMeta):
    """
    Singleton route_registry of proxy routes and public access rules.
    """

    def __init__(self) -> None:
        self._services: dict[str, ServiceRoutes] = {}
        self._public: list[PublicRoute] = []

    def add_public(self, method: str, path: str) -> None:
        """
        Register a public route that does not require authentication.

        Args:
            method: HTTP method (e.g. 'GET', 'POST', '*').
            path: Path or prefix to mark as public.
        """

        self._public.append(PublicRoute(HTTPMethod.normalize(method), path))

    def is_public(self, method: str | HTTPMethod, path: str) -> bool:
        """
        Check if a route is publicly accessible.

        Args:
            method: HTTP method.
            path: Request path.

        Returns:
            True if the route is public.
        """

        return any(r.allows(method, path) for r in self._public)

    def register(
            self,
            prefix: str,
            upstream_base: str,
            rules: list[RewriteRule] | None = None,
            strip_url: str | Pattern[str] | None = None,
    ) -> None:
        """
        Register a new upstream service with optional rewrite rules.

        Args:
            prefix: Path prefix to match incoming requests.
            upstream_base: Target service base URL.
            rules: List of rewrite rules.
            strip_url: Optional prefix/regex to strip from path before forwarding.

        Raises:
            ValueError: If the prefix is already registered.
        """

        if prefix in self._services:
            raise ValueError(f'Prefix {prefix} already registered')
        self._services[prefix] = ServiceRoutes(upstream_base, rules or [], strip_url)

    def resolve(self, method: str, path: str) -> tuple[str | None, str | None]:
        """
        Resolve a request to its upstream target and modified path.

        Args:
            method: HTTP method.
            path: Request path.

        Returns:
            Tuple of (upstream URL, rewritten path) or (None, None) if not matched.
        """

        for prefix, svc in self._services.items():
            if path.startswith(prefix):
                tail = path[len(prefix):]
                new_tail, matched = svc.rewrite_tail(method, tail)
                path = svc.rewrite_upstream(path)
                if matched:
                    return svc.upstream_base, new_tail

                return svc.upstream_base, path

        return None, None


# ------------------------- создаём глобальный реестр -----------------------
registry = RouteRegistry()

# --- auth-service ----------------------------------------------------------

registry.register(
    prefix='/api/v1/auth',
    upstream_base=settings.app.AUTH_SERVICE_URL,
    rules=[
        RewriteRule(HTTPMethod.POST, re.compile(r'^/users/'), '/api/v1/users/register'),
        RewriteRule(HTTPMethod.GET, re.compile(r'^/users/me'), '/api/v1/users/me')
    ],
)

registry.register(
    prefix='/api/v1/agenda',
    strip_url=r'/agenda',
    upstream_base=settings.app.AGENDA_SERVICE_URL
)

registry.register(
    prefix='/api/v1/snapshot',
    upstream_base=settings.app.SNAPSHOT_SERVICE_URL
)

# static assets, version docs, etc.
for p in ('/docs', '/openapi.json', '/docs/openapi.json'):
    registry.add_public('*', p)

# specific unauthenticated endpoints
registry.add_public('POST', '/api/v1/auth/sessions')
registry.add_public('PUT', '/api/v1/auth/sessions')
registry.add_public('POST', '/api/v1/users/register')
registry.add_public('GET', '/api/health/*')
