"""
Reverse-proxy middleware for forwarding requests to external upstream services.

Features:
- Intercepts external routes using `RouteRegistry` and proxies requests to corresponding services.
- Preserves original headers (except hop-by-hop), adding `X-Forwarded-For` when necessary.
- Converts all upstream `Set-Cookie` headers into `litestar.datastructures.Cookie` and attaches them to the request
state.
- Returns upstream error responses (4xx/5xx) directly to the client without touching downstream controllers.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterable
from http.cookies import Morsel, SimpleCookie
from typing import TYPE_CHECKING, cast

from litestar.datastructures import Cookie
from litestar.enums import ScopeType
from litestar.middleware import ASGIMiddleware
from litestar.status_codes import HTTP_400_BAD_REQUEST
from personal_growth_sdk.authorization.constants.http_headers import (
    HEADER_DEVICE_FINGERPRINT,
    HEADER_USER_AGENT,
    HEADER_X_FORWARDED_FOR,
)

from app.config.route_registry import route_registry
from app.lib.context import set_cookies, set_headers, set_upstream
from app.lib.http.http_service import HttpService
from app.lib.logger import logger

if TYPE_CHECKING:
    from collections.abc import Iterable

    from litestar.types import ASGIApp, Receive, Scope, Send

__all__ = ['ReverseProxyMiddleware']

_HOP_BY_HOP = {
    b'connection',
    b'keep-alive',
    b'te',
    b'trailer',
    b'upgrade',
    b'proxy-authenticate',
    b'proxy-authorization',
    b'transfer-encoding',
    b'host',
}

# ── convert once; the rest of the code works with bytes only  ──────────────
HDR_XFF = HEADER_X_FORWARDED_FOR.lower().encode()  # b'x-forwarded-for'
HDR_UA = HEADER_USER_AGENT.lower().encode()  # b'user-agent'
HDR_DFP = HEADER_DEVICE_FINGERPRINT.lower().encode()  # b'x-device-fingerprint'


def copy_request_headers(scope: Scope) -> list[tuple[bytes, bytes]]:
    """
    Extracts and prepares request headers to be forwarded to the upstream service.

    - Removes hop-by-hop headers per RFC 9110 §7.6.1.
    - Ensures presence of `X-Forwarded-For`, `User-Agent`, and `X-Device-Fingerprint`.
    - Maintains original casing and duplicates.

    Args:
        scope: ASGI scope of the incoming request.

    Returns:
        List of raw header tuples suitable for use in HTTP client libraries.
    """

    out: list[tuple[bytes, bytes]] = []
    seen = {
        HDR_XFF: False,
        HDR_UA: False,
        HDR_DFP: False,
    }

    for name, value in scope['headers']:
        if name.lower() in _HOP_BY_HOP:
            continue

        low_name = name.lower()
        if low_name in seen:
            seen[low_name] = True

        out.append((name, value))

    if not seen[HDR_XFF]:
        client_ip = (scope.get('client') or ('',))[0]
        out.append((HDR_XFF, client_ip.encode('ascii')))

    if not seen[HDR_UA]:
        out.append((HDR_UA, b''))

    if not seen[HDR_DFP]:
        out.append((HDR_DFP, b''))

    return out


def _morsel_to_cookie(m: Morsel) -> Cookie:
    """
    Converts a `Morsel` object from `http.cookies` to a Litestar `Cookie`.

    Args:
        m: Parsed morsel containing Set-Cookie data.

    Returns:
        Cookie: Structured representation of the cookie.
    """

    path = m['path'] or '/'
    domain = m['domain'] or None
    secure = bool(m['secure'])
    httponly = bool(m['httponly'])
    samesite = m['samesite'].lower() if m['samesite'] else 'lax'

    # --- Max-Age / Expires --------------------------------------------------
    max_age: int | None = int(m['max-age']) if m['max-age'] else None
    if max_age is None and m['expires']:
        # Upstream returned “Wdy, DD-Mon-YYYY HH:MM:SS GMT”
        expires_dt = datetime.datetime.strptime(
            m['expires'], '%a, %d-%b-%Y %H:%M:%S %Z'
        ).replace(tzinfo=datetime.UTC)
        max_age = int((expires_dt - datetime.datetime.now(datetime.UTC)).total_seconds())

    return Cookie(
        key=m.key,
        value=m.value,
        path=path,
        domain=domain,
        secure=secure,
        httponly=httponly,
        samesite=samesite,
        max_age=max_age,
    )


def parse_set_cookie(headers: Iterable[str]) -> list[Cookie]:
    """
    Parses all Set-Cookie headers from the upstream response.

    Args:
        headers: Iterable of Set-Cookie header strings.

    Returns:
        List of `Cookie` objects compatible with Litestar's response interface.
    """

    cookies: list[Cookie] = []
    for header in headers:
        jar = SimpleCookie()
        jar.load(header)
        for morsel in jar.values():
            cookies.append(_morsel_to_cookie(morsel))
    return cookies


def clean_headers(raw: list[tuple[bytes, bytes]]) -> dict[str, str]:
    """
    Prepares a safe response header dictionary for use in Litestar.

    Drops headers that should not be manually forwarded, such as:
    - `Set-Cookie` (handled separately)
    - `Content-Length` (auto-managed by Litestar)
    - `Date`, `Server`

    Args:
        raw: List of raw response headers.

    Returns:
        Dictionary of sanitized headers.
    """

    drop = {
        b'set-cookie',
        b'content-length',
        b'date',
        b'server',
    }
    hdr: dict[str, str] = {}
    for name, value in raw:
        lname = name.lower()
        if lname in drop:
            continue

        hdr.setdefault(name.decode(), value.decode())
    return hdr


async def read_body(receive: Receive) -> bytes:
    """
    Reads the entire body of the incoming request.

    Args:
        receive: ASGI receive callable.

    Returns:
        The complete request body as bytes.
    """

    chunks: list[bytes] = []

    while True:
        message = await receive()
        if message['type'] != 'http.request':
            # ignore lifespan / websocket messages
            continue

        # tell the type-checker: “this **is** bytes”
        chunk = cast('bytes', message.get('body', b''))
        chunks.append(chunk)

        if not message.get('more_body', False):
            break

    return b''.join(chunks)


def replay_body(body: bytes) -> Receive:
    """
    Reconstructs a `receive()` coroutine that replays the given body exactly once.

    Useful for passing the same request payload downstream after reading it once.

    Args:
        body: Request body previously read.

    Returns:
        A coroutine-compatible object simulating a fresh body stream.
    """

    consumed = False

    async def _wrapper() -> dict:
        nonlocal consumed
        if not consumed:
            consumed = True
            return {'type': 'http.request', 'body': body, 'more_body': False}
        return {'type': 'http.request', 'body': b'', 'more_body': False}

    return _wrapper


async def direct_send(send: Send, resp):
    """
    Forwards the upstream response directly to the client as-is.

    Used for error responses to bypass application controller logic.

    Args:
        send: ASGI send callable.
        resp: HTTP response object returned by upstream.
    """

    await send(
        {
            'type': 'http.response.start',
            'status': resp.status_code,
            'headers': list(resp.headers.raw),
        }
    )
    await send({'type': 'http.response.body', 'body': resp.content})


class ReverseProxyMiddleware(ASGIMiddleware):
    """
    ASGI middleware that turns the gateway into a lightweight reverse-proxy.

    Responsibilities:
    - Routes matching external upstream definitions are proxied to the appropriate target.
    - Reads the full request body and headers once, replicating them for upstream transmission.
    - Parses upstream responses and makes payload, headers, and cookies available in request scope.
    - Short-circuits error responses (HTTP ≥ 400), returning them unchanged to the client.

    This is especially useful for proxying user messages, calendar operations, or profile actions
    to services like Agenda, Auth, or ML subsystems, without duplicating internal logic.
    """

    scopes = (ScopeType.HTTP,)

    async def handle(
            self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp
    ) -> None:
        """
        Process an incoming HTTP request and proxy it to an upstream service if applicable.

        This method:
        - Resolves whether the request matches a registered external service.
        - If not, it passes the request through to the next ASGI app.
        - If matched:
            * It reads and stores the request body.
            * Copies all relevant headers (preserving necessary metadata).
            * Forwards the request to the upstream using the `HttpService`.
            * If the upstream responds with an error (status >= 400), it streams the
              response directly back to the client.
            * Otherwise, it attaches upstream content, headers, and cookies to the
              request scope for downstream processing.

        Args:
            scope: The ASGI scope of the current request.
            receive: The ASGI receive callable.
            send: The ASGI send callable.
            next_app: The next ASGI application in the middleware chain.

        Returns:
            None. The response is either streamed from the upstream or passed to the next app.
        """

        method, path = scope['method'], scope['path']
        upstream, tail = route_registry.resolve(method, path)

        # ------------- local route -----------------------------------------
        if upstream is None:
            await next_app(scope, receive, send)
            return

        target = f'{upstream}{tail}'
        logger.debug('Proxy → %s %s', method, target)

        # ------------- build proxied request -------------------------------
        body = await read_body(receive)
        req_headers = copy_request_headers(scope)

        resp = await HttpService.raw_request(
            method=method,
            url=target,
            headers=req_headers,
            content=body or None,
            params=scope['query_string'].decode() or None,
        )

        # ------------- error? return upstream response as-is ---------------
        if resp.status_code >= HTTP_400_BAD_REQUEST:
            await direct_send(send, resp)
            return

        # ------------- success → pass data downstream ----------------------
        set_upstream(scope, resp.content)
        set_cookies(scope, parse_set_cookie(resp.headers.get_list('set-cookie')))

        hdr_dict = clean_headers(resp.headers.raw)
        set_headers(scope, hdr_dict)

        await next_app(scope, replay_body(body), send)
