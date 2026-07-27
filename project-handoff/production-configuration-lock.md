# Production Configuration Lock

**Date:** 2026-07-26
**Status:** FROZEN — No further configuration changes without Release Engineering review.

---

## SECTION 1 — Approved Environment Variables

### Mandatory (app crashes if missing)

| Variable | Production Value | Source |
|---|---|---|
| `JWT_SECRET_KEY` | 256-bit hex string (set via vault) | `jwt_handler.py:37` — RuntimeError if missing |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/swarm` | `session.py:25` |
| `FRONTEND_URL` | `https://realms2riches.com` | `payments.py:63` |
| `BACKEND_URL` | `https://api.realms2riches.com` | client config |

### Required (graceful degradation if absent)

| Variable | Production Value | Source | Degradation |
|---|---|---|---|
| `REDIS_URL` | `redis://redis:6379/0` (Docker) or managed Redis URL | `jwt_handler.py:76` | Auth works; token revocation disabled |
| `STRIPE_API_KEY` | `sk_live_*` (live) | `payment_service.py:17` | Checkout returns 500 |
| `STRIPE_WEBHOOK_SECRET` | `whsec_*` | `payment_service.py:156` | Async payment events not processed |
| `ELEVENLABS_API_KEY` | `sk_fb1f...` | `elevenlabs_client.py:52` | Voice falls back to text |
| `ELEVENLABS_DEFAULT_VOICE_ID` | `21m00Tcm4TlvDq8ikWAM` (Rachel) | `elevenlabs_client.py:57` | Uses default |
| `SMTP_HOST` | `smtp.gmail.com` (NOT `SMTP_SERVER`) | `notification_tasks.py:68` | Email silently skipped |
| `SMTP_PORT` | `587` | `notification_tasks.py:69` | |
| `SMTP_USER` | Gmail address | `notification_tasks.py:70` | |
| `SMTP_PASS` | Gmail app password | `notification_tasks.py:71` | |
| `SMTP_FROM` | sender address | `notification_tasks.py:72` | Falls back to SMTP_USER |
| `CONTACT_EMAIL` | `robertdemottojr83@gmail.com` | config | |

### Recommended

| Variable | Production Value | Source |
|---|---|---|
| `CORS_ORIGINS` | `https://realms2riches.com,https://api.realms2riches.com` | `main.py:41` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | `jwt_handler.py:50` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | `jwt_handler.py:57` |
| `JWT_ALGORITHM` | `HS256` | `jwt_handler.py:44` |
| `ENV` | `production` | `config_loader.py:16` |
| `LOG_LEVEL` | `INFO` | |
| `OLLAMA_API_BASE` | `http://localhost:11434` or managed LLM endpoint | `health_dashboard.py:315` |
| `TECH_DOMAIN` | `realms2riches.tech` | `tenant_service.py:61` |
| `STRIPE_HOSTING_PRICE_ID` | Stripe Price ID (created in dashboard) | `payment_service.py:30` |

### Optional (infrastructure-specific)

| Variable | Notes |
|---|---|
| `CELERY_BROKER_URL` | Falls back to REDIS_URL |
| `CELERY_RESULT_BACKEND` | Falls back to REDIS_URL |
| `S3_ENDPOINT_URL` | For S3-compatible file storage |
| `S3_ACCESS_KEY` | |
| `S3_SECRET_KEY` | |
| `S3_BUCKET_NAME` | |
| `STORAGE_MODE` | `local` or `s3` |
| `LOCAL_STORAGE_DIR` | |
| `TENANT_BOX_IMAGE` | Docker image for tenant boxes |
| `TENANT_BOX_NETWORK` | Docker network for tenant boxes |

## SECTION 2 — Approved Domains

| Domain | Purpose |
|---|---|
| `realms2riches.com` | Primary production website — FRONTEND_URL |
| `api.realms2riches.com` | Backend API — BACKEND_URL |
| `realms2riches.tech` | Deployment host — TECH_DOMAIN |
| `corp.realms2riches.com` | Corporate domain |

## SECTION 3 — Approved Infrastructure

| Component | Configuration | Source |
|---|---|---|
| **PostgreSQL** | 16-alpine, database `swarm`, user `swarm` | `docker-compose.yml:3-24` |
| **Redis** | 7-alpine, port 6379 | `docker-compose.yml:26-42` |
| **API Server** | Python 3.11-slim, uvicorn, port 8000 | `Dockerfile` |
| **Frontend** | Next.js 16, static export, 22 pages | `frontend/` |
| **CI** | GitHub Actions, Ubuntu latest, pytest + coverage | `.github/workflows/tests.yml` |

## SECTION 4 — Approved Stripe Configuration

| Setting | Value |
|---|---|
| **Mode** | Live (key prefix: `sk_live_*`) |
| **Payment flow** | Checkout Session (redirect) |
| **Billing mode** | Subscription (monthly) |
| **Success URL** | `{FRONTEND_URL}/success?session_id={CHECKOUT_SESSION_ID}` |
| **Cancel URL** | `{FRONTEND_URL}/cancel` |
| **Webhook endpoint** | Not registered in API routes (async events not handled) |
| **Webhook events needed** | `invoice.payment_succeeded`, `invoice.payment_failed`, `customer.subscription.deleted` |
| **Customer portal** | Not configured |
| **Price ID** | `price_hosting_monthly` (default, override via `STRIPE_HOSTING_PRICE_ID`) |
| **Products needed** | 1x hosting subscription (monthly, amount TBD by Stripe dashboard) |

## SECTION 5 — Approved ElevenLabs Configuration

| Setting | Value |
|---|---|
| **API Key** | Set via `ELEVENLABS_API_KEY` env var |
| **Default Voice** | `21m00Tcm4TlvDq8ikWAM` (Rachel) |
| **Default Model** | `eleven_multilingual_v2` |
| **STT Model** | `scribe_v1` |
| **Base URL** | `https://api.elevenlabs.io/v1` |
| **Graceful degradation** | Text fallback, session preserved, memory preserved |
| **Barge-in** | Supported (stream cancellation) |
| **Conversation persistence** | Supported |

## SECTION 6 — Configuration Changes Applied (this session)

| Change | File | Reason |
|---|---|---|
| Added `!/.env.example` to `.gitignore` | `.gitignore` | `.env.example` was gitignored by `.env.*` pattern |
| Added `data/long_term_memory.json` to `.gitignore` | `.gitignore` | Runtime test artifact |
| Renamed `SMTP_SERVER` to `SMTP_HOST` in `.env.example` | `.env.example` | Code reads `SMTP_HOST` (B4) |
| Added missing vars to `.env.example` | `.env.example` | Stripe, ElevenLabs, Celery, etc. |
| Added `RuntimeError` if `JWT_SECRET_KEY` is unset | `jwt_handler.py` | Prevents silent auth failure (B3) |
| Converted CORS origins to use `CORS_ORIGINS` env var | `main.py` | Production URLs needed (was hardcoded localhost) |
| Added `release/**` to CI push triggers | `.github/workflows/tests.yml` | CI never ran on release branch (B5) |
| Added `JWT_SECRET_KEY`/`SWARM_DB_URL`/`DATABASE_URL` to CI env | `.github/workflows/tests.yml` | CI would crash without B3 fix (no JWT key) |

## SECTION 7 — Frozen Configuration HASH

```
Config version: 1.0.0-rc.1
Date: 2026-07-26
Files locked:
  - .env.example (28 vars)
  - .gitignore (76 lines)
  - docker-compose.yml (67 lines, 3 services)
  - .github/workflows/tests.yml (31 lines)
  - main.py (CORS origins now configurable)
  - interfaces/api/auth/jwt_handler.py (SECRET_KEY validation)
```

**Configuration is FROZEN.** No further changes without Release Engineering Director approval.
