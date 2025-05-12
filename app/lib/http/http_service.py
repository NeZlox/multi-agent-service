"""
Asynchronous HTTP client wrapper for outbound requests.

This module defines `HttpService`, a singleton HTTP client built on top of
httpx.AsyncClient. It centralizes request handling logic, including connection pooling,
response validation, retry mechanisms, and JSON parsing using `msgspec`.
"""

import asyncio
from collections.abc import Callable
from typing import Any, Literal

import httpx
import msgspec
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.lib.errors.exceptions import HttpClientError, HttpRequestTimeoutError, HttpServerError
from app.lib.logger import logger
from app.lib.singleton import SingletonMeta

__all__ = ['HttpService']


class HttpService(metaclass=SingletonMeta):
    """
    Base HTTP service client using httpx.AsyncClient.
    Handles connection pooling, retries, and request/response processing.

    Features:
    - Singleton pattern for connection reuse
    - Automatic JSON serialization/deserialization with msgspec
    - Custom error handling
    - Request timeout and retry logic
    """

    _POOL_SIZE = 100
    _client: httpx.AsyncClient | None = None

    @classmethod
    async def initialize_resources(cls) -> None:
        """
        Initialize the underlying HTTP client with connection pool settings.

        Creates a shared `httpx.AsyncClient` instance used for all outbound requests.
        Must be called before making any requests if no client is present.
        """

        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(
                    max_connections=cls._POOL_SIZE,
                    max_keepalive_connections=cls._POOL_SIZE
                )
            )

    @classmethod
    async def cleanup_resources(cls) -> None:
        """
        Clean up resources by closing the shared HTTP client.

        Ensures connections are closed gracefully and memory is released.
        Should be called on application shutdown.
        """

        if cls._client:
            await cls._client.aclose()
            cls._client = None

    @classmethod
    def _normalize_params(cls, params: dict | None) -> dict:
        """
        Normalize query parameters for HTTP requests.

        Specifically converts all boolean values into lowercase string literals
        ('true' / 'false') to match common web API expectations.

        Args:
            params: Original query parameters

        Returns:
            A new dictionary with normalized parameter values.
        """

        return {
            key: 'true' if value is True else 'false' if value is False else value
            for key, value in (params or {}).items()
        }

    @classmethod
    async def make_json_request[T](  # noqa: PLR0913
            cls,
            url: str,
            method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            response_type: type[T],
            headers: dict | None = None,
            cookies: dict | None = None,
            params: dict | None = None,
            data: dict | None = None,
            json: dict | None = None,
            include_cookies: bool = False
    ) -> T | tuple[T, dict]:
        """
        Send an HTTP request expecting a JSON response, decoded using `msgspec`.

        Args:
            url: Endpoint URL
            method: HTTP method
            response_type: The expected type of the decoded response
            headers: Optional request headers
            cookies: Optional cookies
            params: Query parameters
            data: Form-encoded body
            json: JSON-encoded body
            include_cookies: Whether to return response cookies along with the payload

        Returns:
            Either:
            - Parsed response of type `T`
            - Or a tuple of `(T, cookies)` if `include_cookies=True`

        Raises:
            HttpClientError: For 4xx responses
            HttpServerError: For 5xx responses
            HttpRequestTimeoutError: On repeated timeouts
        """

        async def parse_response(response: httpx.Response) -> T | tuple[T, dict]:
            decoded = msgspec.json.decode(
                response.content,
                type=response_type
            )
            return (decoded, dict(response.cookies)) if include_cookies else decoded

        return await cls._execute_request(
            url=url,
            method=method,
            headers=headers,
            cookies=cookies,
            params=params,
            data=data,
            json=json,
            response_handler=parse_response
        )

    @classmethod
    async def make_request(  # noqa: PLR0913
            cls,
            url: str,
            method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] = 'GET',
            headers: dict | None = None,
            cookies: dict | None = None,
            params: dict | None = None,
            data: dict | None = None,
            json: dict | None = None,
    ) -> httpx.Response:
        """
        Send an HTTP request and return the raw `httpx.Response`.

        Unlike `.make_json_request()`, this method does not decode or parse the response body.
        It executes the full pipeline including:
        - Boolean param normalization
        - Retry logic (3 attempts on timeouts)
        - HTTP status validation (raises `HttpClientError` or `HttpServerError`)

        This is useful when you want to access the raw response data (e.g., `.text`, `.content`, `.json()`).

        Args:
            url: Target URL
            method: HTTP verb to use (default: GET)
            headers: Optional request headers
            cookies: Optional request cookies
            params: Optional query parameters
            data: Optional form data
            json: Optional JSON body

        Returns:
            httpx.Response: Raw response object (if status is valid)
        """

        async def _return_response(response: httpx.Response) -> httpx.Response:
            return response

        return await cls._execute_request(
            url=url,
            method=method,
            headers=headers,
            cookies=cookies,
            params=params,
            data=data,
            json=json,
            response_handler=_return_response
        )

    @classmethod
    async def raw_request(
            cls,
            method: str,
            url: str,
            *,
            headers: list[tuple[bytes, bytes]] | None = None,
            content: bytes | None = None,
            params: str | None = None,
    ) -> httpx.Response:
        """
        Direct, low-level request to an HTTP endpoint without retry or validation.

        This is intended for internal usage where you need full control over request/response
        at the `httpx` layer — e.g., for health checks or binary protocols.

        Args:
            method: HTTP method (e.g., 'GET', 'POST')
            url: Fully qualified endpoint URL
            headers: Byte-string headers list (httpx-style)
            content: Raw request body
            params: Encoded query string

        Returns:
            The raw `httpx.Response` object.
        """

        if cls._client is None:
            await cls.initialize_resources()
        return await cls._client.request(
            method=method,
            url=url,
            headers=headers,
            content=content,
            params=params,
        )

    @classmethod
    async def _execute_request(  # noqa: PLR0913
            cls,
            url: str,
            method: str,
            headers: dict | None,
            cookies: dict | None,
            params: dict | None,
            data: dict | None,
            json: dict | None,
            response_handler: Callable[[httpx.Response], Any]
    ) -> Any:
        """
        Core request execution logic with retry mechanism.

        Implements:
        - 3 retries for timeout errors
        - Error classification (client/server)
        - Response validation
        """
        params = cls._normalize_params(params)

        for attempt in range(1, 4):
            try:
                response = await cls._client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    cookies=cookies,
                    params=params,
                    data=data,
                    json=json,
                )
                await cls._validate_response(response)
                return await response_handler(response)

            except TimeoutError as exc:
                logger.warning(f'Request timeout (attempt {attempt}/3)')
                if attempt == 3:  # noqa: PLR2004
                    raise HttpRequestTimeoutError(details=exc) from exc
                await asyncio.sleep(2 ** attempt)

            except httpx.HTTPStatusError as e:
                cls._map_http_error(e)
            except Exception as exc:
                raise exc

    @classmethod
    async def _validate_response(cls, response: httpx.Response) -> None:
        """Validate HTTP response status code."""
        if HTTP_400_BAD_REQUEST <= response.status_code < HTTP_500_INTERNAL_SERVER_ERROR:
            raise HttpClientError(
                message=f'Client error: {response.status_code}',
                details=response.text
            )
        elif response.status_code >= HTTP_500_INTERNAL_SERVER_ERROR:
            raise HttpServerError(
                message=f'Server error: {response.status_code}',
                details=response.text
            )

    @classmethod
    def _map_http_error(cls, error: httpx.HTTPStatusError) -> None:
        """Map httpx error to custom exception."""
        if error.response.status_code >= HTTP_500_INTERNAL_SERVER_ERROR:
            raise HttpServerError(details=str(error)) from error
        raise HttpClientError(details=str(error)) from error
