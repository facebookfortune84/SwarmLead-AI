# Deployment Readiness Report

**Date:** 2026-07-26
**Author:** Genesis Chief Engineer

---

## Deployment Target

| Item | Value |
|---|---|
| **Source branch** | `release/v1.0.0-rc.1` |
| **Commit** | `6db9cb4` |
| **Docker Compose** | `docker compose up -d` |
| **PostgreSQL** | `postgres:16-alpine` (via compose) |
| **Redis** | `redis:7-alpine` (via compose) |
| **API** | Python 3.11-slim, uvicorn, port 8000 |
| **Frontend** | Next.js 16.2.10, Node 24.14.1 |

## Infrastructure Requirements

| Dependency | Status | Action |
|---|---|---|
| Docker daemon | ⚠️ Offline | Start Docker Desktop before deployment |
| PostgreSQL 16 | ⬜ Not provisioned | `docker compose up -d postgres` |
| Redis 7 | ⬜ Not provisioned | `docker compose up -d redis` |
| Stripe API key | ⚠️ Live key in `.env` | Use `sk_test_*` for staging |
| ElevenLabs API key | ✅ Present in `.env` | Production key ready |
| Production domains | ⬜ Not configured | Set `FRONTEND_URL`, `BACKEND_URL` for target environment |

## Deployment Steps

### 1. Environment Variables

```bash
# Generate unique secrets
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Set environment-appropriate URLs
FRONTEND_URL=https://staging.realms2riches.com
BACKEND_URL=https://api.staging.realms2riches.com
CORS_ORIGINS=https://staging.realms2riches.com,https://api.staging.realms2riches.com

# Use test keys for staging
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test...
ELEVENLABS_API_KEY=<existing key>

# Database
SWARM_DB_URL=postgresql://swarm:password@postgres:5432/swarm
```

### 2. Start Infrastructure

```bash
cd /path/to/SwarmLead-AI
docker compose up -d postgres redis
# Wait for health checks to pass
```

### 3. Deploy API

```bash
docker compose up -d api
# Verify with:
curl -f http://localhost:8000/health
curl -f http://localhost:8000/ready
```

### 4. Deploy Frontend

```bash
docker compose up -d frontend
# Or if deploying separately:
cd frontend && npm run build && npm start
```

### 5. Register Stripe Webhook

In Stripe Dashboard → Developers → Webhooks → Add endpoint:
- **URL:** `https://api.staging.realms2riches.com/api/stripe/webhook`
- **Events:**
  - `invoice.payment_succeeded`
  - `invoice.payment_failed`
  - `customer.subscription.deleted`
- **Webhook secret:** Set as `STRIPE_WEBHOOK_SECRET` env var

## Post-Deployment Verification

| Check | Command |
|---|---|
| API health | `curl -f http://localhost:8000/health` |
| API ready | `curl -f http://localhost:8000/ready` |
| OpenAPI docs | `curl -f http://localhost:8000/openapi.json` |
| Webhook reachable | `curl -f -X POST http://localhost:8000/api/stripe/webhook` |
| Frontend | Visit `http://localhost:3000` in browser |
| Voice session | `curl -X POST http://localhost:8000/api/voice/session` |

## Rollback Plan

```bash
# Stop all services
docker compose down

# Roll back to previous image tag
git checkout <previous-tag>
docker compose up -d --build
```

## Security Notes

1. **Live Stripe key in `.env`** — The `.env` file contains `sk_live_*`. For staging, use `sk_test_*`. For production, the live key is correct.
2. **JWT_SECRET_KEY must be unique per environment** — Do not reuse the dev key in production.
3. **SMTP_HOST vs SMTP_SERVER** — `.env` uses `SMTP_SERVER` but code reads `SMTP_HOST`. Fix `.env` to use `SMTP_HOST` for email to work.
4. **No TLS termination** — Docker Compose does not include a reverse proxy. For production, add nginx/Caddy/Traefik in front of the API.

## Deployment Readiness: **READY with caveats**

Infrastructure must be provisioned first (PostgreSQL, Redis, Docker daemon). The codebase is production-ready pending environment configuration.
