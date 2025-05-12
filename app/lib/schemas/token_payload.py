"""
JWT Token payload schema definition.
Defines the structure and validation rules for JWT token contents.
"""
import contextlib
import datetime

import msgspec


class TokenPayloadSchema(msgspec.Struct, forbid_unknown_fields=True):
    """
    JWT token payload schema with validation rules.

    Attributes:
        sub: User ID (required)
        exp: Expiration (datetime)
        role: Optional role string

    Config:
        forbid_unknown_fields: Rejects payloads with extra fields
    """

    sub: str
    exp: datetime.datetime | int
    role: str | None

    def __post_init__(self):
        """
        Post-initialization processing.
        Automatically converts integer timestamps to UTC datetime objects if needed.
        """

        with contextlib.suppress(TypeError, ValueError):
            self.exp = datetime.datetime.fromtimestamp(int(self.exp), datetime.UTC)
