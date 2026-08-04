"""Unit tests for the secret rotation framework (core.auth.secret_rotation)."""

import os
from datetime import datetime, timedelta, timezone

from core.auth.secret_rotation import (
    ROTATION_CONFIG,
    get_previous_secret,
    get_secret_age_days,
    is_rotation_due,
    list_rotation_status,
    rotate_secret,
)


def _clear(monkeypatch, *names):
    for n in names:
        monkeypatch.delenv(n, raising=False)
        monkeypatch.delenv(f"{n}_ROTATED_AT", raising=False)
        monkeypatch.delenv(f"{n}_PREVIOUS", raising=False)


def test_rotation_config_covers_jwt_and_elevenlabs():
    assert set(ROTATION_CONFIG) == {"JWT_SECRET_KEY", "ELEVENLABS_API_KEY"}
    assert ROTATION_CONFIG["JWT_SECRET_KEY"]["min_age_days"] == 90
    assert ROTATION_CONFIG["JWT_SECRET_KEY"]["previous_env_var"] == "JWT_SECRET_KEY_PREVIOUS"


def test_get_secret_age_days_none_when_unset(monkeypatch):
    _clear(monkeypatch, "JWT_SECRET_KEY_ROTATED_AT")
    assert get_secret_age_days("JWT_SECRET_KEY") is None


def test_get_secret_age_days_none_on_malformed(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY_ROTATED_AT", "not-a-timestamp")
    assert get_secret_age_days("JWT_SECRET_KEY") is None


def test_get_secret_age_days_computes_age(monkeypatch):
    rotated = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    monkeypatch.setenv("JWT_SECRET_KEY_ROTATED_AT", rotated)
    age = get_secret_age_days("JWT_SECRET_KEY")
    assert age is not None
    assert 9.5 <= age <= 10.5


def test_is_rotation_due_false_for_unknown_secret():
    assert is_rotation_due("NOT_A_SECRET") is False


def test_is_rotation_due_false_when_never_rotated(monkeypatch):
    _clear(monkeypatch, "JWT_SECRET_KEY_ROTATED_AT")
    assert is_rotation_due("JWT_SECRET_KEY") is False


def test_is_rotation_due_true_after_min_age(monkeypatch):
    rotated = (datetime.now(timezone.utc) - timedelta(days=95)).isoformat()
    monkeypatch.setenv("JWT_SECRET_KEY_ROTATED_AT", rotated)
    assert is_rotation_due("JWT_SECRET_KEY") is True


def test_is_rotation_due_false_before_min_age(monkeypatch):
    rotated = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    monkeypatch.setenv("JWT_SECRET_KEY_ROTATED_AT", rotated)
    assert is_rotation_due("JWT_SECRET_KEY") is False


def test_rotate_unknown_secret_returns_false():
    assert rotate_secret("BOGUS", "x") is False


def test_rotate_secret_without_current_value(monkeypatch):
    _clear(monkeypatch, "JWT_SECRET_KEY", "JWT_SECRET_KEY_PREVIOUS", "JWT_SECRET_KEY_ROTATED_AT")
    assert rotate_secret("JWT_SECRET_KEY", "new-secret") is True
    assert os.getenv("JWT_SECRET_KEY") == "new-secret"
    assert os.getenv("JWT_SECRET_KEY_ROTATED_AT") is not None


def test_rotate_secret_moves_current_to_previous(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "old-secret")
    _clear(monkeypatch, "JWT_SECRET_KEY_PREVIOUS")
    assert rotate_secret("JWT_SECRET_KEY", "new-secret") is True
    assert os.getenv("JWT_SECRET_KEY") == "new-secret"
    assert os.getenv("JWT_SECRET_KEY_PREVIOUS") == "old-secret"


def test_rotate_secret_stamps_rotated_at(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "current")
    _clear(monkeypatch, "JWT_SECRET_KEY_ROTATED_AT")
    rotate_secret("JWT_SECRET_KEY", "rotated")
    stamp = os.getenv("JWT_SECRET_KEY_ROTATED_AT")
    assert stamp is not None
    datetime.fromisoformat(stamp)


def test_get_previous_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY_PREVIOUS", "prev")
    assert get_previous_secret("JWT_SECRET_KEY") == "prev"


def test_get_previous_secret_unknown(monkeypatch):
    assert get_previous_secret("BOGUS") is None


def test_list_rotation_status(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-current")
    rotated = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
    monkeypatch.setenv("ELEVENLABS_API_KEY_ROTATED_AT", rotated)

    statuses = list_rotation_status()
    by_name = {s["secret"]: s for s in statuses}

    assert len(statuses) == 2
    jwt = by_name["JWT_SECRET_KEY"]
    assert jwt["configured"] is True
    assert jwt["rotation_due"] is False
    assert jwt["min_age_days"] == 90

    el = by_name["ELEVENLABS_API_KEY"]
    assert el["configured"] is True
    assert el["rotation_due"] is True
    assert el["age_days"] is not None


def test_list_rotation_status_unconfigured(monkeypatch):
    _clear(monkeypatch, "JWT_SECRET_KEY", "ELEVENLABS_API_KEY")
    statuses = list_rotation_status()
    assert all(s["configured"] is False for s in statuses)
    assert all(s["age_days"] is None for s in statuses)
