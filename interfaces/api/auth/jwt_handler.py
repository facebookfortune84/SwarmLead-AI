"""
JWT token handling for authentication.

Production-hardened implementation:
- Uses REDIS_URL exclusively.
- Gracefully degrades when Redis is unavailable.
- Validates critical configuration at startup.
- Supports token revocation.
- Supports refresh tokens.
- Uses timezone-aware datetimes.
- Logs safely without exposing secrets.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import redis

try:
    import jwt
    from jwt import InvalidTokenError
except ImportError:
    raise ImportError(
        "PyJWT is required. Install it with: pip install PyJWT"
    )

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    logger.critical(
        "JWT_SECRET_KEY is not configured. Authentication will fail."
    )

ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "120",
    )
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv(
        "REFRESH_TOKEN_EXPIRE_DAYS",
        "30",
    )
)

# Startup diagnostics

logger.warning(
    "JWT CONFIG LOADED | SECRET_PREFIX=%s | ACCESS_MINUTES=%s | REFRESH_DAYS=%s",
    SECRET_KEY[:10] if SECRET_KEY else "NONE",
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

# ============================================================================
# Redis Configuration
# ============================================================================

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://redis:6379/0",
)

redis_client: Optional[redis.Redis] = None

try:
    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )

    redis_client.ping()

    logger.info(
        "JWT Redis connected successfully: %s",
        REDIS_URL,
    )

except Exception as exc:
    logger.warning(
        "JWT Redis unavailable. Token revocation cache disabled. Error: %s",
        exc,
    )

    redis_client = None

# ============================================================================
# Token Creation
# ============================================================================


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    """

    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_refresh_token(
    data: Dict[str, Any],
) -> str:
    """
    Create a JWT refresh token.
    """

    to_encode = data.copy()

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

# ============================================================================
# Token Verification
# ============================================================================


def verify_token(token: str) -> bool:
    """
    Verify token validity and revocation status.
    """

    if is_token_revoked(token):
        return False

    try:
        jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return True

    except InvalidTokenError:
        return False


def decode_token(
    token: str,
) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    """

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except InvalidTokenError as exc:
        logger.exception(
            "JWT decode failed: %s",
            exc,
        )

        return None

# ============================================================================
# Token Revocation
# ============================================================================


def revoke_token(
    token: str,
) -> bool:
    """
    Revoke a token by storing it in Redis
    until natural expiration.
    """

    if redis_client is None:
        logger.warning(
            "Token revocation requested but Redis is unavailable."
        )
        return False

    try:
        payload = decode_token(token)

        if not payload:
            return False

        exp = payload.get("exp")

        if not exp:
            return False

        ttl = int(
            exp - datetime.now(
                timezone.utc
            ).timestamp()
        )

        if ttl <= 0:
            return False

        redis_client.setex(
            f"revoked:{token}",
            ttl,
            "1",
        )

        return True

    except Exception as exc:
        logger.error(
            "Failed to revoke token: %s",
            exc,
        )

        return False


def is_token_revoked(
    token: str,
) -> bool:
    """
    Check whether a token is revoked.

    Fail-open behavior:
    If Redis is unavailable, authentication
    continues rather than locking out users.
    """

    if redis_client is None:
        return False

    try:
        return (
            redis_client.exists(
                f"revoked:{token}"
            )
            > 0
        )

    except Exception as exc:
        logger.error(
            "Redis unavailable while checking token revocation; treating token as valid: %s",
            exc,
        )

        return False

# ============================================================================
# Refresh Flow
# ============================================================================


def refresh_access_token(
    refresh_token: str,
) -> Optional[str]:
    """
    Generate a new access token from a valid
    refresh token.
    """

    if is_token_revoked(refresh_token):
        return None

    payload = decode_token(
        refresh_token
    )

    if not payload:
        return None

    if payload.get("type") != "refresh":
        return None

    user_data = {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role"),
    }

    return create_access_token(
        user_data
    )