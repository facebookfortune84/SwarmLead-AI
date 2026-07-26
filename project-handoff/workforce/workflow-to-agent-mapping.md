# Workflow to Agent Mapping

**Generated**: 2026-07-26  
**Sources**: `core/workflows/`, `core/orchestration/`, `core/services/`, `infrastructure/celery/`, `interfaces/api/routers/`, `docs/agents/AGENT_REGISTRY.md`, `docs/operations/`

---

## Mapping Principle

Each workflow maps to:
- **Responsible Agent**: Primary owner/executor
- **Supporting Agents**: Collaborators in execution
- **Governance Touchpoints**: Constitutional/operational gates

---

## Core Workflows (`core/workflows/`)

### Campaign Pipeline (`campaign_pipeline.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `campaign_pipeline` |
| **Responsible Agent** | StrategyAgent → OutreachAgent (sequential pipeline) |
| **Supporting Agents** | BaseAgent (execution framework), AgentManager (orchestration) |
| **Steps** | 1. Strategy Generation (StrategyAgent) → 2. Outreach Generation (OutreachAgent) |
| **Inputs** | `product`, `audience`, `goal`, `context` |
| **Outputs** | `strategy_data` (angles, hooks, summary), `outreach_data` |
| **Governance Gates** | Constitution §5 (Product/code = autonomous reversible), §5 (External comms = AI-drafted, human-reviewed) |
| **Runtime Status** | ✅ Active |
| **Error Handling** | Trace_id logging, graceful failure return |

---

### Feedback Loop (`feedback_loop.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `feedback_loop` |
| **Responsible Agent** | StrategyAgent, OutreachAgent (both learn) |
| **Supporting Agents** | BaseAgent (memory integration), VectorStore (retrieval) |
| **Purpose** | Learn from execution outcomes, adjust adaptive weights |
| **Inputs** | Execution results, performance feedback |
| **Outputs** | Updated weights (AdaptiveWeights), learnings (LongTermMemory) |
| **Governance Gates** | Constitution §12 (Continuous Improvement), ADR-012 |
| **Runtime Status** | ✅ Active |
| **Key Methods** | `add_feedback()`, `get_weights()`, `get_learnings()` |

---

### Outreach Sequences (`outreach_sequences.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `outreach_sequences` |
| **Responsible Agent** | OutreachAgent |
| **Supporting Agents** | BaseAgent, Celery Workers (email delivery via OutreachWorker) |
| **Purpose** | Multi-step outreach campaign orchestration |
| **Inputs** | Sequence definition, lead list, timing |
| **Outputs** | Sent emails, engagement tracking |
| **Governance Gates** | Constitution §5 (External comms = AI-drafted, human-reviewed), §12 (No autonomous spend) |
| **Runtime Status** | ✅ Active |
| **Key Components** | Sequence steps, enrollment tracking, metrics |

---

## Orchestration Workflows (`core/orchestration/`)

### Agent Execution Workflow (`agent_manager.py`, `task_router.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `agent_execution` |
| **Responsible Agent** | AgentManager (registry), TaskRouter (routing) |
| **Supporting Agents** | All registered BaseAgent subclasses |
| **Flow** | Register Agent → Route Task → Execute → Return Result |
| **Governance Gates** | Constitution §13 (Agent identity), ADR-001 (Verification separate), §5 (Domain autonomy) |
| **Runtime Status** | ✅ Active |
| **Key Methods** | `register_agent()`, `execute_agent()`, `route()`, `get_agent()` |

---

### Scheduler Workflow (`scheduler.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `scheduled_tasks` |
| **Responsible Agent** | Scheduler |
| **Supporting Agents** | TaskRouter, AgentManager |
| **Flow** | Schedule Config → Trigger → Route → Execute |
| **Governance Gates** | Constitutional audit logging, §5 (Domain autonomy) |
| **Runtime Status** | ✅ Active |
| **Key Methods** | `schedule()`, `run_scheduled()`, `cancel()` |

---

### Swarm Coordination Workflow
| Field | Value |
|-------|-------|
| **Workflow ID** | `swarm_coordination` |
| **Responsible Agent** | SwarmCoordinator, SwarmDecisionEngine, SwarmEvaluator |
| **Supporting Agents** | AgentManager, TaskRouter, AutonomousSwarm |
| **Flow** | Spawn → Coordinate → Decide → Evaluate → Iterate |
| **Governance Gates** | Constitution §5 (Product/code = autonomous reversible), ADR-001 (No self-graded homework - Evaluator separate), §13 (Agent identity) |
| **Runtime Status** | ✅ Active (4 orchestrator agents) |
| **Components** | Spawn logic, consensus, decision engine, evaluation |

---

### Repository Health Workflows
| Field | Value |
|-------|-------|
| **Workflow ID** | `repository_health` |
| **Responsible Agent** | **NOT IMPLEMENTED** (doc: Knowledge Agent, Documentation Agent) |
| **Supporting Agents** | BuilderAgent (repairs), ReviewAgent (validation) |
| **Flow** | Scan → Plan → Monitor → Repair → Validate |
| **Governance Gates** | ADR-007 (Repository Intelligence), Constitution §6 (Knowledge = infrastructure) |
| **Runtime Status** | ⚠️ Framework exists, no owning agent |
| **Components** | `repository_health_monitor.py`, `repository_health_service.py`, `repository_planner.py`, `repository_scanner.py`, `repository_state.py` |

---

### Repair Workflows (`repair_agent.py`, `repair_workflow.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `code_repair` |
| **Responsible Agent** | RepairAgent |
| **Supporting Agents** | BuilderAgent (code gen), ReviewAgent (validation) |
| **Flow** | Detect → Analyze → Generate Repair → Validate → Apply |
| **Governance Gates** | Constitution §5 (Product/code = autonomous reversible), ADR-001 (Review separate from generation) |
| **Runtime Status** | ✅ Active |
| **Key Methods** | `analyze()`, `generate_repair()`, `validate_repair()` |

---

### Code Generation Workflows (`code_generation_task.py`, `builder_agent.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `code_generation` |
| **Responsible Agent** | BuilderAgent |
| **Supporting Agents** | ReviewAgent (validation), RepairAgent (fixes) |
| **Flow** | Spec → Generate → Review → Repair → Complete |
| **Governance Gates** | Constitution §5, ADR-001, ADR-008 (Documentation-driven) |
| **Runtime Status** | ✅ Active |

---

### Continuous Improvement Workflows
| Workflow | Responsible Agent | Supporting | Status |
|----------|-------------------|------------|--------|
| `improvement_planner` | ImprovementPlannerAgent | SwarmEvaluator | ✅ |
| `failure_analyzer` | FailureAnalyzerAgent | SwarmEvaluator | ✅ |
| `technical_debt_analyzer` | TechnicalDebtAnalyzerAgent | BuilderAgent | ✅ |
| `coverage_analyzer` | CoverageAnalyzerAgent | ReviewAgent | ✅ |
| `architecture_validator` | ArchitectureValidatorAgent | ChiefArchitect (doc) | ✅ |

---

## Service Workflows (`core/services/`)

### Tenant Lifecycle (`tenant_service.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `tenant_lifecycle` |
| **Responsible Agent** | **NOT IMPLEMENTED** (doc: Deployment Agent, Backup Agent) |
| **Supporting Agents** | BoxDeployer, FileManager, S3Client |
| **Flow** | Register → Provision (Docker/Hyper-V) → Monitor → Backup |
| **Governance Gates** | Constitution §4.6 (Portfolio isolation - **GAP**), §4.5 (Identity verification), §4.7 (Simulation fallback), §10 (Licensed boundaries) |
| **Runtime Status** | ⚠️ Service exists, no owning agent |
| **Key Methods** | `register()`, `provision()`, `get_status()`, `backup()` |

---

### Workflow Service (`workflow_service.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `workflow_management` |
| **Responsible Agent** | **NOT IMPLEMENTED** (doc: Release Agent, Operations) |
| **Supporting Agents** | TaskRouter, AgentManager |
| **Flow** | Create → Advance → Complete → Status → History |
| **Governance Gates** | Constitution §5, RELEASE_MANAGEMENT SOP |
| **Runtime Status** | ⚠️ Service exists, no owning agent |
| **Key Methods** | `create()`, `advance()`, `complete()`, `get_status()`, `get_history()` |

---

### Ticket Service (`ticket_service.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `ticket_lifecycle` |
| **Responsible Agent** | **NOT IMPLEMENTED** (doc: QA Agent, Operations) |
| **Supporting Agents** | NotificationService, Celery Workers |
| **Flow** | Create → Lifecycle → Comments → History → Escalate → Metrics |
| **Governance Gates** | Constitution §3 (Legible authorship - TicketHistory), §5.1 (Legal triggers), §12.6 (Reconciliation escalation) |
| **Runtime Status** | ⚠️ Service exists, no owning agent |
| **Key Methods** | `create()`, `update()`, `escalate()`, `get_comments()`, `get_history()`, `get_metrics()` |

---

### Notification Service (`notification_service.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `notification_delivery` |
| **Responsible Agent** | **NOT IMPLEMENTED** (doc: Monitoring Agent) |
| **Supporting Agents** | WebSocketManager, Celery EmailWorker |
| **Flow** | In-app + WebSocket push |
| **Governance Gates** | Constitution §5 (External comms = human-reviewed) |
| **Runtime Status** | ⚠️ Service exists, no owning agent |
| **Key Methods** | `notify()`, `broadcast()`, `push_ws()` |

---

### Payment Service (`payment_service.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `payment_processing` |
| **Responsible Agent** | **NOT IMPLEMENTED** (doc: Payment Agent) |
| **Supporting Agents** | Governance Agent (approval), Audit Agent |
| **Flow** | Checkout → Subscription → Cancel → Webhook |
| **Governance Gates** | Constitution §5 (Financial = human approval EVERY $), §12 (Session caps, allowlists, dual-rail, audit logging - **GAPS**) |
| **Runtime Status** | ⚠️ Service exists, no owning agent, monetary rules not enforced |
| **Key Methods** | `create_checkout()`, `cancel_subscription()`, `handle_webhook()` |

---

## Celery Workflows (`infrastructure/celery/`)

### Notification Tasks (`notification_tasks.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `celery_notifications` |
| **Worker** | Celery notification worker (queue: `notifications`) |
| **Tasks** | `send_notification`, `send_email_notification`, `broadcast_event` |
| **Owning Agent** | None (doc: Monitoring Agent) |
| **Governance** | Constitution §5, §7 (SMTP secrets via env) |
| **Runtime Status** | ✅ Active |

---

### Ticket Tasks (`ticket_tasks.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `celery_tickets` |
| **Worker** | Celery ticket worker (queue: `tickets`, `high_priority`) |
| **Tasks** | `process_ticket`, `check_sla_breaches`, `escalate_overdue_tickets` |
| **Owning Agent** | None (doc: QA Agent, Operations) |
| **Governance** | Constitution §5.1 (Legal triggers), §6 (Emergency), §12.6 (Reconciliation) |
| **Runtime Status** | ✅ Active |

---

### Workflow Tasks (`workflow_tasks.py`)
| Field | Value |
|-------|-------|
| **Workflow ID** | `celery_workflows` |
| **Worker** | Celery workflow worker (queue: `default`) |
| **Tasks** | `execute_workflow_step`, `handle_step_failure`, `advance_workflow` |
| **Owning Agent** | None (doc: Release Agent, Operations) |
| **Governance** | Constitution §5 |
| **Runtime Status** | ✅ Active |

---

### Celery Beat Schedule (Periodic)
| Task | Schedule | Queue | Purpose |
|------|----------|-------|---------|
| `check_sla_breaches` | Every 30 min | `high_priority` | SLA watchdog |
| `escalate_overdue_tickets` | Every hour | `high_priority` | Escalation sweep |

---

## API Workflows (`interfaces/api/routers/`)

### Workflow Router (`workflows.py`)
| Aspect | Details |
|--------|---------|
| **Endpoints** | CRUD, advance, complete, status |
| **Owning Agent** | None (API layer) |
| **Backend** | WorkflowService |
| **Governance** | Constitution §5, authentication via AuthMiddleware |

---

### Tenant Router (`tenants.py`)
| Aspect | Details |
|--------|---------|
| **Endpoints** | Register, provision, status |
| **Owning Agent** | None |
| **Backend** | TenantService, BoxDeployer |
| **Governance** | Constitution §4.5 (Identity verification), §4.6 (Isolation), §4.7 (Simulation fallback) |

---

### Payment Router (`payments.py`)
| Aspect | Details |
|--------|---------|
| **Endpoints** | Checkout, subscriptions, webhooks |
| **Owning Agent** | None |
| **Backend** | PaymentService, StripeClient |
| **Governance** | Constitution §5, §12 (Critical gaps) |

---

### Outreach Router (`outreach.py`)
| Aspect | Details |
|--------|---------|
| **Endpoints** | Campaigns, sequences |
| **Owning Agent** | None |
| **Backend** | OutreachAgent, Celery OutreachWorker |
| **Governance** | Constitution §5 (AI-drafted, human-reviewed) |

---

## Documented Agent Workflows (from AGENT_REGISTRY.md)

| Documented Agent | Workflow Responsibility | Runtime Implementation |
|------------------|------------------------|------------------------|
| Program Director | Strategic coordination, prioritization, allocation, conflict resolution | ❌ Not implemented |
| Chief Architect | Architecture reviews, standards enforcement, technical direction, design validation | ❌ Not implemented (StrategyAgent partial) |
| Product Strategist | Product direction, requirement validation, market alignment | ❌ Not implemented |
| Backend Agent | Business logic, services, integrations, database interactions | ❌ Not implemented (BuilderAgent partial) |
| Frontend Agent | Interfaces, user journeys, interaction design, accessibility | ❌ Not implemented |
| Database Agent | Schema design, relationship management, performance review | ❌ Not implemented |
| Integration Agent | API integrations, service communication, data exchange validation | ❌ Not implemented |
| QA Agent | Testing, validation, defect discovery | ❌ Not implemented |
| Security Agent | Vulnerability analysis, threat modeling, dependency auditing | ❌ Not implemented |
| Performance Agent | Profiling, benchmarking, optimization recommendations | ❌ Not implemented |
| Accessibility Agent | Standards validation, accessibility review | ❌ Not implemented |
| Knowledge Agent | Knowledge graph maintenance, relationship preservation, context quality | ❌ Not implemented |
| Documentation Agent | Documentation generation, validation, synchronization | ❌ Not implemented |
| RAG Agent | Embedding management, vector indexing, retrieval optimization | ❌ Not implemented |
| Release Agent | Releases, versioning, change validation | ❌ Not implemented |
| Monitoring Agent | Monitoring, alerting, operational analysis | ❌ Not implemented (stubs only) |
| Backup Agent | Backup creation, recovery validation, archive management | ❌ Not implemented |
| Governance Agent | Policy validation, governance auditing, constitutional traceability | ❌ Not implemented |
| Audit Agent | Activity reviews, compliance validation, historical analysis | ❌ Not implemented |

---

## Workflow Coverage Matrix

| Workflow Category | Total Workflows | Has Responsible Agent | Has Supporting Agents | Governance Gates |
|-------------------|-----------------|----------------------|----------------------|------------------|
| Core (`core/workflows/`) | 3 | 2 | ✅ | ✅ |
| Orchestration (`core/orchestration/`) | 12 | 12 | ✅ | ✅ |
| Service (`core/services/`) | 4 | 0 | ✅ | ⚠️ Partial |
| Celery (`infrastructure/celery/`) | 3 | 0 | ✅ | ✅ |
| API (`interfaces/api/`) | 4+ | 0 | N/A | ✅ |
| Documented Agents | 33 | 0 | N/A | N/A |
| **TOTAL** | **59+** | **14** | **✅** | **Mixed** |

---

## Missing Workflow Owners (Critical)

| Workflow | Current Owner | Required Agent | Priority |
|----------|---------------|----------------|----------|
| Tenant Lifecycle | TenantService (no agent) | Deployment Agent, Backup Agent | P0 |
| Workflow Management | WorkflowService (no agent) | Release Agent | P0 |
| Ticket Lifecycle | TicketService (no agent) | QA Agent, Operations | P0 |
| Notification Delivery | NotificationService (no agent) | Monitoring Agent | P1 |
| Payment Processing | PaymentService (no agent) | Payment Agent, Governance Agent | P0 |
| Repository Health | Framework (no agent) | Knowledge Agent, Documentation Agent | P1 |
| Monitoring | Stubs only | Monitoring Agent | P0 |
| Backup/Recovery | Services only | Backup Agent | P1 |
| Disaster Recovery | Doc only | Backup Agent, Governance Agent | P1 |

---

## Governance Touchpoints by Workflow

| Workflow | Constitution | ADRs | Operations SOPs | Agent SOPs |
|----------|-------------|------|-----------------|------------|
| Campaign Pipeline | §5 (Product, External comms) | ADR-001, ADR-006 | - | StrategyAgent, OutreachAgent |
| Feedback Loop | §12 | ADR-012 | CONTINUOUS_IMPROVEMENT_PROGRAM | All agents |
| Agent Execution | §13, §5 | ADR-001, ADR-003, ADR-006 | - | All agents |
| Swarm Coordination | §5, §13 | ADR-001, ADR-006, ADR-011 | - | Orchestrator agents |
| Repair | §5 | ADR-001 | SELF_HEALING_ARCHITECTURE | RepairAgent, ReviewAgent |
| Code Generation | §5 | ADR-001, ADR-008 | RELEASE_MANAGEMENT, CHANGE_MANAGEMENT | BuilderAgent, ReviewAgent |
| Tenant Lifecycle | §4.5, §4.6, §4.7, §10 | ADR-009 | DEPLOYMENT, BACKUP_STRATEGY | Deployment Agent |
| Payment Processing | §5, §12 | ADR-003, ADR-011 | MONETARY RULES (§12) | Payment Agent |
| Celery Tasks | §5, §7, §12 | ADR-009 | MONITORING, SELF_HEALING | Workers |
| Monitoring | §5 | ADR-012 | MONITORING_AND_ALERTING | Monitoring Agent |

---

## Notes

- **14/59+ workflows** have responsible runtime agents
- **33 documented agents** have **0** workflow ownership in runtime
- **Service workflows** (4) exist but lack owning agents
- **Celery workflows** (3) run but have no agent identity
- **Governance gates** defined but not enforced in most workflows
- **Priority**: Assign agents to service workflows + implement missing agents