# Tool to Agent Mapping

**Generated**: 2026-07-26  
**Sources**: `tool-registry.md`, `agent-registry.md`, `core/`, `infrastructure/`, `interfaces/`

---

## Mapping Methodology

Each tool mapped to:
- **Agent Consumers**: Which agents use this tool
- **Purpose**: What the tool provides
- **Dependencies**: Other tools/services required
- **Risk Level**: Governance/operational risk (Critical/High/Medium/Low)

---

## LLM & AI Tools

### OllamaClient
| Field | Value |
|-------|-------|
| **Agent Consumers** | StrategyAgent, OutreachAgent, BuilderAgent, RepairAgent, ReviewAgent (all via BaseAgent) |
| **Purpose** | Local LLM inference with retry, fallback, concurrency control |
| **Dependencies** | httpx, ConfigLoader, logging, Ollama server (port 11434) |
| **Risk Level** | **High** - LLM costs, model availability, fallback behavior affects all agents |
| **Governance** | Constitution §5 (Financial=human approval), §7 (Secrets), ADR-009 (Single-machine-first) |

### ArchetypeSelector
| Field | Value |
|-------|-------|
| **Agent Consumers** | All agents at startup |
| **Purpose** | Selects appropriate archetype per agent with adaptive weights |
| **Dependencies** | AssetLoader, AdaptiveWeights, optimized_archetypes.json |
| **Risk Level** | **Medium** - Wrong archetype = wrong capabilities |
| **Governance** | Constitution §3 (No self-graded homework), ADR-008 |

### AssetLoader
| Field | Value |
|-------|-------|
| **Agent Consumers** | ArchetypeSelector, all agents |
| **Purpose** | Loads archetype assets from optimized storage |
| **Dependencies** | optimized_archetypes.json, archetype_weights.json |
| **Risk Level** | **Low** - Read-only prompt loading |
| **Governance** | Constitution §7 (Secrets never agent-touchable) |

### AssetOptimizer
| Field | Value |
|-------|-------|
| **Agent Consumers** | None (build-time only) |
| **Purpose** | Raw DNA → optimized archetypes (scoring, classification) |
| **Dependencies** | archetype_classification_report.json, archetype_registry.json, archetype_weights.json |
| **Risk Level** | **Medium** - Build pipeline integrity |
| **Governance** | ADR-001 (No self-graded homework), ADR-007 |

### AdaptiveWeights
| Field | Value |
|-------|-------|
| **Agent Consumers** | ArchetypeSelector (continuous) |
| **Purpose** | Dynamic weight adjustment from performance feedback |
| **Dependencies** | archetype_weights.json, performance metrics |
| **Risk Level** | **Low** - Continuous improvement |
| **Governance** | Constitution §12 (Continuous Improvement), ADR-012 |

---

## Memory & Storage Tools

### SessionMemory
| Field | Value |
|-------|-------|
| **Agent Consumers** | All agents via BaseAgent.session_memory |
| **Purpose** | Ephemeral in-memory key-value per execution |
| **Dependencies** | None (pure Python dict) |
| **Risk Level** | **Low** - Ephemeral, per-execution |
| **Governance** | Constitution §4 (Organizational Memory), §4.6 (Portfolio isolation - **GAP**) |

### LongTermMemory
| Field | Value |
|-------|-------|
| **Agent Consumers** | StrategyAgent, OutreachAgent, CampaignPipeline, FeedbackLoop, all via BaseAgent |
| **Purpose** | Persistent JSON file storage with metadata enrichment |
| **Dependencies** | data/long_term_memory.json, json, datetime |
| **Risk Level** | **High** - **Shared file violates §4.6 portfolio isolation** |
| **Governance** | Constitution §4.6 (CRITICAL GAP), §4, ADR-004 |

### VectorStore
| Field | Value |
|-------|-------|
| **Agent Consumers** | All agents via BaseAgent.vector_store, FeedbackLoop |
| **Purpose** | Lightweight semantic search (keyword overlap v1) |
| **Dependencies** | Python list/set operations |
| **Risk Level** | **Medium** - Shared store violates §4.6; v1 is keyword-only |
| **Governance** | Constitution §4, ADR-005 (Knowledge Graph) |

### S3Client
| Field | Value |
|-------|-------|
| **Agent Consumers** | FileManager, TenantService, BackupAgent (future) |
| **Purpose** | S3-compatible object storage with local FOSS fallback |
| **Dependencies** | boto3 (optional), pathlib, os, logging |
| **Risk Level** | **Medium** - Credentials via env; vendor lock-in risk |
| **Governance** | Constitution §7 (Secrets via env), §14 (Vendor governance), §9 (Open-source core) |

### FileManager
| Field | Value |
|-------|-------|
| **Agent Consumers** | TenantService, BackupAgent (future) |
| **Purpose** | Company archive management (upload, download, metadata, cleanup) |
| **Dependencies** | S3Client, logging |
| **Risk Level** | **Medium** - Tenant data isolation depends on prefix strategy |
| **Governance** | Constitution §4.6 (Portfolio isolation - uses prefixes) |

---

## Database & Persistence Tools

### Database Session (SessionLocal, get_db)
| Field | Value |
|-------|-------|
| **Agent Consumers** | All services, API routers, Celery tasks (via DI) |
| **Purpose** | SQLAlchemy session factory with SQLite/PostgreSQL dual support |
| **Dependencies** | sqlalchemy, core.persistence.base.Base |
| **Risk Level** | **Critical** - **Single DB violates §4.6 portfolio isolation** |
| **Governance** | Constitution §4.6 (CRITICAL GAP), §7 (DB URL via env) |

### LinearEngine
| Field | Value |
|-------|-------|
| **Agent Consumers** | TicketService, LeadService (legacy compatibility) |
| **Purpose** | v2→v3 migration compatibility layer |
| **Dependencies** | core.models.*, sqlalchemy |
| **Risk Level** | **Low** - Migration bridge, deprecated over time |
| **Governance** | ADR-004 (Organizational Memory) |

### TicketHistory Persistence
| Field | Value |
|-------|-------|
| **Agent Consumers** | TicketService |
| **Purpose** | Immutable audit trail for tickets |
| **Dependencies** | core.models.ticket_history.TicketHistory, sqlalchemy |
| **Risk Level** | **Low** - Append-only audit |
| **Governance** | Constitution §3 (Legible authorship), §12 (Tamper-evident logging) |

---

## Queue & Task Tools

### CeleryApp
| Field | Value |
|-------|-------|
| **Agent Consumers** | OutreachWorker, NotificationTasks, TicketTasks, WorkflowTasks |
| **Purpose** | Distributed task queue with 6 queues, beat scheduler, DLQ |
| **Dependencies** | celery, redis, kombu, infrastructure.celery.*_tasks |
| **Risk Level** | **High** - Background processing, retries, DLQ, monetary tasks |
| **Governance** | Constitution §5 (Domain autonomy), §12 (Monetary rules), §13 (Agent identity) |

### TaskQueue
| Field | Value |
|-------|-------|
| **Agent Consumers** | OutreachWorker, simple async tasks |
| **Purpose** | Lightweight Redis queue with in-process fallback |
| **Dependencies** | redis (optional), queue.Queue (fallback) |
| **Risk Level** | **Medium** - Fallback loses persistence |
| **Governance** | Constitution §5, §7 |

### Celery Workers (Notification, Ticket, Workflow)
| Field | Value |
|-------|-------|
| **Agent Consumers** | Respective domain services |
| **Purpose** | Background task processors for specific domains |
| **Dependencies** | CeleryApp, respective services |
| **Risk Level** | **High** - Execute monetary/legal/communication tasks |
| **Governance** | Constitution §5 (Financial=human approval), §12 (Session caps), §12.3 (Allowlists) |

---

## Deployment & Infrastructure Tools

### BoxDeployer
| Field | Value |
|-------|-------|
| **Agent Consumers** | TenantService, Deployment agents (future) |
| **Purpose** | Docker-based tenant isolation (container provisioning, Hyper-V fallback) |
| **Dependencies** | docker, subprocess, powershell (Windows), os, pathlib, re, uuid |
| **Risk Level** | **High** - Container lifecycle, network isolation, Hyper-V on Windows |
| **Governance** | Constitution §4.6 (Container per tenant = isolation), §5 (Security=human-mediated), §10 (Docker not licensed) |

### OutreachWorker
| Field | Value |
|-------|-------|
| **Agent Consumers** | Celery worker process |
| **Purpose** | Background email/outreach processing |
| **Dependencies** | Celery, SMTP config, core.services, core.models |
| **Risk Level** | **High** - External communication, email costs, reputation |
| **Governance** | Constitution §5 (External comms=AI-drafted, human-reviewed), §12 (No autonomous spending) |

---

## Authentication & Security Tools

### JWTHandler
| Field | Value |
|-------|-------|
| **Agent Consumers** | AuthRouter, Middleware, UserService, WebSocketManager |
| **Purpose** | JWT access/refresh tokens with Redis revocation cache |
| **Dependencies** | PyJWT, redis, datetime, os, logging |
| **Risk Level** | **Critical** - Authentication backbone, secret management |
| **Governance** | Constitution §7 (JWT_SECRET_KEY via env), §12 (Monetary auth), §13 (Agent identity) |

### AuthMiddleware
| Field | Value |
|-------|-------|
| **Agent Consumers** | All API routers |
| **Purpose** | Request authentication, API key validation, permission checks |
| **Dependencies** | JWTHandler, APIKey model, User model |
| **Risk Level** | **Critical** - Gatekeeper for all API access |
| **Governance** | Constitution §3 (Legible authorship), §5 (Domain permissions), §13 (Least privilege) |

### Permissions System (RBAC)
| Field | Value |
|-------|-------|
| **Agent Consumers** | API routers, Frontend hooks, Admin agents |
| **Purpose** | Fine-grained permissions (DELETE_OWN_DATA, DELETE_COMPANY, DELETE_DEPLOYMENT, DELETE_ANY_USER) |
| **Dependencies** | User model, frontend types/rbac.ts |
| **Risk Level** | **High** - Authorization decisions |
| **Governance** | Constitution §3, §4.3, §5, §13 (Explicit allowlists - **Phase 2 GAP**) |

### UserService
| Field | Value |
|-------|-------|
| **Agent Consumers** | AuthRouter, AdminRouter |
| **Purpose** | User CRUD, password hashing, Pydantic models for API |
| **Dependencies** | passlib, pydantic, User model |
| **Risk Level** | **High** - Credential management |
| **Governance** | Constitution §4.1 (Legal officer), §7 (Secrets), §12 |

---

## Communication & Integration Tools

### WebSocketManager
| Field | Value |
|-------|-------|
| **Agent Consumers** | WS Router, NotificationService, agents needing real-time |
| **Purpose** | Real-time messaging with JWT auth, connection tracking |
| **Dependencies** | fastapi.WebSocket, JWTHandler, redis, Message model |
| **Risk Level** | **Medium** - Connection state, scaling limits |
| **Governance** | Constitution §3 (Message attribution), §5 (External comms=human-reviewed) |

### EventBus
| Field | Value |
|-------|-------|
| **Agent Consumers** | Orchestration, Services, all agents (internal events) |
| **Purpose** | In-process pub/sub for agent coordination and audit logging |
| **Dependencies** | asyncio, logging |
| **Risk Level** | **Low** - Internal coordination |
| **Governance** | Constitution §3 (Legible authorship - events = audit trail) |

### EmailWorker (Celery Task)
| Field | Value |
|-------|-------|
| **Agent Consumers** | NotificationService, Celery |
| **Purpose** | Background email delivery via SMTP |
| **Dependencies** | smtplib, email, Celery, env config |
| **Risk Level** | **High** - External communication, deliverability, costs |
| **Governance** | Constitution §5 (AI-drafted, human-reviewed), §7 (SMTP secrets via env) |

### StripeClient (PaymentService)
| Field | Value |
|-------|-------|
| **Agent Consumers** | PaymentService, PaymentRouter, TenantService, Webhooks |
| **Purpose** | Payment processing: subscriptions, checkout, cancellations |
| **Dependencies** | stripe, os, core.models.tenant, core.models.user |
| **Risk Level** | **Critical** - Real money movement |
| **Governance** | Constitution §5 (Financial=human approval EVERY $), §12 (Session caps, allowlists, dual-rail, audit logging - **GAPS**) |

---

## Monitoring & Observability Tools

### Monitoring Stubs (HealthDashboard, MetricsCollector, SystemMonitor)
| Field | Value |
|-------|-------|
| **Agent Consumers** | MonitoringAgent (future) |
| **Purpose** | Placeholders for observability |
| **Dependencies** | None (0-byte stubs) |
| **Risk Level** | **Critical** - **No monitoring implemented** |
| **Governance** | Constitution §5 (Monitoring), SELF_HEALING_ARCHITECTURE (Detect→Diagnose→Attempt→Validate→Escalate - **NO DATA SOURCE**) |

### Logger (utils/logging.py)
| Field | Value |
|-------|-------|
| **Agent Consumers** | All modules, all agents via BaseAgent |
| **Purpose** | Structured logging with context, performance timing, trace_id |
| **Dependencies** | logging, contextvars, uuid, time |
| **Risk Level** | **Low** - Observability backbone |
| **Governance** | Constitution §3 (Legible authorship), §12 (Tamper-evident audit logging) |

---

## Development Tools

### pytest + ruff + mypy
| Field | Value |
|-------|-------|
| **Agent Consumers** | CI/CD, developers |
| **Purpose** | Test runner, linting, type checking |
| **Dependencies** | pytest, ruff, mypy |
| **Risk Level** | **Low** - Dev tools |
| **Governance** | Constitution §35 (Testing=evidence), §11 (IP hygiene) |

### GitHub Actions (tests.yml)
| Field | Value |
|-------|-------|
| **Agent Consumers** | CI/CD pipeline |
| **Purpose** | Lint, typecheck, test automation |
| **Dependencies** | GitHub Actions, pytest |
| **Risk Level** | **Low** - Automation |
| **Governance** | Constitution §11 (Automated scanning) |

---

## Frontend Tools

### APIClient (axios wrapper)
| Field | Value |
|-------|-------|
| **Agent Consumers** | All frontend hooks (40+) |
| **Purpose** | HTTP client with JWT auth, refresh, interceptors |
| **Dependencies** | axios, auth.ts |
| **Risk Level** | **High** - Token storage in localStorage (**SECURITY RISK**) |
| **Governance** | Constitution §7 (Secrets never agent-touchable - localStorage accessible), §13 |

### AuthUtils
| Field | Value |
|-------|-------|
| **Agent Consumers** | APIClient, hooks |
| **Purpose** | Token management (access/refresh in localStorage) |
| **Dependencies** | localStorage, APIClient |
| **Risk Level** | **Critical** - localStorage tokens accessible to any JS |
| **Governance** | Constitution §7 (Critical violation), §13 |

### Permissions (Frontend RBAC)
| Field | Value |
|-------|-------|
| **Agent Consumers** | Components, hooks |
| **Purpose** | Client-side permission checking (UX gating) |
| **Dependencies** | Permission enum, roles |
| **Risk Level** | **Medium** - UX only, not security |
| **Governance** | Constitution §5 (Frontend gates ≠ security) |

### QueryProvider (React Query)
| Field | Value |
|-------|-------|
| **Agent Consumers** | All hooks |
| **Purpose** | Server state management, caching, retry |
| **Dependencies** | @tanstack/react-query |
| **Risk Level** | **Low** - Client state |
| **Governance** | Constitution §5 |

### ThemeProvider
| Field | Value |
|-------|-------|
| **Agent Consumers** | UI components |
| **Purpose** | Theme context (light/dark) |
| **Dependencies** | next-themes |
| **Risk Level** | **None** |
| **Governance** | N/A |

---

## Summary Statistics

| Risk Level | Tool Count | Tools |
|------------|------------|-------|
| **Critical** | 4 | JWTHandler, AuthMiddleware, APIClient, AuthUtils |
| **High** | 9 | OllamaClient, LongTermMemory, Database Session, CeleryApp, Celery Workers, OutreachWorker, EmailWorker, StripeClient, Permissions |
| **Medium** | 12 | ArchetypeSelector, VectorStore, S3Client, FileManager, TaskQueue, BoxDeployer, WebSocketManager, PaymentService, UserService, Monitoring Stubs, AuthMiddleware (permission checks), Frontend Permissions |
| **Low** | 8 | AssetLoader, AdaptiveWeights, SessionMemory, LinearEngine, TicketHistory, EventBus, Logger, Dev Tools, QueryProvider, ThemeProvider |

---

## Critical Governance Gaps by Tool

| Tool | Constitutional Requirement | Gap |
|------|---------------------------|-----|
| LongTermMemory | §4.6 Portfolio isolation | Single shared JSON file |
| VectorStore | §4.6 Portfolio isolation | Shared in-memory store |
| Database Session | §4.6 Portfolio isolation | Single SQLite/PostgreSQL |
| JWTHandler | §13 Agent identity | No per-agent scoped credentials |
| AuthMiddleware | §13 Explicit allowlists | Phase 2 - not implemented |
| Permissions System | §13 Per-role allowlists | Phase 2 - not implemented |
| StripeClient | §12 Session caps, allowlists, dual-rail | Not implemented |
| APIClient/AuthUtils | §7 Secrets never agent-touchable | localStorage tokens |
| Monitoring Stubs | §5 Monitoring, Self-Healing | 0-byte stubs |
| Celery Workers | §13 Agent identity | No task-level agent attribution |

---

## Tool Consolidation Opportunities

| Consolidation | Tools | Benefit |
|---------------|-------|---------|
| Memory Layer | SessionMemory + LongTermMemory + VectorStore | Unified interface, tenant scoping |
| Auth Stack | JWTHandler + AuthMiddleware + Permissions + UserService | Single auth service with scoped credentials |
| Queue Layer | CeleryApp + TaskQueue | Unified task interface |
| Payment Stack | StripeClient + PaymentService | Monetary rules enforcement |
| Frontend Auth | APIClient + AuthUtils | httpOnly cookies, CSRF protection |