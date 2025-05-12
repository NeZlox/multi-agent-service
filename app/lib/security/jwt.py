"""
Utility for validating JWT access tokens using a public RSA key (RS256).

Handles signature verification, expiration checks, and structured error handling.
"""
from jose import ExpiredSignatureError, JWTError, jwt

from app.config.base_settings import get_settings
from app.lib.errors.exceptions import (
    JWTCannotDecodeException,
    JWTExpiredException,
    JWTInvalidException,
)

settings = get_settings()


class PublicJWTManager:
    """
    Utility for decoding and validating JWT access tokens using a public RSA key (RS256).
    """

    @staticmethod
    def decode_access_token(token: str) -> dict:
        """
        Decodes and validates the signature of a JWT access token.
        """
        try:
            decoded_token = jwt.decode(
                token,
                settings.app.JWT_PUBLIC_KEY,
                algorithms=[settings.app.JWT_ALGORITHM],
            )
            return decoded_token
        except ExpiredSignatureError as exc:
            raise JWTExpiredException from exc
        except JWTError as exc:
            raise JWTInvalidException from exc
        except Exception as exc:
            raise JWTCannotDecodeException from exc
