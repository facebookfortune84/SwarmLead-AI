# Environment Validation Report

**Date:** 2026-07-26

---

## Active Environment (`.env`)

| Variable | Current Value | Production Value Required |
|---|---|---|
| `ENV` | `development` | `production` |
| `FRONTEND_URL` | `http://localhost:3000` | `https://realms2riches.com` |
| `BACKEND_URL` | `http://localhost:8000` | `https://api.realms2riches.com` |
| `CORS_ORIGINS` | `http://localhost:8000, http://localhost:3000` | `https://realms2riches.com,https://api.realms2riches.com` |
| `STRIPE_API_KEY` | `sk_live_*` (LIVE) | Use test key for dev, live for prod |
| `SMTP_*` | Gmail config with `SMTP_SERVER` | Use `SMTP_HOST` (not `SMTP_SERVER`) |
| `JWT_SECRET_KEY` | `5c41277b...` (set) | New key for production |

## Issues Found

| # | Issue | Severity | Notes |
|---|---|---|---|
| E1 | `ENV=development` but **live Stripe key** is used | HIGH | Dev should use `sk_test_*`. Live charges could accidentally be created. |
| E2 | `SMTP_SERVER` used instead of `SMTP_HOST` | MEDIUM | Code reads `SMTP_HOST` — email silently fails in this config. Fix by setting `SMTP_HOST=smtp.gmail.com`. |
| E3 | `IMAP_USER`/`IMAP_PASS`/`IMAP_SERVER` | LOW | Set in `.env` but not read by any code. Dead config. |
| E4 | `CORS_ORIGINS` has space after comma | LOW | Code handles spaces via `.strip()`, but inconsistent. |
| E5 | No `JWT_ALGORITHM`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_HOSTING_PRICE_ID`, `ELEVENLABS_DEFAULT_VOICE_ID`, `SMTP_FROM`, `CELERY_*`, `TECH_DOMAIN` | LOW | Missing from `.env`. All have safe defaults or are optional. |

## `.env.example` Validation

| Criteria | Status |
|---|---|
| Contains all mandatory vars | ✅ `JWT_SECRET_KEY`, `DATABASE_URL`, `FRONTEND_URL` |
| Uses `SMTP_HOST` (not `SMTP_SERVER`) | ✅ Fixed in previous session |
| Includes Stripe vars | ✅ `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_HOSTING_PRICE_ID` |
| Includes ElevenLabs vars | ✅ `ELEVENLABS_API_KEY`, `ELEVENLABS_DEFAULT_VOICE_ID` |
| No hardcoded secrets | ✅ All values blank |
| Tracked in git | ✅ Un-ignored and staged |

## `.env.docker` Validation

| Criteria | Status | Notes |
|---|---|---|
| JWT_SECRET_KEY set | ✅ | Hardcoded — for local dev only. Not production-safe. |
| DATABASE_URL set | ✅ | Points to `postgres` service in Docker network |
| REDIS_URL set | ✅ | Points to `redis` service in Docker network |
| ACCESS_TOKEN_EXPIRE_MINUTES | ✅ | 120 min default |
| REFRESH_TOKEN_EXPIRE_DAYS | ✅ | 30 day default |
| Missing vars | ⚠️ | No FRONTEND_URL, CORS_ORIGINS, STRIPE_API_KEY, ELEVENLABS_API_KEY |

## Production Deployment Checklist

- [ ] Generate new `JWT_SECRET_KEY` (256-bit random, not the hardcoded dev key)
- [ ] Set `ENV=production`
- [ ] Set `FRONTEND_URL=https://realms2riches.com`
- [ ] Set `BACKEND_URL=https://api.realms2riches.com`
- [ ] Set `CORS_ORIGINS=https://realms2riches.com,https://api.realms2riches.com`
- [ ] Set `DATABASE_URL` with production PostgreSQL credentials
- [ ] Set `REDIS_URL` with production Redis URL
- [ ] Use fresh `STRIPE_API_KEY` live key (current live key in `.env` may be valid, but should be moved to vault)
- [ ] Set `STRIPE_WEBHOOK_SECRET` for async payment events
- [ ] Use `SMTP_HOST` (not `SMTP_SERVER`)
- [ ] Set `STRIPE_HOSTING_PRICE_ID` with actual price ID from Stripe dashboard
