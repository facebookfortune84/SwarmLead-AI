"""
Site-wide domain configuration — the single source of truth for every public
hostname in the system.

Everything that renders a URL (CORS origins, SEO base URL, share links,
Stripe redirects, tenant subdomains) derives from ONE variable:
``PUBLIC_DOMAIN``. Changing the public domain is a one-line change:

    PUBLIC_DOMAIN=new-brand.com

and nothing in the code needs to move. Optional overrides remain available
for setups that split the frontend and API across different hosts.

Rules applied:
- ``PUBLIC_DOMAIN`` may be given with or without a scheme (``example.com``
  or ``https://example.com``); bare values are assumed ``https://``.
- The API host defaults to ``api.<PUBLIC_DOMAIN>`` (subdomain siblings are
  convention across the project: ``api.*``, ``www.*``, tenant slugs).
- CORS origins are derived automatically from the public domain and its
  standard subdomains (apex, www, api) plus any explicit ``CORS_ORIGINS``
  extras. Localhost origins are always allowed for development.
- ``TECH_DOMAIN`` defaults to ``PUBLIC_DOMAIN`` when not set, so tenant
  boxes land on ``<slug>.<PUBLIC_DOMAIN>``.
- A Cloudflare tunnel hostname (``CLOUDFLARE_TUNNEL_HOSTNAME``) is included
  in CORS origins when set, so a trycloudflare quick-link works during
  domain-migration staging.

Dynamic tunnel mode
-------------------
When ``DYNAMIC_TUNNEL_MODE=1``, the site origin is resolved at REQUEST time
from the ``site:public_url`` key that the ``tunnel-quick`` service keeps in
Redis (the current Quick Tunnel URL, which rotates daily). This lets the
whole app follow a changing URL with zero rebuilds — see
``core/runtime_origin.py``. Explicit env overrides (``FRONTEND_URL``,
``PUBLIC_DOMAIN``, ...) always win over the runtime value.
"""

import os
from typing import List

from core.runtime_origin import dynamic_tunnel_mode, runtime_tunnel_url

PUBLIC_DOMAIN = (os.getenv("PUBLIC_DOMAIN") or "realms2riches.com").strip()


def _strip_scheme(value: str) -> str:
    """Remove any http(s):// prefix so we can rebuild URLs safely."""
    return value.strip().replace("https://", "").replace("http://", "").rstrip("/")


def _runtime_origin() -> str | None:
    """Full origin (with scheme) of the live tunnel URL, when dynamic mode
    is on and the tunnel service has published one."""
    if not dynamic_tunnel_mode():
        return None
    return runtime_tunnel_url()


def public_domain() -> str:
    """Bare hostname (no scheme) of the public site."""
    runtime = _runtime_origin()
    if runtime:
        return _strip_scheme(runtime)
    return _strip_scheme(PUBLIC_DOMAIN)


def api_domain() -> str:
    """Bare hostname (no scheme) of the API."""
    runtime = _runtime_origin()
    if runtime:
        return _strip_scheme(runtime)
    return _strip_scheme(os.getenv("API_DOMAIN") or f"api.{public_domain()}")


def site_url() -> str:
    """Full origin of the frontend (used for links, shares, redirects)."""
    explicit = os.getenv("FRONTEND_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    runtime = _runtime_origin()
    if runtime:
        return runtime.rstrip("/")
    return f"https://{public_domain()}"


def api_url() -> str:
    """Full origin of the backend (used for webhooks, cross-origin links)."""
    explicit = os.getenv("BACKEND_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    runtime = _runtime_origin()
    if runtime:
        return runtime.rstrip("/")
    return f"https://{api_domain()}"


def tech_domain() -> str:
    """Root domain for multi-tenant boxes (defaults to the public domain)."""
    return _strip_scheme(os.getenv("TECH_DOMAIN") or public_domain())


def cors_origins() -> List[str]:
    """Allowed browser origins, derived from PUBLIC_DOMAIN + overrides."""
    root = public_domain()
    derived = {
        f"https://{root}",
        f"https://www.{root}",
        f"https://api.{root}",
        f"https://corp.{root}",
        f"https://{api_domain()}",
    }

    extra = os.getenv("CORS_ORIGINS", "")
    for origin in extra.split(","):
        origin = origin.strip()
        if origin:
            derived.add(origin)

    tunnel = os.getenv("CLOUDFLARE_TUNNEL_HOSTNAME", "").strip()
    if tunnel:
        derived.add(f"https://{_strip_scheme(tunnel)}")

    runtime = runtime_tunnel_url()
    if runtime:
        derived.add(runtime.rstrip("/"))

    dev = {"http://localhost:3000", "http://127.0.0.1:3000"}
    return sorted(dev | derived)


def frontend_cookie_domain() -> str | None:
    """Cookie domain for the frontend host, or None for host-only cookies."""
    domain = os.getenv("COOKIE_DOMAIN", "").strip()
    if not domain:
        return None
    return _strip_scheme(domain).lstrip(".")