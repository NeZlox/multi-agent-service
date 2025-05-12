"""
Role-based access control groups.
Defines permission sets for different user roles.
"""

from typing import ClassVar

from personal_growth_sdk.authorization.models.enums import RoleType

__all__ = ['RoleGroup']

from app.config.base_settings import get_settings

settings = get_settings()


class RoleGroup:
    """
    Organizes roles into permission groups with environment awareness.
    """

    _is_prod_mode = settings.app.MODE == 'PROD'

    _extra: ClassVar[tuple[RoleType, ...]] = () if _is_prod_mode else (RoleType.DEVELOPER,)

    # Access groups
    ADMIN: ClassVar[tuple[RoleType, ...]] = tuple({RoleType.ADMIN, *_extra})
    STAFF: ClassVar[tuple[RoleType, ...]] = tuple({*ADMIN, RoleType.MANAGER, *_extra})
    COMMON: ClassVar[tuple[RoleType, ...]] = tuple({*ADMIN, *STAFF, RoleType.USER, *_extra})

    # Development-only roles
    PRIVATE: ClassVar[tuple[RoleType, ...]] = _extra if not _is_prod_mode else ()
