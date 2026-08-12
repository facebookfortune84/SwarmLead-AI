# Tunnel Auto-Pilot: Quick Tunnel supervisor.
#
# Runs cloudflared's free Quick Tunnel (no account, no domain), extracts the
# freshly-issued trycloudflare.com URL, and publishes it to Redis under
# `site:public_url` (24h TTL) so the rest of the stack can follow the URL
# at request time. Re-acquires a fresh URL on every boot AND on a daily
# rotation interval (SYNC_INTERVAL_HOURS), because Quick Tunnel URLs change
# every time cloudflared restarts.
#
# Base: python:alpine (the stock cloudflared image is distroless — no shell,
# no package manager — so we download the cloudflared binary instead).
FROM python:3.12-alpine

ARG TARGETARCH

RUN apk add --no-cache curl \
    && curl -fsSL -o /usr/local/bin/cloudflared \
        "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${TARGETARCH}" \
    && chmod +x /usr/local/bin/cloudflared \
    && pip install --no-cache-dir redis

COPY tunnel_sync.py /tunnel_sync.py

ENTRYPOINT ["python3", "/tunnel_sync.py"]
