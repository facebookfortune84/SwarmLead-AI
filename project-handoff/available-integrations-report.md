# Available Integrations Report

**Date:** 2026-07-26
**Source:** `.env.bak` (backup environment)

---

## LLM Providers

| Provider | Key Status | Potential Usage | Runtime Benefit |
|---|---|---|---|
| **Groq** (`GROQ_API_KEY`) | ✅ Configured | OpenAI-compatible API for fast LLM inference | Higher throughput than local Ollama |
| **Google AI** (`GOOGLE_API_KEY`) | ✅ Configured | Gemini models via Google AI API | Alternative LLM provider for agents |
| **Anthropic** (`ANTHROPIC_API_KEY`) | ✅ Configured | Claude models (Opus, Sonnet) | High-quality reasoning for governance/planning agents |
| **Ollama** (`OLLAMA_URL`) | ✅ Configured (local) | Local LLM inference (default) | Currently the active LLM backend |

## Voice

| Provider | Key Status | Potential Usage | Runtime Benefit |
|---|---|---|---|
| **ElevenLabs** (`ELEVENLABS_API_KEY`) | ✅ Configured | STT/TTS for voice system | Currently active in voice pipeline |

## Payments

| Provider | Key Status | Notes |
|---|---|---|
| **Stripe** (`STRIPE_API_KEY`) | ✅ LIVE key in `.env` | Active. Should use test key for dev. |

## Email

| Provider | Key Status | Notes |
|---|---|---|
| **SMTP (Gmail)** (`SMTP_USER`/`SMTP_PASS`) | ✅ Configured | Active but uses `SMTP_SERVER` — code reads `SMTP_HOST`. |

## Cloud Infrastructure

| Provider | Key Status | Potential Usage |
|---|---|---|
| **IONOS** (`IONOS_API_PUBLIC_PREFIX`, `IONOS_API_SECRET`) | ✅ Configured | Cloud VM provisioning for tenants |
| **Cloudflare** (`CLOUDFLARE_TUNNEL_TOKEN`) | ✅ Configured | Tunnel for ingress to self-hosted services |
| **Docker Registry** (`DOCKER_REGISTRY_HOST=ghcr.io`) | ⚠️ No credentials | Registry host set but no GHCR login configured |

## Social / Marketing

| Provider | Key Status | Potential Usage |
|---|---|---|
| **Facebook** (`FACEBOOK_APP_ID`, `FACEBOOK_PAGE_TOKEN`) | ✅ Configured | Social advertising, page management |
| **LinkedIn** (`LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_CLIENT_ID`) | ✅ Configured | B2B outreach, lead generation |
| **Linear** (`LINEAR_API_KEY`) | ✅ Configured | Project management integration |

## Monitoring (NOT configured)

| Provider | Key Status |
|---|---|
| **Sentry** (`SENTRY_DSN`) | ❌ Empty |
| **Umami Analytics** (`UMAMI_APP_SECRET`) | ❌ Empty |
| **OpenTelemetry** (`OTEL_OTLP_ENDPOINT`) | ❌ Empty |
| **CrewAI Telemetry** (`CREWAI_DISABLE_TELEMETRY=true`) | ⚠️ Explicitly disabled |

## Summary

**Currently active in runtime:**
- ElevenLabs (voice STT/TTS)
- Stripe (payments)
- Ollama (local LLM)
- SMTP (email — needs `SMTP_HOST` fix)

**Available but not wired into runtime:**
- Groq, Google AI, Anthropic — all available for LLM inference but not configured as providers
- IONOS — cloud provisioning available
- Cloudflare — tunnel available
- Facebook, LinkedIn — social integrations available but no runtime consumers

**Monitoring gap:** No error tracking (Sentry), no analytics (Umami), no APM (OpenTelemetry). All monitoring is currently limited to application logs.
