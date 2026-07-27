# Staging Validation Checklist

**Branch:** `release/v1.0.0-rc.1`
**Commit:** `e17c79f`

---

## Environment

- [ ] Staging server provisioned (or Docker host available)
- [ ] PostgreSQL 16 running and reachable
- [ ] Redis 7 running and reachable
- [ ] DNS records: `staging.realms2riches.com` → staging IP
- [ ] SSL certificates provisioned

## Configuration

- [ ] `JWT_SECRET_KEY` set (256-bit+ random value)
- [ ] `DATABASE_URL` set to staging PostgreSQL
- [ ] `REDIS_URL` set to staging Redis
- [ ] `FRONTEND_URL` set to `https://staging.realms2riches.com`
- [ ] `BACKEND_URL` set to `https://api.staging.realms2riches.com`
- [ ] `CORS_ORIGINS` set to staging URLs
- [ ] `STRIPE_API_KEY` set to **test** key (`sk_test_*`)
- [ ] `STRIPE_WEBHOOK_SECRET` set to test webhook secret
- [ ] `ELEVENLABS_API_KEY` set
- [ ] `SMTP_HOST` set (not `SMTP_SERVER`)
- [ ] `ENV` set to `staging`
- [ ] `LOG_LEVEL` set to `DEBUG` (for first validation)

## Backend

- [ ] `docker compose up -d` starts without errors
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] `GET /ready` returns `{"status": "ready"}`
- [ ] `GET /docs` renders OpenAPI UI
- [ ] `POST /api/auth/register` creates a user
- [ ] `POST /api/auth/login` returns JWT
- [ ] `POST /api/auth/refresh` returns new access token
- [ ] `POST /api/voice/session` returns session ID

## Frontend

- [ ] `cd frontend && npx next build` passes
- [ ] `GET /` renders landing page
- [ ] `/login` page loads
- [ ] `/dashboard` page loads (authenticated)
- [ ] `/agents` page loads (authenticated)
- [ ] `/billing` page loads (authenticated)
- [ ] `/onboarding` page loads
- [ ] `/robots.txt` returns valid robots
- [ ] `/sitemap.xml` returns valid sitemap

## Voice System

- [ ] Voice component loads on landing page
- [ ] Voice session can be created
- [ ] Speech-to-text works (if ElevenLabs key valid)
- [ ] Text-to-speech works (if ElevenLabs key valid)
- [ ] Graceful degradation: unset ElevenLabs key → text fallback
- [ ] Barge-in: new input cancels current stream

## Authentication

- [ ] Register → Login → Access protected route
- [ ] Invalid credentials → 401
- [ ] Expired token → 401 → refresh → new token
- [ ] Token revocation (with Redis): revoke → subsequent request returns 401

## Subscription Flow

- [ ] `/billing` loads with subscription options
- [ ] Stripe Checkout session creates successfully (test mode)
- [ ] Success redirect: `/success?session_id=...`
- [ ] Cancel redirect: `/cancel`

## Monitoring

- [ ] Logs show startup sequence without errors
- [ ] Structured log output format verified
- [ ] No secrets or keys in logs
- [ ] JWT startup diagnostic logged (prefix only)

## Docker

- [ ] `docker build -t swarmlead-api .` succeeds
- [ ] `docker compose up -d` starts all 3 services
- [ ] Postgres health check passes
- [ ] Redis health check passes
- [ ] API container starts after Postgres + Redis are healthy
