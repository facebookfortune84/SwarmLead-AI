"""
Runtime origin registry — the dynamic-URL half of the tunnel auto-pilot.

The Quick Tunnel (cloudflared, no fixed domain) produces a NEW public URL
every time it restarts. Instead of baking a domain into the app at build
time, the `tunnel-quick` service publishes the current URL into Redis under
``site:public_url`` (24h TTL). This module reads that key at REQUEST time
so CORS, SEO base URLs, share links and Stripe redirects always point at
the URL the tunnel is serving right now.

Resolution order (highest wins):
1. Explicit env override (``FRONTEND_URL`` / ``BACKEND_URL`` /
   ``API_DOMAIN`` / ``PUBLIC_DOMAIN``).
2. Runtime tunnel URL from Redis, when ``DYNAMIC_TUNNEL_MODE=1``.
3. Static default (``PUBLIC_DOMAIN`` env, else realms2riches.com).

Redis is a soft dependency: if it is unreachable the runtime URL is simply
``None`` and the env/static path behaves exactly like before.
"""

import os
import threading
import time
from typing import Optional

_REDIS_URL = os.getenv("REDIS_URL") or "redis://localhost:6379/0"
_TUNNEL_URL_KEY = "site:public_url"

_runtime_cache: dict = {"ts": 0.0, "value": None}
_cache_lock = threading.Lock()
_CACHE_TTL_SECONDS = 10.0
_REDIS_TIMEOUT_SECONDS = 0.5


def dynamic_tunnel_mode() -> bool:
    """True when the app should follow the tunnel's rotating URL."""
    return os.getenv("DYNAMIC_TUNNEL_MODE", "").strip().lower() in {"1", "true", "yes", "on"}


def _read_redis_key() -> Optional[str]:
    """Read the current tunnel URL from Redis, never raising."""
    try:
        import redis

        client = redis.from_url(
            _REDIS_URL,
            socket_connect_timeout=_REDIS_TIMEOUT_SECONDS,
            socket_timeout=_REDIS_TIMEOUT_SECONDS,
        )
        raw = client.get(_TUNNEL_URL_KEY)
        if raw is None:
            return None
        value = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
        return value.strip() or None
    except Exception:
        return None


def runtime_tunnel_url() -> Optional[str]:
    """Current tunnel origin (e.g. https://abc.trycloudflare.com) or None.

    Cached for a few seconds so request-time reads stay cheap; Redis
    outages degrade to ``None`` without raising.
    """
    with _cache_lock:
        now = time.monotonic()
        if now - _runtime_cache["ts"] > _CACHE_TTL_SECONDS:
            _runtime_cache["ts"] = now
            _runtime_cache["value"] = _read_redis_key()
        return _runtime_cache["value"]


def _clear_runtime_cache():
    """Test hook: force the next call to re-read Redis."""
    with _cache_lock:
        _runtime_cache["ts"] = 0.0
        _runtime_cache["value"] = None
