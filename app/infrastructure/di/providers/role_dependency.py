"""
Role-based access dependency.
Validates user permissions using GatewayState and allowed role list.
"""

from personal_growth_sdk.authorization.models.enums import RoleType

from app.lib.context import GatewayState
from app.lib.errors.exceptions import UserAccessDeniedException

__all__ = ['role_required']


def role_required(allowed_roles: tuple[RoleType, ...]):
    """
    Creates dependency that enforces role-based access control.

    Args:
        allowed_roles: Tuple of permitted roles

    Returns:
        Dependency that validates user roles at runtime
    """

    async def wrapper(
            gw_state: GatewayState
    ) -> None:
        user = gw_state.auth_user
        if user is None or user.role not in allowed_roles:
            raise UserAccessDeniedException

    return wrapper
