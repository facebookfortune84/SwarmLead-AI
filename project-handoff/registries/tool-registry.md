# Tool Registry

**Generated**: 2026-07-24  
**Sources**: `core/`, `infrastructure/`, `interfaces/`, `utils/`, `configs/`  
**Classification Rules**: Active | Deprecated | Archive Candidate | Delete Candidate | Unknown

---

## LLM & AI Tools

| Tool Name | Purpose | Dependencies | Users | Agent Consumers | Governance Concerns | Status | Confidence |
|-----------|---------|--------------|-------|-----------------|---------------------|--------|------------|
| OllamaClient | Local LLM inference with retry, fallback, concurrency control | httpx, ConfigLoader, logging | All agents via BaseAgent | StrategyAgent, OutreachAgent, BuilderAgent, RepairAgent, ReviewAgent | Constitution §7: Secrets never agent-touchable (API keys not used); §5: Financial = human approval (LLM costs); ADR-009: Single-machine-first (local LLM) | Active | 0.95 |
| ArchetypeSelector | Select appropriate archetype per agent with adaptive weights | AssetLoader, AdaptiveWeights, optimized_archetypes.json | Orchestration layer | All agents at startup | Constitution §3: No self-graded homework (selection ≠ verification); ADR-008: Documentation-driven | Active | 0.90 |
| AssetLoader | Load archetype assets from optimized storage | optimized_archetypes.json, archetype_weights.json | ArchetypeSelector | All agents | Constitution §7: Secrets never agent-touchable (assets are prompts, not secrets) | Active | 0.90 |
| AssetOptimizer | Build-time: raw DNA → optimized archetypes (scoring, classification) | archetype_classification_report.json, archetype_registry.json, archetype_weights.json | CI/build pipeline | None (build-time) | ADR-001: No self-graded homework (automated classification); ADR-007: Repository Intelligence | Active | 0.90 |
| AdaptiveWeights | Dynamic weight adjustment from performance feedback | archetype_weights.json | ArchetypeSelector at runtime | All agents | Constitution §12: Continuous Improvement Framework; evidence-based adaptation | Active | 0.90 |

---

## Memory & Storage Tools

| Tool Name | Purpose | Dependencies | Users | Agent Consumers | Governance Concerns | Status | Confidence |
|-----------|---------|--------------|-------|-----------------|---------------------|--------|------------|
| SessionMemory | Ephemeral in-memory key-value store for single execution | None (pure Python dict) | BaseAgent, CampaignPipeline, FeedbackLoop | All agents via BaseAgent.session_memory | Constitution §4: Organizational Memory System; data isolation per session | Active | 0.95 |
| LongTermMemory | Persistent JSON file storage with metadata enrichment | `data/long_term_memory.json`, `json`, `datetime` | BaseAgent, CampaignPipeline, FeedbackLoop, StrategyAgent, OutreachAgent | All agents via BaseAgent.long_term_memory | Constitution §4.6: Portfolio isolation (currently shared file - **gap**); §4: Organizational Memory | Active | 0.85 |
| VectorStore | Lightweight semantic search (keyword overlap v1, embeddings planned) | None (pure Python) | BaseAgent, FeedbackLoop | All agents via BaseAgent.vector_store | Constitution §4: Organizational Memory; future: embedding model licensing | Active | 0.80 |
| S3Client | Object storage abstraction (S3-compatible or local filesystem) | `boto3` (optional), `os`, `pathlib`, `logging` | FileManager, TenantService | Tenant Service, Deployment agents | Constitution §7: Secrets never agent-touchable (credentials via env); §14: Vendor governance (S3 provider) | Active | 0.90 |
| FileManager | Company archive management (upload, download, metadata, cleanup) | S3Client, `logging` | TenantService | Tenant Service, Deployment agents | Constitution §4.6: Portfolio isolation (per-company prefixes); §7: Secrets never agent-touchable | Active | 0.90 |

---

## Database & Persistence Tools

| Tool Name | Purpose | Dependencies | Users | Agent Consumers | Governance Concerns | Status | Confidence |
|-----------|---------|--------------|-------|-----------------|---------------------|--------|------------|
| Database Session (SessionLocal, get_db) | SQLAlchemy session factory with SQLite/PostgreSQL dual support | `sqlalchemy`, `core.persistence.base.Base` | All services, API routers, Celery tasks | All services via dependency injection | Constitution §4.6: Portfolio isolation (single DB - **gap**); §7: Secrets never agent-touchable (DB URL via env) | Active | 0.90 |
| LinearEngine | Compatibility layer for v2→v3 migration; bridges legacy patterns | `core.models.*`, `sqlalchemy` | Legacy compatibility, some services | Migration/legacy paths | ADR-004: Organizational Memory System; migration completeness | Active | 0.85 |
| TicketHistory Persistence | Ticket audit trail persistence | `core.models.ticket_history.TicketHistory`, `sqlalchemy` | TicketService | Ticket Service | Constitution §3: Legible authorship (audit trail); §12: Tamper-evident audit logging | Active | 0.95 |

---

## Queue & Task Tools

| Tool Name | Purpose | Dependencies | Users | Agent Consumers | Governance Concerns | Status | Confidence |
|-----------|---------|--------------|-------|-----------------|---------------------|--------|------------|
| CeleryApp | Distributed task queue with Redis broker/backend; DLQ, retries, monitoring | `celery`, `redis`, `kombu`, `infrastructure.celery.*_tasks` | All async workers | Outreach Worker, Notification Tasks, Ticket Tasks, Workflow Tasks | Constitution §5: Financial/legal = human-mediated (tasks gated); §12: Monetary rules (payment tasks); §13: Agent identity (task attribution) | Active | 0.95 |
| TaskQueue | Lightweight Redis queue with in-process fallback | `redis` (optional), `queue.Queue` (fallback) | Outreach Worker, simple async tasks | Outreach Worker | Constitution §5: Autonomy by domain (outreach = agent-autonomous); §7: Secrets (Redis URL via env) | Active | 0.90 |
| Celery Workers (notification, ticket, workflow) | Background task processors for specific domains | CeleryApp, respective services | Celery beat/scheduler | Respective domain agents | Constitution §5: Domain autonomy; §12: Payment tasks require human approval | Active | 0.90 |

---

## Deployment & Infrastructure Tools

| Tool Name | Purpose | Dependencies | Users | Agent Consumers | Governance Concerns | Status | Confidence |
|-----------|---------|--------------|-------|-----------------|---------------------|--------|------------|
| BoxDeployer | Docker-based tenant isolation (container provisioning, Hyper-V fallback) | `docker`, `subprocess`, `powershell` (Windows), `os`, `pathlib`, `re`, `uuid` | TenantService | Tenant Service, Deployment agents | Constitution §4.6: Portfolio isolation (container per tenant); §5: Security = human-mediated; §10: Licensed boundaries (Docker not licensed) | Active | 0.85 |
| OutreachWorker | Background email/outreach processing | Celery, SMTP config, core.services, core.models | Celery worker process | Outreach Agent, Campaign Pipeline | Constitution §5: External comms = AI-drafted, human-reviewed; §12: No autonomous spending (email costs) | Active | 0.85 |

---

## Authentication & Security Tools

| Tool Name | Purpose | Dependencies | Users | Agent Consumers | Governance Concerns | Status | Confidence |
|-----------|---------|--------------|-------|-----------------|---------------------|--------|------------|
| JWTHandler | JWT access/refresh tokens with Redis revocation cache, HS256 | `PyJWT`, `redis`, `datetime`, `os`, `logging` | AuthRouter, Middleware, UserService | All API consumers, agents via API | Constitution §7: Secrets never agent-touchable (JWT_SECRET_KEY via env); §12: Monetary rules (auth for payments); §13: Agent identity (unique non-shared) | Active | 0.95 |
| AuthMiddleware | Request authentication, API key validation, permission checks | JWTHandler, `core.models.api_key.APIKey`, `core.models.user.User` | All API routers | All agents via API | Constitution §3: Legible authorship (request attribution); §5: Autonomy by domain (permission gating) | Active | 0.95 |
| Permissions System | RBAC with Permission enum (DELETE_OWN_DATA, DELETE_COMPANY, DELETE_DEPLOYMENT, DELETE_ANY_USER) | `core.models.user.User`, `frontend.src.types.rbac` | API routers, Frontend hooks | Admin agents, User-facing agents | Constitution §3: Legible authorship; §4.3: External representation; §5: Autonomy by domain | Active | 0.90 |

---

## Communication & Integration Tools

| Tool Name | Purpose | Dependencies | Users | Agent Consumers | Governance Concerns | Status | Confidence |
|-----------|---------|--------------|-------|-----------------|---------------------|--------|------------|
| WebSocket Manager | Real-time messaging with JWT auth, connection tracking | `fastapi.WebSocket`, JWTHandler, `core.models.message.Message` | WS Router | Notification Service, agents needing real-time | Constitution §3: Legible authorship (message attribution); §5: External comms = human-reviewed | Active | 0.85 |
| NotificationService | In-app + WebSocket push notifications | `core.models.notification.Notification`, `core.models.user.User`, WebSocket | TicketService, WorkflowService, TenantService, Celery tasks | All services, agents | Constitution §5: External comms = AI-drafted, human-reviewed; §12: Monetary (no spend) | Active | 0.90 |
| PaymentService | Stripe integration: subscriptions, checkout, cancellations | `stripe`, `os`, `core.models.tenant.CompanyTenant`, `core.models.user.User` | Payment Router, TenantService, Webhooks | Payment Agent, Tenant Service | Constitution §5: Financial = human approval every $; §12: Monetary transaction rules (session caps, allowlists, dual-rail, audit logging) | Active | 0.90 |
| Integrations (CRM, Email, LinkedIn, Telephony) | Stub interfaces for external integrations | None (stubs) | Future use | Future agents | Constitution §14: Third-party vendor governance (security/liability review required) | Archive Candidate | 0.60 |

---

## Development & Observability Tools

| Tool Name | Purpose | Dependencies | Users | Agent Consumers | Governance Concerns | Status | Confidence |
|-----------|---------|--------------|-------|-----------------|---------------------|--------|------------|
| pytest + ruff + mypy | Test runner, linting, type checking | `pytest`, `ruff`, `mypy` | CI/CD, developers | N/A (dev tools) | Constitution §35: Testing is evidence; §11: IP hygiene (automated scanning) | Active | 0.95 |
| GitHub Actions (tests.yml) | CI pipeline: lint, typecheck, test | GitHub Actions, pytest | CI/CD | N/A (automation) | Constitution §11: IP & licensing hygiene (automated scanning) | Active | 0.95 |
| Logging (utils/logging.py) | Structured logging with context, performance timing | `logging`, `contextvars`, `uuid`, `time` | All modules | All agents via BaseAgent | Constitution §3: Legible authorship (trace_id in logs); §12: Tamper-evident audit logging | Active | 0.95 |
| Monitoring Stubs (health_dashboard, metrics_collector, system_monitor) | Placeholders for observability | None (stubs) | None (not implemented) | Monitoring Agent (future) | Constitution §5: Monitoring = observe; SELF_HEALING_ARCHITECTURE: Detect→Diagnose→Attempt→Validate→Escalate | Archive Candidate | 0.40 |

---

## Summary Statistics

| Category | Total | Active | Archive Candidate | Critical Governance Gaps |
|----------|-------|--------|-------------------|--------------------------|
| LLM & AI | 5 | 5 | 0 | ADR-001 verification separation |
| Memory & Storage | 5 | 5 | 0 | Portfolio isolation (shared files/DB) |
| Database & Persistence | 3 | 3 | 0 | Portfolio isolation (single DB) |
| Queue & Task | 3 | 3 | 0 | Human approval gating in tasks |
| Deployment | 2 | 2 | 0 | Container per tenant enforcement |
| Auth & Security | 3 | 3 | 0 | Per-role allowlists (Phase 2) |
| Communication | 5 | 4 | 1 (integrations) | Vendor governance for integrations |
| Dev & Observability | 4 | 3 | 1 (monitoring stubs) | Monitoring implementation |

**Total Tools**: 30  
**Active**: 28  
**Archive Candidate**: 2 (integrations stubs, monitoring stubs)  

---

## Critical Governance Gaps Requiring Implementation

1. **Portfolio Isolation** (Constitution §4.6): Single SQLite DB and shared `long_term_memory.json` violate structural isolation mandate
2. **Per-Role Tool Allowlists** (Constitution §13): Agent Identity & Permissions requires explicit allowlists per agent role (Phase 2)
3. **Monitoring Implementation** (SELF_HEALING_ARCHITECTURE): Stubs in `core/monitoring/` must be implemented for Detect→Diagnose→Attempt→Validate→Escalate
4. **Vendor Governance** (Constitution §14): Integration stubs need security/liability review before activation
5. **Session Caps & Allowlists** (Constitution §12): PaymentService needs monetary rule enforcement (session caps, counterparty allowlists)