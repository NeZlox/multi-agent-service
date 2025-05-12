"""
Client context information schema.
Captures and transports client metadata throughout the application.
"""

import msgspec


class ClientInfoSchema(msgspec.Struct, forbid_unknown_fields=True):
    """
    Client information and authentication tokens schema.
    Used to store and transport client context throughout the application.

    Attributes:
        ip: Client IP address (IPv4 or IPv6)
        user_agent: Raw User-Agent header string
        fingerprint: Browser/device fingerprint hash
        access_token: JWT access token string
        refresh_token: JWT refresh token string

    Config:
        forbid_unknown_fields: Rejects payloads with extra fields
    """

    ip: str | None = None
    user_agent: str | None = None
    fingerprint: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
