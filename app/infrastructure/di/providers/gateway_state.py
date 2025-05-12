"""
Dependency provider for GatewayState.
Extracts authenticated user context from the incoming request.
"""

from litestar import Request

from app.lib.context import GatewayState, gather_state


def gateway_state_provider(request: Request) -> GatewayState:
    """
    Retrieves gateway state based on the incoming request.

    Args:
        request: Incoming HTTP request

    Returns:
        GatewayState: Parsed authentication and user context
    """

    return gather_state(request)
