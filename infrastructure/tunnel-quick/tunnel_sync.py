"""
Tunnel Auto-Pilot: Quick Tunnel supervisor.

Runs ``cloudflared tunnel --url <target>`` (free Quick Tunnel — no account,
no domain), watches its log output for the freshly issued
``https://<random>.trycloudflare.com`` URL, and publishes it to Redis under
``site:public_url`` with a 24h TTL.

Because Quick Tunnel URLs change on EVERY cloudflared restart, this
supervisor:

1. publishes the URL immediately at boot (covers reboots / patch
   deployments / container restarts), and
2. restarts cloudflared every ``SYNC_INTERVAL_HOURS`` (default 24) so the
   stack follows a fresh URL daily without any manual step.

The rest of the stack reads ``site:public_url`` at request time
(``core/runtime_origin.py`` backend, ``lib/server-site.ts`` frontend), so a
rotated URL flows through automatically: CORS, SEO base URLs, share links
and Stripe redirects all follow the tunnel.

Env:
- TUNNEL_TARGET: origin the tunnel exposes (default http://frontend:3000)
- REDIS_URL: Redis to publish the URL into (default redis://redis:6379/0)
- SYNC_INTERVAL_HOURS: hours between tunnel restarts (default 24)
- TUNNEL_URL_KEY: Redis key (default site:public_url)
"""

import os
import re
import signal
import subprocess
import sys
import time
from typing import Optional

import redis

TUNNEL_TARGET = os.getenv("TUNNEL_TARGET", "http://frontend:3000")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_HOURS", "24")) * 3600
TUNNEL_URL_KEY = os.getenv("TUNNEL_URL_KEY", "site:public_url")
TUNNEL_URL_TTL_SECONDS = 24 * 3600  # 24h: the key self-expires if we die

_URL_PATTERN = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")

_shutdown = False


def _handle_signal(signum, _frame):
    global _shutdown
    _shutdown = True


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


def _publish(client: redis.Redis, url: str) -> None:
    try:
        client.set(TUNNEL_URL_KEY, url, ex=TUNNEL_URL_TTL_SECONDS)
        print(f"published {TUNNEL_URL_KEY} = {url} (TTL 24h)", flush=True)
    except redis.RedisError as exc:  # pragma: no cover - defensive
        print(f"redis publish failed: {exc}", flush=True)


def _extract_url(line: str) -> Optional[str]:
    match = _URL_PATTERN.search(line)
    return match.group(0) if match else None


def run_cycle(client: redis.Redis) -> None:
    """Run cloudflared once; publish its URL; keep it alive until rotation."""
    print(f"starting Quick Tunnel -> {TUNNEL_TARGET}", flush=True)
    proc = subprocess.Popen(
        [
            "cloudflared",
            "tunnel",
            "--no-autoupdate",
            "--url",
            TUNNEL_TARGET,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    published_url: Optional[str] = None
    started_at = time.monotonic()

    try:
        while True:
            if _shutdown:
                print("shutdown requested, stopping tunnel", flush=True)
                return

            line = proc.stdout.readline()
            if line:
                url = _extract_url(line)
                if url and url != published_url:
                    _publish(client, url)
                    published_url = url
                    print(f"tunnel URL: {url}", flush=True)

            if proc.poll() is not None:
                print(f"cloudflared exited with code {proc.returncode}", flush=True)
                return

            if time.monotonic() - started_at >= SYNC_INTERVAL_SECONDS:
                print(
                    f"rotation interval ({SYNC_INTERVAL_SECONDS}s) elapsed; "
                    "restarting tunnel for a fresh URL",
                    flush=True,
                )
                return
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> int:
    client = redis.from_url(
        REDIS_URL,
        socket_connect_timeout=2,
        socket_timeout=2,
        retry_on_timeout=True,
    )
    while not _shutdown:
        try:
            run_cycle(client)
        except Exception as exc:  # pragma: no cover - defensive loop
            print(f"cycle failed: {exc!r}; retrying in 10s", flush=True)
            time.sleep(10)
        else:
            if _shutdown:
                break
            time.sleep(2)
    print("tunnel-sync stopped", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
