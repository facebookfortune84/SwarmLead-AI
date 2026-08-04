import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"


def load_env(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not value.startswith('"'):
            value = value.split("#", 1)[0].strip()
        else:
            value = value.strip('"')
        os.environ.setdefault(key, value)


def main() -> int:
    load_env(ENV_PATH)
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-for-local-runs-only")
    # Integration tests run on the host against the Docker-published services,
    # so rewrite docker-network hostnames to localhost when present in .env.
    _remap("DATABASE_URL", "postgres", "localhost")
    _remap("SWARM_DB_URL", "postgres", "localhost")
    _remap("REDIS_URL", "redis", "localhost")
    return subprocess.call([sys.executable, "-m", "pytest", *sys.argv[1:]], cwd=ROOT)


def _remap(key: str, hostname: str, replacement: str) -> None:
    value = os.environ.get(key, "")
    if not value:
        return
    os.environ[key] = value.replace(f"@{hostname}:", f"@{replacement}:")
    os.environ[key] = os.environ[key].replace(f"://{hostname}:", f"://{replacement}:")
    # Docker-compose credentials (published on localhost) may differ from .env.
    if key in ("DATABASE_URL", "SWARM_DB_URL") and hostname == "postgres":
        os.environ[key] = os.environ[key].replace(":strongpassword@", ":SwarmLead2026!@")


if __name__ == "__main__":
    raise SystemExit(main())
