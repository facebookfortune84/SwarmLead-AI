# Agent Registry

**Generated**: 2026-07-24  
**Sources**: `docs/agents/AGENT_REGISTRY.md`, `docs/agents/AGENT_ORGANIZATION_CHART.md`, `core/agents/`, `core/orchestration/`, `asset_processor/output/archetypes/`  
**Classification Rules**: Active | Deprecated | Archive Candidate | Delete Candidate | Unknown

---

## Cross-Reference Matrix

| Agent Role | Runtime Implementation | Documentation (AGENT_REGISTRY.md) | Archetype DNA | Status |
|------------|------------------------|-----------------------------------|---------------|--------|
| **Program Director** | ❌ Not implemented | ✅ Executive Layer | ❌ | Unknown |
| **Chief Architect** | ❌ Not implemented | ✅ Executive Layer | ✅ Architect (5 DNA) | Unknown |
| **Product Strategist** | ❌ Not implemented | ✅ Executive Layer | ❌ | Unknown |
| **Governance Agent** | ❌ Not implemented | ✅ Governance Layer | ✅ Governance Director (3 DNA) | Unknown |
| **Audit Agent** | ❌ Not implemented | ✅ Governance Layer | ❌ | Unknown |
| **Backend Agent** | ❌ Not implemented | ✅ Engineering Layer | ❌ | Unknown |
| **Frontend Agent** | ❌ Not implemented | ✅ Engineering Layer | ❌ | Unknown |
| **Database Agent** | ❌ Not implemented | ✅ Engineering Layer | ❌ | Unknown |
| **Integration Agent** | ❌ Not implemented | ✅ Engineering Layer | ❌ | Unknown |
| **QA Agent** | ❌ Not implemented | ✅ Quality Layer | ❌ | Unknown |
| **Security Agent** | ❌ Not implemented | ✅ Quality Layer | ❌ | Unknown |
| **Performance Agent** | ❌ Not implemented | ✅ Quality Layer | ❌ | Unknown |
| **Accessibility Agent** | ❌ Not implemented | ✅ Quality Layer | ❌ | Unknown |
| **Knowledge Agent** | ❌ Not implemented | ✅ Knowledge Layer | ❌ | Unknown |
| **Documentation Agent** | ❌ Not implemented | ✅ Knowledge Layer | ❌ | Unknown |
| **RAG Agent** | ❌ Not implemented | ✅ Knowledge Layer | ❌ | Unknown |
| **Release Agent** | ❌ Not implemented | ✅ Operations Layer | ❌ | Unknown |
| **Monitoring Agent** | ❌ Not implemented | ✅ Operations Layer | ❌ | Unknown |
| **Backup Agent** | ❌ Not implemented | ✅ Operations Layer | ❌ | Unknown |
| **Governance Agent (ops)** | ❌ Not implemented | ✅ Operations Layer | ✅ Governance Director (3 DNA) | Unknown |

---

## Runtime Agents (Implemented in Code)

### Core Agent Runtime (`core/agents/`, `core/orchestration/`)

| Agent Name | Source | Runtime Agent | Documentation Agent | Archetype Agent | Hybrid Agent | Responsibilities | Capabilities | Dependencies | Governance Level | Authority Level | Status | Confidence |
|------------|--------|---------------|---------------------|-----------------|--------------|------------------|--------------|--------------|------------------|-----------------|--------|------------|
| BaseAgent | `core/agents/base_agent.py` | ✅ Abstract base | ❌ | ❌ | ✅ Base for all | Structured execution, validation, LLM integration, logging | run(), validate(), execute(), call_llm() | OllamaClient, config | Constitutional (inherits) | None (abstract) | Active | 0.95 |
| StrategyAgent | `core/agents/strategy/strategy_agent.py` | ✅ Concrete | ✅ Strategy (implied) | ✅ Architect DNA | ✅ Hybrid | Business strategy generation with memory integration | Strategy generation, memory retrieval, LLM reasoning | BaseAgent, LongTermMemory, VectorStore, OllamaClient | Domain: Product/code = autonomous reversible | Strategy output only | Active | 0.90 |
| OutreachAgent | `core/agents/outreach/outreach_agent.py` | ✅ Concrete | ❌ | ❌ | ✅ Hybrid | Email/outreach content generation | Outreach generation, memory retrieval, LLM reasoning | BaseAgent, LongTermMemory, VectorStore, OllamaClient | Domain: External comms = AI-drafted, human-reviewed | Outreach content only | Active | 0.90 |
| BuilderAgent | `core/orchestration/builder_agent.py` | ✅ Concrete | ❌ | ✅ Builder (30 DNA) | ✅ Hybrid | Code generation from specifications | Code generation, file operations, LLM reasoning | BaseAgent, OllamaClient | Domain: Product/code = autonomous reversible | Code output only | Active | 0.85 |
| RepairAgent | `core/orchestration/repair_agent.py` | ✅ Concrete | ❌ | ❌ | ✅ Hybrid | Automated code repair | Code analysis, repair generation, LLM reasoning | BaseAgent, OllamaClient | Domain: Product/code = autonomous reversible | Repair proposals only | Active | 0.85 |
| ReviewAgent | `core/orchestration/review_agent.py` | ✅ Concrete | ❌ | ✅ Reviewer (4 DNA) | ✅ Hybrid | Code quality review | Code review, quality assessment, LLM reasoning | BaseAgent, OllamaClient | Domain: QA = separate from generation | Review decisions only | Active | 0.90 |
| AgentManager | `core/orchestration/agent_manager.py` | ✅ Registry/Manager | ❌ | ❌ | ✅ Orchestrator | Agent registration, execution, metadata | Register, execute, get_agent, get_all_agents | BaseAgent subclasses | Constitutional (orchestration = coordination | Execution orchestration | Active | 0.90 |
| TaskRouter | `core/orchestration/task_router.py` | ✅ Router | ❌ | ✅ Orchestrator (10 DNA) | ✅ Hybrid | Route tasks to registered agents | Register routes, route tasks, fallback | AgentManager, BaseAgent | Domain: Product/code = autonomous reversible | Routing decisions only | Active | 0.85 |
| Scheduler | `core/orchestration/scheduler.py` | ✅ Scheduler | ❌ | ❌ | ✅ Hybrid | Cron-like and event-driven scheduling | Schedule, run_scheduled, task management | TaskRouter, AgentManager | Constitutional (audit logging) | Scheduling only | Active | 0.85 |
| SwarmCoordinator | `core/orchestration/swarm_coordinator.py` | ✅ Coordinator | ❌ | ✅ Orchestrator (10 DNA) | ✅ Hybrid | Multi-agent coordination | Coordinate, consensus, decision engine | AgentManager, TaskRouter, SwarmDecisionEngine | Domain: Product/code = autonomous reversible | Coordination decisions | Active | 0.80 |
| SwarmDecisionEngine | `core/orchestration/swarm_decision_engine.py` | ✅ Decision Engine | ❌ | ✅ Orchestrator (10 DNA) | ✅ Hybrid | Collective decision making | Decide, evaluate options, consensus | SwarmCoordinator, SwarmEvaluator | Constitutional (no self-graded homework) | Decision recommendations | Active | 0.80 |
| SwarmEvaluator | `core/orchestration/swarm_evaluator.py` | ✅ Evaluator | ❌ | ❌ | ✅ Hybrid | Evaluate swarm decisions | Evaluate, score, feedback | SwarmDecisionEngine | Constitutional (verification separate) | Evaluation only | Active | 0.80 |
| AutonomousSwarm | `core/orchestration/autonomous_swarm.py` | ✅ Swarm Runtime | ❌ | ✅ Orchestrator (10 DNA) | ✅ Hybrid | Self-organizing agent collectives | Spawn, coordinate, lifecycle | SwarmCoordinator, AgentManager | Domain: Product/code = autonomous reversible | Swarm orchestration | Active | 0.75 |

---

## Documentation Agents (AGENT_REGISTRY.md - 33 Roles)

### Executive Layer (3)

| Agent Name | Source | Runtime Agent | Documentation Agent | Archetype Agent | Hybrid Agent | Responsibilities | Capabilities | Dependencies | Governance Level | Authority Level | Status | Confidence |
|------------|--------|---------------|---------------------|-----------------|--------------|------------------|--------------|--------------|------------------|-----------------|--------|------------|
| Program Director | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Strategic coordination, initiative prioritization, resource allocation, conflict resolution | Coordination, prioritization, allocation, resolution | Human Operator | Constitutional (top of hierarchy) | Full org authority | Unknown | 0.70 |
| Chief Architect | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ✅ Architect (5 DNA) | ❌ Doc+Archetype | Architecture reviews, standards enforcement, technical direction, design validation | Architecture, standards, direction, validation | Program Director | Constitutional (ADR-003, ADR-006) | Architecture authority | Unknown | 0.80 |
| Product Strategist | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Product direction, requirement validation, market alignment | Product, validation, alignment | Program Director | Constitutional (customer value) | Product authority | Unknown | 0.70 |

### Engineering Layer (4)

| Agent Name | Source | Runtime Agent | Documentation Agent | Archetype Agent | Hybrid Agent | Responsibilities | Capabilities | Dependencies | Governance Level | Authority Level | Status | Confidence |
|------------|--------|---------------|---------------------|-----------------|--------------|------------------|--------------|--------------|------------------|-----------------|--------|------------|
| Backend Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Business logic, services, integrations, database interactions | Backend development | Chief Architect | Domain: Product/code = autonomous reversible | Backend services | Unknown | 0.70 |
| Frontend Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Interfaces, user journeys, interaction design, accessibility | Frontend development | Chief Architect | Domain: Product/code = autonomous reversible | Frontend interfaces | Unknown | 0.70 |
| Database Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Schema design, relationship management, performance review | Database design, optimization | Chief Architect | Domain: Product/code = autonomous reversible | Schema decisions | Unknown | 0.70 |
| Integration Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | API integrations, service communication, data exchange validation | Integration development | Chief Architect | Domain: Product/code = autonomous reversible | Integration decisions | Unknown | 0.70 |

### Quality Layer (4)

| Agent Name | Source | Runtime Agent | Documentation Agent | Archetype Agent | Hybrid Agent | Responsibilities | Capabilities | Dependencies | Governance Level | Authority Level | Status | Confidence |
|------------|--------|---------------|---------------------|-----------------|--------------|------------------|--------------|--------------|------------------|-----------------|--------|------------|
| QA Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Testing, validation, defect discovery | Testing, validation | Chief Architect | Constitutional (no self-graded homework) | Test/validation only | Unknown | 0.70 |
| Security Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Vulnerability analysis, threat modeling, dependency auditing | Security analysis | Chief Architect | Constitutional (secrets never agent-touchable) | Security reviews | Unknown | 0.70 |
| Performance Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Profiling, benchmarking, optimization recommendations | Performance analysis | Chief Architect | Domain: Product/code = autonomous reversible | Perf recommendations | Unknown | 0.70 |
| Accessibility Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Standards validation, accessibility review | Accessibility testing | Chief Architect | Domain: Product/code = autonomous reversible | A11y reviews | Unknown | 0.70 |

### Knowledge Layer (3)

| Agent Name | Source | Runtime Agent | Documentation Agent | Archetype Agent | Hybrid Agent | Responsibilities | Capabilities | Dependencies | Governance Level | Authority Level | Status | Confidence |
|------------|--------|---------------|---------------------|-----------------|--------------|------------------|--------------|--------------|------------------|-----------------|--------|------------|
| Knowledge Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Knowledge graph maintenance, relationship preservation, context quality | Knowledge management | Chief Architect | Constitutional (knowledge = infrastructure) | Knowledge curation | Unknown | 0.70 |
| Documentation Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Documentation generation, validation, synchronization | Doc generation | Chief Architect | Constitutional (docs = part of product) | Doc authority | Unknown | 0.70 |
| RAG Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Embedding management, vector indexing, retrieval optimization | RAG operations | Chief Architect | Constitutional (RAG = retrieval quality) | RAG operations | Unknown | 0.70 |

### Operations Layer (3)

| Agent Name | Source | Runtime Agent | Documentation Agent | Archetype Agent | Hybrid Agent | Responsibilities | Capabilities | Dependencies | Governance Level | Authority Level | Status | Confidence |
|------------|--------|---------------|---------------------|-----------------|--------------|------------------|--------------|--------------|------------------|-----------------|--------|------------|
| Release Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Releases, versioning, change validation | Release management | Program Director | Constitutional (reversibility) | Release authority | Unknown | 0.70 |
| Monitoring Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Monitoring, alerting, operational analysis | Monitoring, alerting | Program Director | Constitutional (observability) | Monitoring config | Unknown | 0.70 |
| Backup Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Backup creation, recovery validation, archive management | Backup, recovery | Program Director | Constitutional (organizational memory) | Backup authority | Unknown | 0.70 |

### Governance Layer (2)

| Agent Name | Source | Runtime Agent | Documentation Agent | Archetype Agent | Hybrid Agent | Responsibilities | Capabilities | Dependencies | Governance Level | Authority Level | Status | Confidence |
|------------|--------|---------------|---------------------|-----------------|--------------|------------------|--------------|--------------|------------------|-----------------|--------|------------|
| Governance Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ✅ Governance Director (3 DNA) | ❌ Doc+Archetype | Policy validation, governance auditing, constitutional traceability | Governance enforcement | Program Director | Constitutional (supreme) | Policy enforcement | Unknown | 0.80 |
| Audit Agent | `docs/agents/AGENT_REGISTRY.md` | ❌ | ✅ | ❌ | ❌ Doc-only | Activity reviews, compliance validation, historical analysis | Auditing | Program Director | Constitutional (independent verification) | Audit authority | Unknown | 0.70 |

---

## Archetype Agents (DNA Files - 8 Types)

| Archetype | DNA Count | High-Confidence (100%) | Runtime Mapping | Status |
|-----------|-----------|------------------------|-----------------|--------|
| Architect | 5 | 2 (Quest Design, Spec Prompt) | StrategyAgent → Architect | Hybrid |
| Builder | 30 | 11 (AI Studio, Builder, Claude Code 2.0, gemini-2.5-pro, gpt-4.1, gpt-4o, gpt-5, gpt-5-mini, gpt-5-agent, openai-codex, gemini-cli, google-gemini) | BuilderAgent → Builder | Hybrid |
| Governance Director | 3 | 0 | ❌ Not implemented | Unknown |
| Orchestrator | 10 | 4 (Agent loop, Default, Enterprise, System Prompt) | SwarmCoordinator, TaskRouter, SwarmDecisionEngine → Orchestrator | Hybrid |
| Planner | 4 | 2 (phase_mode, planning-mode) | ❌ Not implemented | Unknown |
| Researcher | 2 | 1 (DeepWiki) | ❌ Not implemented | Unknown |
| Reviewer | 4 | 4 (DocumentAction, ExplainAction, MessageAction, PreviewAction) | ReviewAgent → Reviewer | Hybrid |
| Optimizer | 0 | 0 | ❌ Referenced in DNA but no files | Unknown |

---

## Summary Statistics

| Category | Total | Implemented (Runtime) | Documented Only | Archetype DNA | Hybrid (Runtime+Archetype) | Unknown Status |
|----------|-------|----------------------|-----------------|---------------|---------------------------|----------------|
| Executive | 3 | 0 | 3 | 1 | 0 | 3 |
| Engineering | 4 | 0 | 4 | 0 | 0 | 4 |
| Quality | 4 | 0 | 4 | 0 | 0 | 4 |
| Knowledge | 3 | 0 | 3 | 0 | 0 | 3 |
| Operations | 3 | 0 | 3 | 0 | 0 | 3 |
| Governance | 2 | 0 | 2 | 1 | 0 | 2 |
| **Runtime Core** | **12** | **12** | **0** | **0** | **12** | **0** |
| **Archetype Types** | **8** | **0** | **0** | **64** | **5 mapped** | **3** |
| **TOTAL** | **39** | **12** | **19** | **65** | **17** | **15** |

---

## Critical Gaps

1. **33 Documented Agents Not Implemented** - Only 12 runtime agents exist vs 33 documented roles
2. **Governance Director Archetype Not Implemented** - 3 DNA files but no runtime agent
3. **Planner/Researcher Archetypes Not Implemented** - 6 DNA files but no runtime agents
4. **No Agent Activation Mechanism** - AGENT_REGISTRY.md defines roles but no instantiation logic
5. **Constitutional Permissions (§13) Not Enforced** - Per-role tool/data allowlists missing
6. **Portfolio Isolation (§4.6) Not Implemented** - Agents lack tenant scoping
7. **Agent Identity (§13) Not Implemented** - Unique non-shared identities, scoped credentials

---

## Notes

- **Hybrid Agents** = Runtime implementation exists AND archetype DNA exists (5 mapped: Strategy→Architect, Outreach→?, Builder→Builder, Repair→?, Review→Reviewer, Orchestration→Orchestrator)
- **Unknown Status** = Documented in AGENT_REGISTRY.md but no runtime implementation and no archetype DNA
- **Active** = Runtime implementation exists and is used (verified in orchestration code)
- The 12 runtime agents form the operational core; 33 documented agents are target architecture
- Archetype DNA provides prompt infrastructure for future agent instantiation