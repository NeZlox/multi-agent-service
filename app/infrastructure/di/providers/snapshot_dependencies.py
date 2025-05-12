"""
Dependency provider for SnapshotService.

Used to inject a pre-configured instance of `SnapshotService` into the DI container.
"""

from app.application.services import SnapshotService
from app.lib.http import HttpService

__all__ = ['provide_snapshot_service']


def provide_snapshot_service() -> SnapshotService:
    """
    Returns a singleton-like SnapshotService instance, bound to a shared HttpService.

    This provider is designed to be used with dependency injection.

    Returns:
        SnapshotService: Snapshot ML service proxy client
    """

    return SnapshotService(http_service=HttpService())
