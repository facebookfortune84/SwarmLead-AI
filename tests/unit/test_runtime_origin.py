"""Unit tests for the runtime origin registry and dynamic site resolution.

Covers core/runtime_origin.py and the dynamic-tunnel-mode branches of
core/site.py (CORS / site_url / api_url following the rotating Quick
Tunnel URL published in Redis).
"""

import pytest


@pytest.fixture(autouse=True)
def _clear_runtime_cache():
    from core import runtime_origin

    runtime_origin._clear_runtime_cache()
    yield
    runtime_origin._clear_runtime_cache()


class _FakeRedis:
    """Minimal redis-like stub for get()."""

    def __init__(self, value):
        self._value = value

    def get(self, _key):
        return self._value


class _BoomRedis:
    """Redis client that raises on connect (simulates outage)."""

    def get(self, _key):
        raise ConnectionError("redis down")


def test_runtime_tunnel_url_returns_none_without_dynamic_mode(monkeypatch):
    monkeypatch.delenv("DYNAMIC_TUNNEL_MODE", raising=False)
    from core.site import site_url

    assert site_url().startswith("https://realms2riches.com")


def test_runtime_tunnel_url_reads_redis(monkeypatch):
    from core import runtime_origin

    monkeypatch.setattr(
        runtime_origin,
        "_read_redis_key",
        lambda: "https://abc-123.trycloudflare.com",
    )
    assert runtime_origin.runtime_tunnel_url() == "https://abc-123.trycloudflare.com"


def test_runtime_tunnel_url_degrades_on_redis_outage(monkeypatch):
    from core import runtime_origin

    monkeypatch.setattr(runtime_origin, "_read_redis_key", lambda: None)
    assert runtime_origin.runtime_tunnel_url() is None


def test_runtime_tunnel_url_caches(monkeypatch):
    from core import runtime_origin

    calls = {"n": 0}

    def flaky_read():
        calls["n"] += 1
        return "https://cached.trycloudflare.com"

    monkeypatch.setattr(runtime_origin, "_read_redis_key", flaky_read)

    assert runtime_origin.runtime_tunnel_url() == "https://cached.trycloudflare.com"
    assert runtime_origin.runtime_tunnel_url() == "https://cached.trycloudflare.com"
    assert calls["n"] == 1  # second call served from the TTL cache


def test_read_redis_key_handles_outage():
    from core import runtime_origin

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(runtime_origin, "_REDIS_URL", "redis://127.0.0.1:1/0")

    try:
        assert runtime_origin._read_redis_key() is None
    finally:
        monkeypatch.undo()


def test_dynamic_mode_site_url_follows_tunnel(monkeypatch):
    from core import runtime_origin
    from core import site as site_module

    monkeypatch.delenv("FRONTEND_URL", raising=False)
    monkeypatch.delenv("BACKEND_URL", raising=False)
    monkeypatch.setenv("DYNAMIC_TUNNEL_MODE", "1")
    monkeypatch.setattr(
        runtime_origin,
        "_read_redis_key",
        lambda: "https://daily-rotating.trycloudflare.com",
    )

    assert site_module.site_url() == "https://daily-rotating.trycloudflare.com"
    assert site_module.api_url() == "https://daily-rotating.trycloudflare.com"
    assert site_module.public_domain() == "daily-rotating.trycloudflare.com"


def test_explicit_env_override_wins_over_tunnel(monkeypatch):
    from core import runtime_origin
    from core import site as site_module

    monkeypatch.setenv("DYNAMIC_TUNNEL_MODE", "1")
    monkeypatch.setenv("FRONTEND_URL", "https://brand.example")
    monkeypatch.setattr(
        runtime_origin,
        "_read_redis_key",
        lambda: "https://daily-rotating.trycloudflare.com",
    )

    assert site_module.site_url() == "https://brand.example"


def test_cors_origins_include_runtime_tunnel_url(monkeypatch):
    from core import runtime_origin
    from core.site import cors_origins

    monkeypatch.setattr(
        runtime_origin,
        "_read_redis_key",
        lambda: "https://daily-rotating.trycloudflare.com",
    )

    origins = cors_origins()
    assert "https://daily-rotating.trycloudflare.com" in origins


def test_cors_origins_without_tunnel_has_derived_set():
    from core.site import cors_origins

    origins = cors_origins()
    assert "https://realms2riches.com" in origins
    assert "http://localhost:3000" in origins
