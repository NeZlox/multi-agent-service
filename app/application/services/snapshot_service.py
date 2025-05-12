"""
Snapshot service — sends user prompts to an external ML/analytics service
to extract user characteristics (e.g., emotions, intent, etc.).

This service is designed to be **non-blocking** — failures are logged and ignored
to ensure the chat experience remains uninterrupted.
"""

from __future__ import annotations

from app.config.base_settings import get_settings
from app.lib.http.http_service import HttpService
from app.lib.logger import logger
from app.lib.singleton import SingletonMeta

settings = get_settings()

__all__ = ['SnapshotService']


class SnapshotService(metaclass=SingletonMeta):
    """
    Proxy client for communicating with the external Snapshot ML analytics service.

    Responsibilities:
    - Sending user messages for emotion/intent analysis
    - Performing availability checks (ping)

    Failures are non-critical and are logged without affecting flow.
    """

    def __init__(self, http_service: HttpService):
        self.http_service = http_service

    async def ping(self) -> None:
        """
        Perform a simple health check to the Snapshot service.

        Raises:
            HttpClientError / HttpServerError: On request failure
        """

        url = f'{settings.app.SNAPSHOT_SERVICE_URL}/api/health/ping'
        await self.http_service.make_request(url=url, method='GET')

    async def capture(self, user_id: int, message: str) -> None:
        """
        Submit a user message for analysis (emotion, intent, etc.).

        If the snapshot service is unreachable or fails, the exception is caught
        and logged — the main application flow is not interrupted.

        Args:
            user_id: ID of the user who sent the message
            message: The actual message content to analyze
        """

        return
        params = {'user_id': user_id, 'message': message}
        try:
            await self.http_service.make_json_request(
                url=f'{settings.app.SNAPSHOT_SERVICE_URL}/v1/snapshot',
                method='POST',
                response_type=dict,
            )
        except Exception as exc:
            logger.warning('Snapshot service failed: %s', exc)
