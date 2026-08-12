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

# Stable "door" page: a static host (e.g. GitHub Pages) whose URL never
# changes, forwarding visitors to the CURRENT tunnel URL. When the tunnel
# rotates, we regenerate the page and push it, so the door always points at
# the live app. DOOR_REPO is the SSH clone URL of the door repo,
# DOOR_SSH_ARGS the ssh invocations (identity file, no host checking).
DOOR_REPO = os.getenv("DOOR_REPO", "").strip()
DOOR_SSH_ARGS = os.getenv(
    "DOOR_SSH_ARGS",
    "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
)
_SSH_IDENTITY = os.getenv("DOOR_SSH_KEY", "/door_key")


def _prepare_ssh_key() -> None:
    """Windows mounts the key with world-readable perms + CRLF; OpenSSH
    refuses both. Copy to a private path with LF endings and 0600."""
    global _SSH_IDENTITY  # noqa: PLW0603
    source = os.environ.get("DOOR_SSH_KEY", "/door_key")
    if not os.path.exists(source):
        return
    content = open(source, "rb").read().replace(b"\r\n", b"\n")
    import stat

    private = "/door_key.private"
    with open(private, "wb") as fh:
        fh.write(content)
    os.chmod(private, stat.S_IRUSR | stat.S_IWUSR)
    _SSH_IDENTITY = private


DOOR_TITLE = "SwarmLead — Redirecting\u2026"

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


def _write_door_page(workdir: str, url: str) -> None:
    """Rewrite the door repo's index.html to redirect to the live URL."""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{DOOR_TITLE}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0; url={url}">
<style>
  body {{ margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
         background: #0a0a1a; color: #c7c7d8; font-family: system-ui, sans-serif; }}
  .box {{ text-align: center; padding: 2rem; }}
  a {{ color: #818cf8; }}
</style>
</head>
<body>
<div class="box">
  <p>Redirecting to the live app\u2026</p>
  <p><a href="{url}">Click here if you are not redirected automatically</a></p>
</div>
<script>window.location.replace({url!r});</script>
</body>
</html>
"""
    path = os.path.join(workdir, "index.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)


def _git(args, workdir, **kw):
    env = dict(os.environ, GIT_SSH_COMMAND=f"ssh {DOOR_SSH_ARGS} -i {_SSH_IDENTITY}")
    return subprocess.run(
        ["git", *args], cwd=workdir, env=env, capture_output=True, text=True, **kw
    )


def _sync_door(url: str) -> None:
    """If a door repo is configured, point its index.html at the live URL and push."""
    if not DOOR_REPO:
        return
    print(f"syncing door -> {url}", flush=True)
    workdir = "/door"
    import shutil

    shutil.rmtree(workdir, ignore_errors=True)  # always start clean
    cloned = False
    for attempt in range(3):  # retry clone against flaky network
        result = _git(["clone", "--depth", "1", DOOR_REPO, workdir], "/")
        if result.returncode == 0:
            cloned = True
            break
        err = (result.stderr or result.stdout).strip()
        print(f"door clone attempt {attempt + 1} failed:\n{err}", flush=True)
        shutil.rmtree(workdir, ignore_errors=True)
        time.sleep(5)
    if not cloned:
        print("door clone failed after retries; will retry next rotation", flush=True)
        return

    _write_door_page(workdir, url)
    _git(
        ["config", "user.name", "SwarmLead Door"],
        workdir,
    )
    _git(
        ["config", "user.email", "door@swarmlead.local"],
        workdir,
    )
    _git(["add", "index.html"], workdir)
    commit = _git(
        [
            "commit",
            "-m",
            f"Redirect door to live tunnel URL: {url}",
        ],
        workdir,
    )
    if commit.returncode != 0 and "nothing to commit" not in commit.stdout:
        print(f"door commit failed: {commit.stderr.strip()}", flush=True)
    _git(["push", "origin", "HEAD"], workdir)
    print("door pushed; GitHub Pages rebuilds shortly (1-2 min)", flush=True)


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
                    _sync_door(url)

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
    _prepare_ssh_key()
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
