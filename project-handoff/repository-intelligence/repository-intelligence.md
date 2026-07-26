# Repository Intelligence Report

## Executive Summary

SwarmLead-AI (Genesis) is an autonomous AI swarm platform designed to transform a human's request into a fully launched company. The repository represents a sophisticated multi-agent system with constitutional governance, knowledge graph architecture, and organizational intelligence as first-class architectural concerns. The codebase comprises 485+ Python files, 100+ TypeScript/TSX frontend files, 54 ADR/governance/founder documents, and 100+ test files across unit, integration, migration, and performance categories. The system has completed migration to v3 architecture with 559 passing tests and 86% coverage. The platform operates on a "Constitution-First" governance model where all agent actions are traceable, human-gated for irreversible decisions, and structured around six risk domains with differentiated autonomy postures.

---

## Technologies Identified

### Core Languages & Frameworks
- **Python 3.10+**: Primary backend language (485+ files)
- **TypeScript/React/Next.js**: Frontend framework (100+ TSX/TS files)
- **FastAPI**: REST API framework with WebSocket support
- **SQLAlchemy 2.0**: ORM with declarative models
- **Pydantic v2**: Configuration and API schema validation
- **Celery + Redis**: Distributed task queue and workers
- **Docker/Docker Compose**: Containerized deployment
- **Pytest**: Testing framework (559 tests, 86% coverage)

### Infrastructure & Operations
- **PostgreSQL/SQLite**: Database (dual support via config)
- **S3-compatible storage**: File management (local mode supported)
- **Ollama**: Local LLM inference (qwen2.5-coder:1.5b default)
- **Stripe**: Payment processing
- **JWT + Redis**: Authentication and session management
- **Uvicorn**: ASGI server

### Development Tools
- **ruff/mypy**: Linting and type checking
- **eslint/prettier**: Frontend linting
- **GitHub Actions**: CI/CD pipeline

---

## Major Systems Identified

### 1. Agent Orchestration System (`core/orchestration/`)
- **Agent Manager**: Registration, execution, and lifecycle management
- **Task Router**: Route tasks to appropriate agents
- **Scheduler**: Cron-like and event-driven task scheduling
- **Swarm Coordinator**: Multi-agent coordination and decision engine
- **Autonomous Swarm**: Self-organizing agent collectives
- **Repository Health**: Monitoring, scanning, planning, and repair workflows

### 2. Agent Runtime (`core/agents/`)
- **BaseAgent**: Abstract base with validation, tracing, LLM integration
- **Strategy Agent**: Business strategy generation with memory integration
- **Outreach Agent**: Email/outreach content generation
- **Builder/Repair/Review Agents**: Code generation and quality

### 3. Memory System (`core/memory/`)
- **Session Memory**: In-memory ephemeral storage
- **Long-term Memory**: Persistent JSON-based storage with query
- **Vector Store**: Embedding-based semantic search

### 4. Persistence Layer (`core/persistence/`)
- **Linear Engine**: Compatibility layer for v3 models
- **Session Management**: Database URL resolution, connection pooling
- **Base Models**: SQLAlchemy declarative base

### 5. API Layer (`interfaces/api/`)
- **Routers**: auth, leads, tenants, workflows, tickets, outreach, payments, notifications, users, reporting, CRM
- **Authentication**: JWT with refresh tokens, API keys, permissions
- **WebSocket**: Real-time messaging (`ws.py`)

### 6. Workflow Engine (`core/workflows/`)
- **Campaign Pipeline**: Strategy → Outreach orchestration
- **Feedback Loop**: Learning from execution outcomes
- **Outreach Sequences**: Multi-step outreach campaigns

### 7. Services Layer (`core/services/`)
- **Tenant Service**: Provisioning, Docker deployment, lifecycle
- **Workflow Service**: CRUD, advancement, completion tracking
- **Ticket Service**: Lifecycle, comments, history, escalation, metrics
- **Notification Service**: In-app + WebSocket push
- **Payment Service**: Stripe integration, subscriptions

### 8. Infrastructure (`infrastructure/`)
- **Celery Workers**: Notification, ticket, workflow tasks
- **Deployment**: Box deployer for tenant isolation
- **Outreach Worker**: Background email processing
- **Task Queue**: Redis-based queue management

### 9. Frontend (`frontend/src/`)
- **Pages**: Dashboard, leads, workflows, tickets, billing, tenants, agents, admin
- **Components**: UI library (shadcn/ui), feature components per domain
- **Hooks**: 40+ React Query hooks for API integration
- **Types**: Comprehensive TypeScript definitions

---

## Major Directories Identified

| Directory | Purpose | File Count |
|-----------|---------|------------|
| `core/` | Core business logic (agents, memory, models, orchestration, services, workflows) | ~120 |
| `interfaces/` | API, CLI, Voice interfaces | ~20 |
| `infrastructure/` | Celery, deployment, outreach, queue | ~10 |
| `integrations/` | CRM, email, LinkedIn, telephony (stubs) | ~5 |
| `configs/` | Configuration schemas, loaders | ~5 |
| `docs/` | Governance, ADRs, founder, agents, knowledge, operations | 54 |
| `tests/` | Unit, integration, migration, performance | 107 |
| `frontend/` | Next.js React application | ~100 |
| `assets/` | Raw and optimized agent archetypes | ~70 |
| `asset_processor/` | Archetype processing pipeline | ~65 |
| `data/` | Runtime data (long_term_memory.json, swarmlead.db) | ~5 |
| `scripts/` | Utility scripts | ~1 |
| `utils/` | Logging, helpers, validation | ~4 |
| `archive/` | Migration artifacts | ~30 |

---

## Founder Assets Identified

Located in `docs/founder/` (13 documents):

1. **vision.md** - Platform vision: democratize enterprise capabilities
2. **mission.md** - Amplify human capability, remove constraints
3. **engineering_principles.md** - No placeholders, no debt by neglect, docs as product, testing as evidence, reversibility, discoverability, knowledge as infrastructure
4. **founder_intent.md** - Detailed founder vision and constraints
5. **founder_story.md** - Origin narrative
6. **philosophy.md** - (empty placeholder)
7. **product_principles.md** - Product design principles
8. **roadmap_end_state.md** - Target architecture
9. **success_definition.md** - Success metrics
10. **north_star.md** - Guiding metric
11. **customer_promises.md** - Commitments to users
12. **anti_patterns.md** - Explicit anti-patterns to avoid
13. **future_of_genesis.md** - Long-term evolution

**Hierarchy Position**: Top of Genesis Architect priority stack (above Constitution)

---

## Governance Assets Identified

Located in `docs/governance/` (7 documents):

1. **CONSTITUTION.md** (40KB) - Founding charter with:
   - Phase 1 deliverable: Swarm Constitution Project
   - Mission: Turn human request into launched company
   - 8 Core Values (legible authorship, reversibility, escalate uncertainty, minimum viable autonomy, no self-graded homework, IP hygiene, secrets never agent-touchable, open-source core)
   - Human oversight philosophy (7 subsections)
   - Autonomy by domain (6 risk domains with differentiated postures)
   - Mandatory legal/compliance review triggers

2. **AGENT_RIGHTS.md** - Agent entitlements and protections
3. **AGENT_RESPONSIBILITIES.md** - Agent duties and accountabilities
4. **DELEGATION_MATRIX.md** - Authority delegation rules
5. **ENFORCEMENT.md** - Governance enforcement mechanisms
6. **ESCALATION_FRAMEWORK.md** - Escalation paths and procedures
7. **SAFETY_CODE.md** - Safety protocols

**Hierarchy Position**: Second in priority stack (below Founder Intent, above Safety Code)

---

## ADR Assets Identified

Located in `docs/adr/` (12 ADRs):

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | No Self-Graded Homework | Accepted |
| ADR-002 | Founder Intent Preservation | Accepted |
| ADR-003 | Constitution-First Governance | Accepted |
| ADR-004 | Organizational Memory System | Accepted |
| ADR-005 | Knowledge Graph Architecture | Accepted |
| ADR-006 | Agent Organization Architecture | Accepted |
| ADR-007 | Repository Intelligence Layers | Accepted |
| ADR-008 | Documentation-Driven Development | Accepted |
| ADR-009 | Single-Machine-First Infrastructure | Accepted |
| ADR-010 | Open-Source-First Strategy | Accepted |
| ADR-011 | Human Authority Preservation | Accepted |
| ADR-012 | Continuous Improvement Framework | Accepted |

**Pattern**: Sequential, foundational architecture decisions establishing the Genesis governance and intelligence framework

---

## Knowledge Assets Identified

Located in `docs/knowledge/` (6 documents):

1. **REPOSITORY_INTELLIGENCE_SPEC.md** - Specification for the repository intelligence layer (discovery, classification, relationship mapping, change awareness, RAG support, artifact registry)
2. **KNOWLEDGE_GRAPH_SPEC.md** - Graph specification (nodes, edges, scope across code/doc/governance/agent/operational/knowledge layers)
3. **NODE_TYPES.md** - Node type definitions
4. **EDGE_TYPES.md** - Relationship type definitions
5. **KNOWLEDGE_LIFECYCLE.MD** - Knowledge creation, validation, deprecation
6. **RAG_ARCHITECTURE.md** - Retrieval-augmented generation architecture

**Purpose**: Transform isolated information into connected organizational intelligence

---

## Agent Assets Identified

### Documentation (`docs/agents/` - 7 documents):
1. **AGENT_REGISTRY.md** - 33 agent roles across 6 layers (Executive, Engineering, Quality, Knowledge, Operations, Governance)
2. **AGENT_ORGANIZATION_CHART.md** - Hierarchical structure
3. **AGENT_COMMUNICATION_PROTOCOL.md** - Inter-agent messaging
4. **AGENT_MEMORY_MODEL.md** - Memory architecture for agents
5. **AGENT_OPERATING_SYSTEM.md** - Runtime environment
6. **AGENT_LIFECYCLE.md** - Creation, deployment, retirement
7. **AGENT_SOP_FRAMEWORK.md** - Standard operating procedures

### Runtime Assets (`assets/` and `asset_processor/`):
- **64 archetype DNA files** in `asset_processor/output/archetypes/` across 8 agent types:
  - Architect (5), Builder (30), Governance Director (3), Orchestrator (10), Planner (4), Researcher (2), Reviewer (4)
- **Raw registries**: `agent_registry.json`, `archetype_registry.json`, `archetype_classification_report.json`
- **Optimized**: `optimized_archetypes.json`, `archetype_weights.json`

### Code Implementation (`core/agents/`, `core/orchestration/`):
- BaseAgent, StrategyAgent, OutreachAgent
- BuilderAgent, RepairAgent, ReviewAgent
- AgentManager, TaskRouter, SwarmCoordinator

---

## Operations Assets Identified

Located in `docs/operations/` (8 documents):

1. **VERSIONING_STANDARD.md** - Semantic versioning rules
2. **RELEASE_MANAGEMENT.md** - Release process and gates
3. **MONITORING_AND_ALERTING.md** - Observability strategy
4. **DISASTER_RECOVERY.md** - Recovery procedures
5. **BACKUP_STRATEGY.md** - Backup policies
6. **CHANGE_MANAGEMENT.md** - Change control process
7. **CONTINUOUS_IMPROVEMENT_PROGRAM.md** - Kaizen framework
8. **SELF_HEALING_ARCHITECTURE.md** - Auto-recovery targets, hierarchy (Detect→Diagnose→Attempt→Validate→Escalate), mandatory escalation rules

---

## Prompt Assets Identified

### Raw Prompt DNA (64 files in `asset_processor/output/archetypes/`):
- Organized by agent archetype (Architect, Builder, Governance Director, Orchestrator, Planner, Researcher, Reviewer)
- Each contains structured prompt components: identity, mission, reasoning framework, capabilities, constraints, collaboration, governance

### Prompt Processing Pipeline (`core/prompts/`):
- **asset_loader.py**: Load archetype assets
- **asset_optimizer.py**: Process raw → optimized (scoring, classification, extraction)
- **archetype_selector.py**: Select appropriate archetype per agent
- **adaptive_weights.py**: Dynamic weight adjustment based on performance

### Documentation Prompts:
- `docs/agents/AGENT_SOP_FRAMEWORK.md` - SOP templates
- `frontend/AGENTS.md` - Frontend agent guidance
- Various ADRs contain prompt-relevant architectural decisions

---

## SOP Assets Identified

1. **AGENT_SOP_FRAMEWORK.md** - Framework for creating agent SOPs
2. **SELF_HEALING_ARCHITECTURE.md** - Operational recovery SOPs
3. **RELEASE_MANAGEMENT.md** - Deployment SOPs
4. **CHANGE_MANAGEMENT.md** - Change control SOPs
5. **DISASTER_RECOVERY.md** - Incident response SOPs
6. **BACKUP_STRATEGY.md** - Backup/restore SOPs
7. **MONITORING_AND_ALERTING.md** - Observability SOPs
8. **CONTINUOUS_IMPROVEMENT_PROGRAM.md** - Improvement cycle SOPs
9. **Agent-specific SOPs** embedded in archetype DNA files (asset_processor/output/)
10. **Constitution** Sections 4-5 define governance SOPs (human oversight, autonomy by domain)

---

## Tool Assets Identified

### Development Tools:
- **pytest**: Test runner (unit, integration, migration, performance)
- **ruff**: Python linting
- **mypy**: Type checking
- **eslint/prettier**: Frontend linting/formatting
- **GitHub Actions**: CI pipeline (`.github/workflows/tests.yml`)

### Runtime Tools:
- **OllamaClient** (`core/models/local_llm/ollama_client.py`): Local LLM with fallback
- **S3Client** (`core/storage/s3_client.py`): Object storage (local/S3)
- **FileManager** (`core/storage/file_manager.py`): Company archive management
- **Celery App** (`infrastructure/celery/celery_app.py`): Distributed task queue
- **TaskQueue** (`infrastructure/queue/task_queue.py`): Redis queue abstraction
- **BoxDeployer** (`infrastructure/deployment/box_deployer.py`): Tenant container deployment

### Agent Tools (via BaseAgent):
- LLM calling with tracing
- Memory integration (session, long-term, vector)
- Input validation
- Execution tracing

---

## Documentation Assets Identified

### Hierarchical Documentation Structure:

**Tier 1 - Founder Intent** (13 files in `docs/founder/`)
**Tier 2 - Governance** (7 files in `docs/governance/`)
**Tier 3 - ADRs** (12 files in `docs/adr/`)
**Tier 4 - Knowledge Systems** (6 files in `docs/knowledge/`)
**Tier 5 - Agent Systems** (7 files in `docs/agents/`)
**Tier 6 - Operations** (8 files in `docs/operations/`)
**Tier 7 - Technical** (README.md, frontend/README.md, CLAUDE.md, AGENTS.md)

### Key Documentation Principles (from engineering_principles.md):
- "Documentation Is Part Of The Product"
- "A feature that only exists in code does not fully exist"
- "Every significant capability must be documented"

---

## Database Assets Identified

### SQLAlchemy Models (`core/models/` - 16 models):
1. **User** - Authentication, roles, subscriptions
2. **APIKey** - Scoped API access
3. **Lead** - Lead management with enrichment fields
4. **Message/MessageThread** - Messaging system
5. **Notification** - In-app notifications
6. **CompanyTenant** - Multi-tenant isolation
7. **Deployment** - Tenant deployment tracking
8. **Ticket/TicketComment/TicketHistory** - Ticketing system
9. **Workflow/WorkflowStep** - Workflow orchestration
10. **Sequence/SequenceEnrollment/SequenceStep/SequenceMetrics/SequenceEvent/SequenceMailbox** - Outreach sequences
11. **UsageEvent** - Usage tracking/billing
12. **Models for local LLM** (embeddings, voice - stubs)

### Data Files:
- `data/swarmlead.db` - SQLite database (274KB)
- `data/long_term_memory.json` - Agent memory (54KB)
- `data/analytics/`, `data/campaigns/`, `data/leads/` - Data directories

### Persistence Layer:
- `core/persistence/session.py` - DB URL resolution, session factory
- `core/persistence/linear_engine.py` - Compatibility engine
- `core/persistence/base.py` - Declarative base
- Migration from v2 to v3 complete (validated by migration tests)

---

## API Assets Identified

### REST Endpoints (`interfaces/api/routers/`):
| Router | Endpoints | Purpose |
|--------|-----------|---------|
| auth.py | /register, /login, /refresh, /me, /password-reset | Authentication |
| leads.py | CRUD leads | Lead management |
| tenants.py | Register, provision, status | Tenant lifecycle |
| workflows.py | CRUD, advance, complete, status | Workflow engine |
| tickets.py | CRUD, comments, history, escalate, metrics | Ticketing |
| outreach.py | Campaigns, sequences | Outreach automation |
| payments.py | Checkout, subscriptions | Stripe billing |
| notifications.py | List, mark read | Notifications |
| users.py | Profile, admin user management | User management |
| reporting.py | Analytics | Reporting |
| crm.py | CRM integration | External CRM |
| usage.py | Usage recording | Metering |

### WebSocket:
- `ws.py` - Real-time messaging with JWT auth

### Authentication:
- JWT access/refresh tokens
- API key authentication
- Role-based permissions (RBAC in `frontend/src/types/rbac.ts`)

### API Schema:
- Pydantic request/response models per router
- OpenAPI/Swagger at `/docs`

---

## Testing Assets Identified

### Test Inventory (107 test files):

**Unit Tests** (54 files in `tests/unit/`):
- Agent tests: base_agent, strategy_agent, outreach_agent, builder_agent, repair_agent, review_agent, agent_manager
- Orchestration: scheduler, task_router, swarm_coordinator, swarm_decision_engine, swarm_evaluator, autonomous_swarm
- Memory: session_memory, long_term_memory, vector_store
- Prompts: adaptive_weights, archetype_selector, asset_loader, asset_optimizer
- Workflows: campaign_pipeline, feedback_loop, outreach_sequences
- Core: config, event_tracker, metrics_engine, dependency_graph
- Repository intelligence: scanner, planner, state, health_monitor, health_service
- Models: ollama_client, schema_archetypes

**Integration Tests** (23 files in `tests/integration/`):
- API health, leads, tenants, tickets, workflows, payments, notifications, usage
- Database bootstrap, CRUD, persistence
- Agent pipeline, end-to-end flow
- Tenant provisioning, env configuration

**Migration Tests** (10 files in `tests/migration/`):
- API schema, AST validity, database models
- Generated models, routers, services
- Migration state, no backend imports, router registration, service construction

**Performance Tests** (1 file in `tests/performance/`):
- Execution speed benchmarks

**Fixtures** (3 files in `tests/fixtures/`):
- Agent fixtures, data fixtures

**CI/CD**: `.github/workflows/tests.yml` runs full test suite

**Status**: 559 passing, 86% coverage (per README.md)

---

## Environment Assets Identified

### Environment Variables (from `environment_references.csv` - 39 references):

**Core Application**:
- `ENV` - Environment mode
- `SWARM_DB_URL` / `DATABASE_URL` - Database connection
- `JWT_SECRET_KEY` - JWT signing
- `REDIS_URL` - Redis connection
- `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` - Celery
- `TEST_MODE` - Test flag

**External Services**:
- `STRIPE_API_KEY`, `STRIPE_HOSTING_PRICE_ID` - Payments
- `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET_NAME`, `STORAGE_MODE`, `LOCAL_STORAGE_DIR` - Storage
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM` - Email
- `TECH_DOMAIN` - Tenant subdomain base (default: realms2riches.tech)
- `DEPLOY_DOCKER_IMAGE` - Tenant container image (default: nginx:alpine)

**Frontend**:
- `process.env` references in `frontend/src/lib/api.ts`

### Configuration Files:
- `.env`, `.env.bak`, `.env.docker` - Environment files
- `configs/system_settings.yaml`, `agent_configs.yaml`, `campaign_templates.yaml` - YAML configs (empty placeholders)
- `configs/schema.py` - Pydantic config schema
- `pyproject.toml` - Project metadata
- `requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies

---

## Architectural Observations

### 1. **Constitution-First Architecture**
The entire system is governed by a written Constitution (40KB) that establishes human oversight, autonomy boundaries, and safety constraints before any code executes. ADR-003 enshrines this as "Constitution-First Governance."

### 2. **Agent-Native Design**
Agents are not bolted on—they are the primary architectural primitive. The Agent Registry defines 33 roles across 6 layers. Every agent has identity, purpose, responsibilities, permissions, escalation path, and accountability chain.

### 3. **Knowledge as Infrastructure**
Per engineering_principles.md: "Knowledge Is Infrastructure." The system invests heavily in:
- Repository Intelligence Layer (ADR-007)
- Knowledge Graph (ADR-005, KNOWLEDGE_GRAPH_SPEC.md)
- Organizational Memory System (ADR-004)
- RAG Architecture (RAG_ARCHITECTURE.md)

### 4. **Multi-Layer Memory Architecture**
Three-tier memory: Session (ephemeral) → Long-term (JSON) → Vector (semantic). Agents integrate all three via BaseAgent.

### 5. **Single-Machine-First with Scale Path** (ADR-009)
Designed to run on one machine (SQLite, local Ollama, local S3) but with PostgreSQL, Redis, S3, and distributed Celery as configurable upgrades.

### 6. **Migration-Complete v3 Architecture**
Clean separation: `core/models/` (pure SQLAlchemy), `core/persistence/` (engine/session), `interfaces/api/` (FastAPI), `core/services/` (business logic), `core/orchestration/` (agent coordination). Validated by 10 migration tests.

### 7. **Open-Source-First Strategy** (ADR-010)
Core swarm logic remains open and auditable. Closed third-party APIs (Stripe, banking) are acceptable dependencies.

### 8. **No Self-Graded Homework** (ADR-001, Constitution Value #5)
Verification structurally separate from generation. QA, Security, Performance agents are distinct from Builder agents.

### 9. **Secrets Never Agent-Touchable** (Constitution Value #7)
Secret access mediated by non-AI systems (config_loader, environment variables, S3Client abstraction).

### 10. **Frontend-Backend Parity**
Frontend hooks (40+) directly mirror API routers. TypeScript types (`frontend/src/types/`) reflect Pydantic models. RBAC enforced on both sides.

---

## Risks

### 1. **Governance Complexity**
12 ADRs, 7 governance docs, 13 founder docs, Constitution (40KB) create high cognitive load. Risk of governance theater vs. actual enforcement.

### 2. **Agent Archetype Proliferation**
64 archetype DNA files across 8 types with asset_processor pipeline. Risk of prompt drift, inconsistent optimization, unclear ownership.

### 3. **Memory System Scaling**
JSON-based long_term_memory.py and vector_store.py are file-based. No clear sharding, compaction, or distributed strategy for multi-tenant scale.

### 4. **Tenant Isolation Enforcement**
Constitution §4.6 mandates "hard architectural boundary" for portfolio isolation. Current implementation uses subdomain + container_id but database is shared (single swarmlead.db). Risk of data leakage.

### 5. **Local LLM Dependency**
Ollama with qwen2.5-coder:1.5b as default. No cloud LLM fallback configured in production path. Model availability, versioning, and performance at scale unproven.

### 6. **Empty Configuration Placeholders**
`configs/agent_configs.yaml`, `campaign_templates.yaml`, `system_settings.yaml` are 0-byte files. Runtime depends on environment variables with defaults in code.

### 7. **Frontend Marked "Planned"**
README.md shows "Frontend: 🚧 Planned" but 100+ TSX files exist. Discrepancy between status and reality.

### 8. **Migration Artifacts in Archive**
30+ files in `archive/migration_artifacts/` including SQL dumps, migration scripts, reports. Risk of confusion with active code.

### 9. **No Observability Implementation**
Monitoring files exist (`core/monitoring/*.py`) but are 0-byte stubs. SELF_HEALING_ARCHITECTURE.md references monitoring but no implementation.

### 10. **Testing Gaps in Agent Behavior**
Unit tests cover agent mechanics but limited integration testing of multi-agent workflows, swarm decision-making, or constitutional compliance.

### 11. **Hardcoded Defaults**
Multiple `os.getenv(key, default)` patterns with production values as defaults (e.g., `TECH_DOMAIN` = realms2riches.tech, `S3_BUCKET_NAME` = swarm-companies).

### 12. **Single Database File**
`data/swarmlead.db` serves all tenants. Constitution §4.6 requires structural isolation, not just logical.

---

## Questions Requiring Further Investigation

1. **Tenant Data Isolation**: How is Constitution §4.6 (portfolio isolation) enforced at the database level? Is there per-tenant database sharding planned?

2. **Agent Archetype Governance**: Who approves new archetypes? How are the 64 DNA files versioned, tested, and validated against Constitution?

3. **Memory Compaction**: What is the strategy for long_term_memory.json growth? No TTL, compaction, or archival visible.

4. **Production Deployment**: Docker Compose exists but no Kubernetes, Helm, or cloud deployment manifests. How does "Single-Machine-First" transition to production scale?

5. **LLM Cost Model**: Local Ollama is free but limited. What is the cloud LLM fallback strategy and cost governance?

6. **Constitutional Compliance Testing**: Are there automated tests that verify agent actions comply with Constitution (e.g., no autonomous spending, human-gated legal actions)?

7. **Secret Rotation**: How are JWT secrets, Stripe keys, S3 credentials rotated? No rotation mechanism visible.

8. **Audit Trail Completeness**: Constitution requires "legible authorship." Does current logging (swarm.log 3.4MB, error.log 647KB) capture all agent decisions with traceability?

9. **Frontend Authentication Flow**: Frontend uses localStorage for tokens. How does this work with httpOnly cookies, refresh token rotation, and CSRF protection?

10. **Multi-Region/HA**: No evidence of high availability, multi-region, or disaster recovery implementation despite DISASTER_RECOVERY.md.

11. **Agent Registry Runtime**: AGENT_REGISTRY.md defines 33 roles. How many are actually instantiated? What is the activation mechanism?

12. **Knowledge Graph Population**: KNOWLEDGE_GRAPH_SPEC.md is ambitious. What is the current graph population status? Is it auto-generated from code or manual?

13. **Migration State**: `migration_state.json` exists. Is migration fully complete or are there pending items?

14. **WebSocket Scaling**: `ws.py` uses in-memory connection tracking. How does this work with multiple Celery workers / horizontal scaling?

15. **Rate Limiting**: No visible rate limiting on API endpoints. How is abuse prevented?

16. **Data Retention**: No visible data retention policies for leads, messages, workflows, audit logs.

17. **Agent-to-Agent Authentication**: How do agents authenticate to each other? Shared secrets? mTLS? JWT?

18. **Constitutional Amendment Process**: How are ADRs/Constitution amended? No visible process beyond "Human decision — see Decision Log #N".

19. **Integration Stub Completeness**: `integrations/crm/`, `email/`, `linkedin/`, `telephony/` contain only `__init__.py`. What is the integration roadmap?

20. **License Compliance**: README.md says "Proprietary" but ADR-010 says "Open-Source-First Strategy" and Constitution Value #8 says "Open-source core, always." Which governs?