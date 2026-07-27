# Staging Readiness Report

**Date:** 2026-07-26

---

## Docker Compose

| Service | Image | Status (Code Review) |
|---|---|---|
| PostgreSQL | `postgres:16-alpine` | ✅ Health check, persistent volume, port 5432 |
| Redis | `redis:7-alpine` | ✅ Health check, persistent volume, port 6379 |
| API | Build from `Dockerfile` | ✅ Python 3.11-slim, uvicorn, port 8000 |

**Dependency ordering:** `api → postgres (healthy) → redis (healthy)` — correct.

## Dockerfile

| Check | Status |
|---|---|
| Base image | ✅ `python:3.11-slim` |
| Dependencies | ✅ `requirements.txt` copied and installed |
| Port | ✅ `EXPOSE 8000` |
| Command | ✅ `uvicorn main:app --host 0.0.0.0 --port 8000` |

## Backend Startup

| Check | Status | Evidence |
|---|---|---|
| Python imports resolve | ✅ | `from main import app` — all 50 routes register |
| JWT config | ✅ | Loads from env var, RuntimeError if missing |
| Redis graceful degradation | ✅ | Auth works without Redis |
| Database initialization | ✅ | `init_db()` creates schema on startup |

## Frontend Build

| Check | Status | Evidence |
|---|---|---|
| `npx next build` | ✅ | 22 pages + robots.txt + sitemap.xml |
| Static generation | ✅ | All pages `○` (static) except `workflows/[id]` `ƒ` (dynamic) |

## API Endpoints

| Category | Routes | Status |
|---|---|---|
| Health | `GET /health`, `GET /ready` | ✅ |
| Auth | Register, login, logout, refresh, verify, me | ✅ |
| Voice | `POST /api/voice/session` | ✅ |
| Leads | CRUD + timeline + ticket creation | ✅ |
| Payments | `POST /api/stripe/create-checkout-session` | ✅ |
| Tenants | Register, provision, status | ✅ |
| Users | CRUD, suspend, activate | ✅ |
| Workflows | CRUD, start, pause, resume, cancel | ✅ |
| Notifications | List, read, read-all | ✅ |
| Outreach | Campaigns, daily reports | ✅ |
| Usage | Record | ✅ |

## Test Results

| Suite | Count | Status |
|---|---|---|
| Unit tests | 666 | ✅ All passing |
| Integration tests | 24 | ✅ All passing |
| Voice tests | 110 | ✅ All passing |
| Coverage (backend) | 73% | Acceptable for launch |

## Environment Configuration

| Variable | Staging Value Needed |
|---|---|
| `JWT_SECRET_KEY` | **Generate new** — do not reuse dev key |
| `DATABASE_URL` | `postgresql://user:pass@staging-db:5432/swarm` |
| `REDIS_URL` | `redis://staging-redis:6379/0` |
| `FRONTEND_URL` | `https://staging.realms2riches.com` |
| `BACKEND_URL` | `https://api.staging.realms2riches.com` |
| `CORS_ORIGINS` | `https://staging.realms2riches.com,https://api.staging.realms2riches.com` |
| `STRIPE_API_KEY` | Use **test** key (`sk_test_*`) for staging |
| `ELEVENLABS_API_KEY` | Same as production (can reuse) |
| `ENV` | `staging` |
| `LOG_LEVEL` | `DEBUG` |

## Staging Deployment Command

```bash
# Ensure production URLs are set
export FRONTEND_URL=https://staging.realms2riches.com
export BACKEND_URL=https://api.staging.realms2riches.com
export CORS_ORIGINS=https://staging.realms2riches.com,https://api.staging.realms2riches.com
export ENV=staging
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Deploy
docker compose up -d

# Verify
curl -f http://localhost:8000/health
curl -f http://localhost:8000/ready
```

## Staging Readiness: **All checks pass at code level.**
Requires PostgreSQL + Redis running in staging environment.
