"""
Integration Test — Authentication Flow

Verifies JWT token creation, validation, and revocation
using the production auth pipeline.
"""

import time
import os

import pytest

from interfaces.api.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    decode_token,
    verify_token,
    revoke_token,
    is_token_revoked,
)


def test_create_and_decode_access_token():
    token = create_access_token(
        data={"sub": "test_user", "role": "admin"},
    )
    assert token is not None
    assert isinstance(token, str)

    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "test_user"
    assert payload["role"] == "admin"


def test_create_and_decode_refresh_token():
    token = create_refresh_token(
        data={"sub": "test_user"},
    )
    assert token is not None

    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "test_user"
    assert payload["type"] == "refresh"


def test_refresh_access_token():
    refresh = create_refresh_token(data={"sub": "refresh_user"})

    new_access = refresh_access_token(refresh)
    assert new_access is not None

    payload = decode_token(new_access)
    assert payload is not None
    assert payload["sub"] == "refresh_user"


def test_verify_valid_token():
    token = create_access_token(data={"sub": "verify_test"})
    assert verify_token(token) is True


def test_verify_invalid_token():
    assert verify_token("invalid.token.here") is False
    assert verify_token("") is False


def test_expired_token_rejected():
    import jwt as pyjwt
    payload = {
        "sub": "expired_user",
        "exp": int(time.time()) - 3600,
    }
    token = pyjwt.encode(
        payload,
        os.getenv("JWT_SECRET_KEY", "test_secret"),
        algorithm="HS256",
    )

    payload = decode_token(token)
    assert payload is None

    assert verify_token(token) is False


def test_decode_nonexistent_token():
    result = decode_token("not.a.real.token")
    assert result is None


def test_token_revocation_fails_gracefully_without_redis():
    token = create_access_token(data={"sub": "revoke_test"})

    assert is_token_revoked(token) is False

    result = revoke_token(token)
    assert result is False  # Redis unavailable, graceful degradation
