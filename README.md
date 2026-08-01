# SwarmLead-AI (SwarmOS)

Production-ready autonomous lead generation, outreach, workflow orchestration,
tenant lifecycle management, voice agent, and self-optimizing growth platform.

## Features

### Autonomous Growth Loop (`core/services/growth_automation.py`)
Runs on a configurable cycle (`GROWTH_CYCLE_HOURS`, default 6h) and executes six
phases, each isolated so one failure never kills a cycle:

1. **Discovery** — finds *real* businesses that publish a contact email on their
   own website (Bing RSS + DuckDuckGo search, then crawling the business site).
   Validates every address: reserved/test domains (example.com, test.co) are
   rejected, role inboxes (noreply@, info@) are skipped, the domain must have a
   working MX record. Only writes verified leads to the DB. Never emails anyone.
2. **SEO** — generates programmatic SEO page specs + technical SEO drafts across
   a rotating 12-industry pool (3 new pages per cycle, cumulative and deduped).
3. **Content** — drafts blog/social/email assets from the GTM task array.
4. **Outreach** — drafts personalized outreach for qualified leads and places
   each send in the **approval queue**. Business-domain leads only; reserved,
   disposable, free-email test artifacts and suppressed addresses are never drafted.
5. **Voice** — reads knowledge-retrieval analytics and learns keyword boosts so
   the voice agent answers better over time.
6. **Monetize** — scores the funnel, composes Stripe checkout offers for
   high-intent leads, and places each quote in the **approval queue**.

### Single Human Gate
Every external action (email send, payment quote) lands behind the founder's
approval queue. The loop only ever *prepares* — it never sends or charges without
an explicit `approve`. This honors the `ai_drafted_human_reviewed` rule
(`docs/governance/ENFORCEMENT.md` §4.4).

### Lead Discovery Accuracy
Replaces naive "public records" scraping (which produced non-response mailboxes
and generic addresses) with search-verified businesses:

- Business-domain emails preferred over free-email inboxes (intent score).
- MX-record validation before a lead enters the pipeline.
- Suppression list (bounces / unsubscribes / complaints) so dead or angry
  addresses are never retried.
- Per-domain outreach caps (max 2/cycle) to protect sender reputation.

### Deliverability Engine (`core/services/deliverability.py`)
- SPF / DKIM / DMARC record generator with copy-paste DNS records.
- Live DNS verification and a 0–100 sender health score with grade.
- Persistent suppression list consulted by the growth loop.

### Voice Agent
Full-duplex voice agent with LLM cap + scripted fallback + knowledge grounding.
Tracks product knowledge and self-tunes via retrieval analytics.

### Monetization
Stripe checkout link generation, three tiers (Starter $29 / Growth $99 /
Enterprise $299), referral program, and upsell recommendations.

### Core Platform
- Lead management + enrichment pipeline + workflow routing
- Outreach campaigns, email queueing, worker architecture, sequence orchestration
- Multi-step workflows with persistence and completion tracking
- Ticketing with lifecycle, history, and department routing
- Tenant registration, provisioning, Docker deployment, runtime monitoring
- 15-agent workforce (SEO, outreach, content, builder, voice, growth, etc.)

## Stack

FastAPI · SQLAlchemy · Redis · Celery · Docker · Next.js (frontend) ·
LangChain-compatible agent core · dnspython (DNS verification) · httpx

## Local Development

```bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set secrets (JWT, Stripe, SMTP, ElevenLabs).

```bash
uvicorn main:app --reload
```

- API: `http://localhost:8000` · Swagger: `http://localhost:8000/docs`
- Frontend: `cd frontend && npm run dev` → `http://localhost:3000`

## Docker

```bash
docker compose build
docker compose up
```

The API and frontend run as containers. `OUTREACH_DRY_RUN=1` in
`.env.docker.local` keeps outreach in dry-run (log-only) mode; flip to `0` to
enable real sends. `GROWTH_DISCOVERY=1` enables live web lead discovery.

## Growth Loop Env

| Var | Default | Meaning |
| --- | --- | --- |
| `GROWTH_AUTO_MODE` | `1` | start the loop on API boot |
| `GROWTH_CYCLE_HOURS` | `6` | hours between cycles |
| `GROWTH_USE_LLM` | `0` | use LLM content generation (slow on CPU) vs deterministic scaffold |
| `GROWTH_DISCOVERY` | `1` | run live web lead discovery |
| `OUTREACH_DRY_RUN` | `1` | dry-run sends (log only) — set `0` for real mail |
| `OUTREACH_RATE_LIMIT_PER_HOUR` | `40` | SMTP send rate cap |

## Testing

```bash
pytest -v                 # full suite
pytest tests/unit -v      # unit tests
pytest tests/integration -v
```

## Project Structure

```text
core/
├── agents/          # 15 specialized agents (seo, outreach, content, voice, builder, ...)
├── services/        # growth_automation, deliverability, lead_discovery, email_sender,
│                    # monetization, product_knowledge, ...
├── models/          # Lead, Ticket, User, ...
├── persistence/     # SQLAlchemy session + linear engine
├── orchestration/   # workflow orchestration
├── analytics/       # event tracking
└── workflows/

interfaces/
├── api/routers/     # growth, deliverability, acquisition, auth, payments, ...
└── cli/

infrastructure/
├── deployment/
├── outreach/        # worker + campaign queueing
├── queue/
└── celery/

frontend/
├── src/app/         # Next.js App Router (autonomy console, tools, landing)
├── src/components/  # UI kit + layout
└── src/hooks/       # react-query hooks (growth, leads, ...)

tests/
├── unit/            # 790+ tests incl. growth loop, discovery, deliverability
├── integration/
└── migration/
```

## Current Status

- Migration: ✅ Complete
- Backend: ✅ Production Candidate
- Tests: ✅ 798 Passing (unit) · 86% coverage
- Docker: ✅ Configured (API + frontend + Postgres + Redis + Ollama)
- Frontend: ✅ Live (autonomy console, business-skeleton tool, landing)

## Docs

- `docs/ph_launch_plan.md` — Product Hunt launch playbook
- `docs/mrr_projection.md` — honest revenue projection + funnel math
- `docs/marketing_voice.md` — voice-of-the-market research

## License

Proprietary.
