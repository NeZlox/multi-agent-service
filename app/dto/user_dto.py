"""
DTO configuration for exposing user data via public API.

This module defines a `UserResponseDTO` based on `UserResponse` schema,
used to serialize and expose only selected public fields in API responses.
"""

from litestar.dto import DTOConfig, MsgspecDTO
from personal_growth_sdk.authorization.schemas import UserResponse

__all__ = ['UserResponseDTO']


class UserResponseDTO(MsgspecDTO[UserResponse]):
    """
    Public representation of UserResponse (no service fields).
    """

    config = DTOConfig(
        exclude={'active_sessions', 'created_at', 'updated_at'},
        experimental_codegen_backend=True,
        forbid_unknown_fields=True
    )
