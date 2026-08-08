# Genesis Forge — by Realms 2 Riches

**Launch your business with your voice.**

Genesis Forge is the first autonomous business launch platform powered by
constitutional voice AI. Speak your vision — the platform provisions a
business, qualifies leads, drafts outreach, and runs the whole operation
with a 19-agent workforce — while every external action stays behind a
single human approval gate.

> **Product Hunt launch: Monday, August 3, 2026 12:01 AM.**
> The landing page runs an animated countdown to that moment.

---

## 🎙️ The Voice Agent — your live salesperson

A full-duplex voice assistant lives on the landing page (`VoiceLandingAgent`)
and starts talking to visitors within seconds. It:

- **Leads the conversation** — proactive greeting, guided discovery,
  qualification, plan recommendation, and sign-up steering.
- **Understands the product** — replies are grounded in the real docs via
  RAG (`core/services/product_knowledge.py`).
- **Never freezes** — a 25s LLM cap falls back to intent-matched scripted
  replies, so the visitor never stares at a silent agent.
- **Supports barge-in** — interrupt it mid-sentence and it stops instantly.
  Detection uses an attack/hold envelope with an adaptive threshold, and a
  higher threshold automatically arms when the microphone lacks echo
  cancellation.
- **Captures leads by voice** — when a visitor asks to be contacted, the
  widget drops a lead card; the email lands in the CRM as a high-intent
  (`source: voice`) lead.
- **Runs on YOUR trained model** — the model is pluggable via `VOICE_MODEL`.
  See **[docs/voice_model_integration.md](docs/voice_model_integration.md)**.

### What to say to the voice agent (demo script)

| You say | It does |
| --- | --- |
| "I want to launch a business" | Starts the launch discovery flow |
| "I need help qualifying leads" | Explains inbound lead qualification |
| "What are the pricing plans?" | Recommends a plan from your answers |
| "Please contact me, leave my email" | Opens the lead-capture card |
| "Tell me about workflows" | Walks through the Workflows page |
| "What is an agentic OS?" | Answers from the docs (RAG) |

### Voice agent endpoints

| Route | Purpose |
| --- | --- |
| `POST /api/voice/session` | Create a session → greeting + audio |
| `POST /api/voice/message` | Send a message → guided reply + audio |
| `POST /api/voice/end` | End / clean up a session |
| `GET /api/voice/models` | Which model is powering the assistant |
| `POST /api/voice/capture` | Persist a voice-captured lead |

### Plug in your trained model

```env
# .env.docker.local
VOICE_MODEL=genesis-voice:latest
VOICE_MODEL_BASE_URL=http://host.docker.internal:11434
```

Restart the API container. Verify with `GET /api/voice/models` (Autonomy
console shows it live too). Full workflow + tuning knobs:
**[docs/voice_model_integration.md](docs/voice_model_integration.md)**.

A ready-to-`ollama create` Modelfile (with the Genesis system prompt baked in)
lives at **`models/genesis-voice/Modelfile`** — replace the base/adapters with
your trained weights and the landing agent runs on them.

### Voice agent field guide (troubleshooting)

| Symptom | Fix |
| --- | --- |
| Agent never talks | Check the ElevenLabs key; the widget falls back to browser TTS automatically |
| Replies feel scripted | Slow local LLM hit the 25s cap — raise `VoiceAgentService._llm_timeout_s` or wire a fast hosted model via `VOICE_MODEL_BASE_URL` |
| Barge-in too eager | Raise `BARGE_IN_THRESHOLD` in `frontend/src/lib/voice-engine.ts` |
| Barge-in misses speech | Lower `BARGE_IN_ATTACK_FRAMES`; the adaptive noise floor self-tunes per mic, so noisy rooms get a higher effective threshold automatically |
| Wrong model active | `GET /api/voice/models` — if `source` says `default`, `VOICE_MODEL` isn't reaching the container |
| Mic sounds echo-y | The mic re-arms with a higher threshold when the browser has no echo cancellation |

---

## 🚀 Product Hunt launch kit

- **Landing page**: animated countdown (live badge after launch), voice agent,
  plan-finder quiz, ROI calculator, exit-intent popup, 30-point checklist
  magnet, live activity ticker, social share buttons, referral banner,
  integrations strip, monthly/annual pricing toggle, testimonials, FAQ,
  comparison table.
- **Feature showcase**: 20 features across four groups (Voice Concierge,
  Revenue & Lead Growth, Launch & Growth Ops, Sales & Operations Spine).
- **Launch Studio**: `frontend/src/app/launch/page.tsx` — one page that runs
  the whole launch: the vocally guided company concierge, nurture plans, and
  outreach maximization levers (`/api/launch/concierge/*`, `/launch/maximize`,
  `/launch/nurture/*` in `interfaces/api/routers/launch_ext.py`).
- **Traffic engine**: the growth loop composes X/LinkedIn/Facebook/Reddit/PH
  posts into your approval queue during launch week (`/api/launch/traffic/drafts`);
  your explicit daily job list is **`docs/launch_traffic_playbook.md`**.
- **Launch API**: `GET /api/launch/status` (promo `LAUNCH100`, share links,
  referral config) + `GET /api/launch/activity` (real launch-week metrics)
  power the landing page share buttons and the live activity ticker.
- **Launch plan**: `docs/ph_launch_plan.md`
- **Voice-of-market research**: `docs/marketing_voice.md`
- **Revenue projection**: `docs/mrr_projection.md`
- **SEO**: 12 programmatic industry pages (`/industries/[slug]`) with JSON-LD
  + sitemap.

---

## 🔁 The Autonomous Growth Loop

Runs on a configurable cycle (`GROWTH_CYCLE_HOURS`, default 6h) with seven
isolated phases — one failure never kills a cycle:

1. **Discovery** — search-verified real businesses that publish a contact
   email (Bing RSS + DuckDuckGo, then crawl the site). Rejects reserved/test
   domains, role inboxes, big brands, and disposable domains; MX-validates.
   Never emails anyone. (`core/services/lead_discovery.py`)
2. **SEO** — programmatic page specs across a rotating 12-industry pool.
3. **Content** — blog/social/email drafts from the GTM task array.
4. **Outreach** — drafts personalized outreach into the **approval queue**.
   Business-domain leads only; reserved/disposable/free-email test artifacts
   and suppressed addresses are never drafted.
5. **Traffic** — during launch week, composes ready-to-post social + Product
   Hunt copy into the **approval queue** (never posts on its own).
6. **Voice** — learns keyword boosts from retrieval analytics so the voice
   agent answers better over time.
7. **Monetize** — composes Stripe checkout offers for high-intent leads into
   the **approval queue**.

### Single human gate

Every external action (email send, payment quote) lands behind the founder's
approval queue. The loop only *prepares* — it never sends or charges without
an explicit `approve`. (`docs/governance/ENFORCEMENT.md` §4.4)

### Lead Discovery Accuracy

- Business-domain emails preferred over free-email inboxes (intent score).
- MX-record validation before a lead enters the pipeline.
- Durable suppression (bounces/unsubscribes/complaints) — purged rows are
  also marked `email_invalid` in Postgres so state survives container recreates.
- Per-domain outreach caps (max 2/cycle) to protect sender reputation.

---

## 📧 Deliverability & the email alias

Cold outreach from a personal Gmail is filtered aggressively. Genesis ships a
deliverability engine that generates SPF/DKIM/DMARC records, live DNS checks,
and a 0–100 sender-health score, plus the recommended **branded sending
alias** (`hello@realms2riches.com`). Full walkthrough:
**[docs/email_alias.md](docs/email_alias.md)**.

```bash
curl "http://localhost:8000/api/deliverability/alias?domain=realms2riches.com"
curl "http://localhost:8000/api/deliverability/score"
```

`OUTREACH_DRY_RUN=0` enables real sends. Until your DNS is verified, keep it
at `1` — the loop will happily rehearse drafts with zero risk.

---

## ☸️ Kubernetes / multi-tenant

Manifests in `infrastructure/k8s/` (base + production overlay):

- Stateless API deployment (replicas 2) + ClusterIP/headless services
- HorizontalPodAutoscaler (CPU + memory, 2–6 replicas)
- Postgres StatefulSet + Redis (persistent volumes)
- ConfigMap for non-secret config, Secret for credentials
- Ingress with TLS + cert-manager annotations

```bash
kubectl create ns genesis
kubectl apply -k infrastructure/k8s/overlays/production/
```

Multi-tenant is **namespace-first**: create a namespace per tenant/box and
re-apply with tenant-scoped Secrets; `core/middleware/tenant_context.py`
isolates requests by tenant. `infrastructure/deployment/box_deployer.py` is
the container-side counterpart.

---

## 🧱 Core Platform

- **Leads**: capture, enrichment, workflow routing, timeline
- **Outreach**: campaigns, queueing, worker architecture, sequences
- **Workflows**: multi-step, persisted, completion tracking
- **Tickets**: lifecycle, history, department routing
- **Tenants**: registration, provisioning, runtime monitoring
- **19-agent workforce**: SEO, outreach, content, builder, voice, growth,
  concierge, nurture, maximization, and more.

## Stack

FastAPI · SQLAlchemy · Redis · Celery · Docker · Kubernetes (manifests) ·
Next.js (frontend) · LangChain-compatible agent core · dnspython · httpx ·
ElevenLabs (TTS/STT) · Ollama (local LLM)

---

## 🧑‍💻 Local Development

Backend (from repo root):

```bash
python -m venv venv
source venv/bin/activate            # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set secrets (JWT, Stripe, SMTP, ElevenLabs).

```bash
uvicorn main:app --reload
```

- API: `http://localhost:8000` · Swagger: `http://localhost:8000/docs`

Frontend (in `frontend/`):

```bash
npm install
npm run dev                        # http://localhost:3000
```

The Next.js dev server proxies `/api/*` and `/health` to `API_BACKEND_URL`
(default `http://localhost:8000`).

## Docker (full stack in one command)

```bash
docker compose up --build
```

Brings up Postgres + Redis + API (port 8000) + frontend (port 3000).
`OUTREACH_DRY_RUN` and `GROWTH_DISCOVERY` live in `.env.docker.local`.
Frontend container env (`frontend/.env.docker`): empty = defaults; set
`FRONTEND_URL` for the canonical site URL used in share links.

> If you have older manually started containers (`swarmlead-*`) still
> running, remove them first so compose can take over the names:
> `docker rm -f swarmlead-api swarmlead-frontend swarmlead-postgres swarmlead-redis`

## CLI

```bash
python cli.py launch        # voice-guided company concierge launch
python cli.py status        # workspace status / growth loop state
```

Run `python cli.py --help` for the full command list.

## Growth Loop Env

| Var | Default | Meaning |
| --- | --- | --- |
| `GROWTH_AUTO_MODE` | `1` | start the loop on API boot |
| `GROWTH_CYCLE_HOURS` | `6` | hours between cycles |
| `GROWTH_USE_LLM` | `0` | LLM content generation (slow on CPU) vs deterministic scaffold |
| `GROWTH_DISCOVERY` | `1` | run live web lead discovery |
| `OUTREACH_DRY_RUN` | `1` | dry-run sends (log only) — set `0` for real mail |
| `OUTREACH_RATE_LIMIT_PER_HOUR` | `40` | SMTP send rate cap |
| `VOICE_MODEL` | *(unset)* | custom Ollama model powering the voice agent |
| `VOICE_MODEL_BASE_URL` | `OLLAMA_API_BASE` | endpoint for the voice model |
| `VOICE_MODEL_OVERRIDES` | *(unset)* | per-model `temp,top_p,max_tokens` tuning |
| `SMTP_FROM` | `SMTP_USER` | branded sending address (alias) |
| `LAUNCH_URL` | `https://realms2riches.com` | site URL used in share links |
| `PRODUCT_HUNT_URL` | PH `genesis-5` | PH page used in share links |

## Testing

```bash
python tests/run_tests.py <files> -p no:cacheprovider   # targeted backend suite
pytest tests/unit -v      # backend unit tests
pytest tests/integration -v
cd frontend && npx vitest run    # frontend unit tests
cd frontend && npx tsc --noEmit  # frontend typecheck
cd frontend && npm run build     # production build
python -m ruff check core interfaces tests utils   # lint (CI scope)
```

## Project Structure

```text
core/
├── agents/          # 19 specialized agents (seo, outreach, content, voice, builder, ...)
├── services/        # growth_automation, lead_discovery, deliverability, voice_agent_service,
│                    # voice_model (pluggable LLM), launch_config (PH campaign), email_sender,
│                    # monetization, product_knowledge
├── models/          # Lead, Ticket, User, ...
├── persistence/     # SQLAlchemy session + linear engine
├── orchestration/   # workflow orchestration
├── analytics/       # event tracking
└── workflows/

interfaces/
├── api/routers/     # growth, deliverability, acquisition, launch, voice, auth, payments, ...
└── cli/

models/
└── genesis-voice/   # Modelfile + system prompt for your trained voice model

infrastructure/
├── k8s/             # Kubernetes manifests (base + production overlay)
├── deployment/      # box_deployer
├── outreach/        # worker + campaign queueing
├── queue/
└── celery/

frontend/
├── src/app/         # Next.js App Router (landing, autonomy console, tools)
├── src/components/  # landing (voice agent, countdown, ROI calc) + UI kit
└── src/hooks/       # react-query hooks

tests/
├── unit/
├── integration/
└── migration/
```

## Current Status

- Migration: ✅ Complete
- Backend: ✅ Production Candidate
- Tests: ✅ 1500+ passing · 96% coverage (see `pytest`)
- Docker: ✅ Configured (API + frontend + Postgres + Redis — one `docker compose up`)
- Kubernetes: ✅ Manifests + HPA + overlay
- Frontend: ✅ Live (landing with 20+ grouped features, Launch Studio, autonomy console, voice agent)
- Launch: ✅ Live on Product Hunt (launch week traffic engine running)

## Docs

- `docs/ph_launch_plan.md` — Product Hunt launch playbook
- `docs/launch_traffic_playbook.md` — your explicit daily traffic job list
- `docs/voice_model_integration.md` — run the agent on your trained model
- `docs/email_alias.md` — branded sending alias + DNS records
- `docs/mrr_projection.md` — honest revenue projection + funnel math
- `docs/marketing_voice.md` — voice-of-the-market research
- `docs/governance/ENFORCEMENT.md` — how the single approval gate is enforced

## License

Proprietary.
