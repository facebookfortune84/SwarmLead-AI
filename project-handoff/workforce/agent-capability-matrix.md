# Agent Capability Matrix

**Generated**: 2026-07-26  
**Sources**: `agent-registry.md`, `prompt-registry.md`, `tool-registry.md`, `sop-registry.md`, archetype DNA files, runtime code

---

## Capability Classification

| Capability Category | Description |
|---------------------|-------------|
| **Reasoning** | Cognitive frameworks, decision-making, planning |
| **Technical** | Code generation, architecture, infrastructure |
| **Communication** | Inter-agent coordination, messaging, collaboration |
| **Memory** | Session, long-term, vector storage and retrieval |
| **Governance** | Policy enforcement, verification, audit |
| **Operations** | Deployment, monitoring, backup, release |
| **Quality** | Review, testing, security, performance |

---

## Runtime Agents (Implemented)

### BaseAgent (`core/agents/base_agent.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Abstract Base |
| **Documentation** | ❌ |
| **Archetype** | Base (all inherit) |
| **Capabilities** | Structured execution, input validation, context handling, LLM integration, structured logging, trace_id propagation |
| **Inputs** | `input_data: Dict`, `context: Dict`, `trace_id: str` |
| **Outputs** | `{"success": bool, "agent": str, "result": Any, "error": str}` |
| **Tools Used** | OllamaClient, ConfigLoader, Logger |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md (template) |
| **Governance Dependencies** | Constitution §3, §5, §7, §13; ADR-001, ADR-003 |

---

### StrategyAgent (`core/agents/strategy/strategy_agent.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Concrete |
| **Documentation** | ✅ Implied (Strategy) |
| **Archetype** | Architect (5 DNA) |
| **Capabilities** | Business strategy generation, memory retrieval (long-term + vector), LLM reasoning with fallback, evidence-based output |
| **Inputs** | `product`, `audience`, `goal`, `context`, `trace_id` |
| **Outputs** | `angles`, `hooks`, `summary`, `strategy` |
| **Tools Used** | OllamaClient, LongTermMemory, VectorStore, BaseAgent |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, AGENT_COMMUNICATION_PROTOCOL.md |
| **Governance Dependencies** | Constitution §5 (Product/code = autonomous reversible), ADR-001 (no self-graded homework), ADR-006 |

---

### OutreachAgent (`core/agents/outreach/outreach_agent.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Concrete |
| **Documentation** | ❌ |
| **Archetype** | None mapped |
| **Capabilities** | Outreach content generation, angle/audience/product synthesis, memory retrieval, feedback incorporation, structured output parsing |
| **Inputs** | `angles`, `audience`, `product`, `context`, `trace_id` |
| **Outputs** | `outreach_content`, `parsed_structure` |
| **Tools Used** | OllamaClient, LongTermMemory, VectorStore, BaseAgent |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, AGENT_COMMUNICATION_PROTOCOL.md |
| **Governance Dependencies** | Constitution §5 (External comms = AI-drafted, human-reviewed), §12 (monetary rules) |

---

### BuilderAgent (`core/orchestration/builder_agent.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Concrete |
| **Documentation** | ❌ |
| **Archetype** | Builder (30 DNA, 11 high-confidence) |
| **Capabilities** | Code generation from specifications, file operations, LLM reasoning, structured output (markdown, code_refs) |
| **Inputs** | Specification, context, trace_id |
| **Outputs** | Generated code, file operations, structured markdown |
| **Tools Used** | OllamaClient, BaseAgent, FileManager (via services) |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, RELEASE_MANAGEMENT.md, CHANGE_MANAGEMENT.md |
| **Governance Dependencies** | Constitution §5 (Product/code = autonomous reversible), ADR-001, ADR-008 |

---

### RepairAgent (`core/orchestration/repair_agent.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Concrete |
| **Documentation** | ❌ |
| **Archetype** | None mapped |
| **Capabilities** | Automated code repair, code analysis, repair generation, LLM reasoning, target-specific fixes |
| **Inputs** | `target` (file/module), context, trace_id |
| **Outputs** | Repair proposals, patch sets, action plans |
| **Tools Used** | OllamaClient, BaseAgent |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, SELF_HEALING_ARCHITECTURE.md |
| **Governance Dependencies** | Constitution §5 (Product/code = autonomous reversible), ADR-012 (Continuous Improvement) |

---

### ReviewAgent (`core/orchestration/review_agent.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Concrete |
| **Documentation** | ❌ |
| **Archetype** | Reviewer (4 DNA, all 100% confidence) |
| **Capabilities** | Code quality review, quality assessment, LLM reasoning, structured review decisions, evidence-based assessment |
| **Inputs** | Code/context to review, trace_id |
| **Outputs** | Review decisions, quality scores, feedback |
| **Tools Used** | OllamaClient, BaseAgent |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, AGENT_COMMUNICATION_PROTOCOL.md |
| **Governance Dependencies** | Constitution §3 (No self-graded homework), §5 (QA separate from generation), ADR-001 |

---

### AgentManager (`core/orchestration/agent_manager.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Registry/Manager |
| **Documentation** | ❌ |
| **Archetype** | Orchestrator (implied) |
| **Capabilities** | Agent registration, execution orchestration, metadata retrieval, async/sync execution, error handling with trace logging |
| **Inputs** | Agent name, input_data, context, trace_id |
| **Outputs** | Execution results, agent metadata, registered agent list |
| **Tools Used** | BaseAgent subclasses, Logger |
| **SOP Dependencies** | AGENT_LIFECYCLE.md, AGENT_OPERATING_SYSTEM.md |
| **Governance Dependencies** | Constitution §13 (Agent identity), ADR-006 |

---

### TaskRouter (`core/orchestration/task_router.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Router |
| **Documentation** | ❌ |
| **Archetype** | Orchestrator (10 DNA, 4 high-confidence) |
| **Capabilities** | Route registration, task routing with fallback, async/sync handler execution, context passing |
| **Inputs** | `task_name`, `input_data`, `context`, trace_id |
| **Outputs** | Routed results, fallback handling |
| **Tools Used** | AgentManager, BaseAgent, Logger |
| **SOP Dependencies** | AGENT_COMMUNICATION_PROTOCOL.md |
| **Governance Dependencies** | Constitution §5, ADR-006 |

---

### Scheduler (`core/orchestration/scheduler.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Scheduler |
| **Documentation** | ❌ |
| **Archetype** | None mapped |
| **Capabilities** | Cron-like scheduling, event-driven tasks, task persistence, performance logging, async/sync handler support |
| **Inputs** | Schedule config, input_data, context, trace_id |
| **Outputs** | Scheduled execution results, task history |
| **Tools Used** | TaskRouter, AgentManager, Logger, Performance logging |
| **SOP Dependencies** | RELEASE_MANAGEMENT.md, MONITORING_AND_ALERTING.md |
| **Governance Dependencies** | Constitution §5, audit logging requirements |

---

### SwarmCoordinator (`core/orchestration/swarm_coordinator.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Coordinator |
| **Documentation** | ❌ |
| **Archetype** | Orchestrator (10 DNA, 4 high-confidence) |
| **Capabilities** | Multi-agent coordination, consensus building, decision engine integration, agent lifecycle management |
| **Inputs** | Coordination requests, agent pool, trace_id |
| **Outputs** | Coordination decisions, consensus results |
| **Tools Used** | AgentManager, TaskRouter, SwarmDecisionEngine, SwarmEvaluator |
| **SOP Dependencies** | AGENT_COMMUNICATION_PROTOCOL.md, AGENT_OPERATING_SYSTEM.md |
| **Governance Dependencies** | Constitution §5, ADR-006, ADR-011 (Human Authority) |

---

### SwarmDecisionEngine (`core/orchestration/swarm_decision_engine.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Decision Engine |
| **Documentation** | ❌ |
| **Archetype** | Orchestrator (10 DNA) |
| **Capabilities** | Collective decision making, option evaluation, consensus building, decision recommendations |
| **Inputs** | Decision context, options, agent inputs |
| **Outputs** | Decisions, evaluations, consensus scores |
| **Tools Used** | SwarmCoordinator, SwarmEvaluator |
| **SOP Dependencies** | AGENT_COMMUNICATION_PROTOCOL.md |
| **Governance Dependencies** | Constitution §3 (No self-graded homework), ADR-001, ADR-011 |

---

### SwarmEvaluator (`core/orchestration/swarm_evaluator.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Evaluator |
| **Documentation** | ❌ |
| **Archetype** | None mapped |
| **Capabilities** | Decision evaluation, scoring, feedback generation, verification separate from generation |
| **Inputs** | Decisions, context, criteria |
| **Outputs** | Evaluation scores, feedback, verification results |
| **Tools Used** | SwarmDecisionEngine |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md |
| **Governance Dependencies** | Constitution §3 (verification separate), ADR-001 |

---

### AutonomousSwarm (`core/orchestration/autonomous_swarm.py`)
| Field | Value |
|-------|-------|
| **Source** | Runtime |
| **Runtime** | ✅ Swarm Runtime |
| **Documentation** | ❌ |
| **Archetype** | Orchestrator (10 DNA) |
| **Capabilities** | Self-organizing agent collectives, spawn/coordinate/lifecycle, dynamic agent pools |
| **Inputs** | Swarm configuration, objectives, trace_id |
| **Outputs** | Swarm execution results, coordination outcomes |
| **Tools Used** | SwarmCoordinator, AgentManager |
| **SOP Dependencies** | AGENT_OPERATING_SYSTEM.md, AGENT_LIFECYCLE.md |
| **Governance Dependencies** | Constitution §5, ADR-006, ADR-011 |

---

## Documentation Agents (AGENT_REGISTRY.md - Not Implemented)

### Executive Layer

#### Program Director
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Strategic coordination, initiative prioritization, resource allocation, conflict resolution |
| **Inputs** | Organizational objectives, resource constraints, conflict reports |
| **Outputs** | Strategic decisions, resource allocations, priority rankings, conflict resolutions |
| **Tools Used** | (Requires: AgentManager, Scheduler, all domain agents) |
| **SOP Dependencies** | All SOPs (top of hierarchy) |
| **Governance Dependencies** | Constitution (all sections), Founder Intent, All ADRs |

#### Chief Architect
| Field | Value |
|-------|-------|
| **Source** | Documentation + Archetype |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ✅ Architect (5 DNA, 2 high-confidence: Quest Design, Spec Prompt) |
| **Capabilities** | Architecture reviews, standards enforcement, technical direction, design validation |
| **Inputs** | Design proposals, architecture decisions, standards violations |
| **Outputs** | Architecture decisions, standards compliance, technical direction |
| **Tools Used** | (Requires: OllamaClient, Knowledge Graph, Repository Intelligence) |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, CHANGE_MANAGEMENT.md, VERSIONING_STANDARD.md |
| **Governance Dependencies** | Constitution §3, §5, ADR-003, ADR-006, ADR-007 |

#### Product Strategist
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Product direction, requirement validation, market alignment |
| **Inputs** | Market data, user feedback, product proposals |
| **Outputs** | Product decisions, validated requirements, strategy documents |
| **Tools Used** | (Requires: Research tools, Analytics, Knowledge Graph) |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, CONTINUOUS_IMPROVEMENT_PROGRAM.md |
| **Governance Dependencies** | Constitution §5 (Product authority), Founder Intent |

---

### Engineering Layer

#### Backend Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Business logic, services, integrations, database interactions |
| **Inputs** | Service specifications, API contracts, data models |
| **Outputs** | Backend services, APIs, integrations |
| **Tools Used** | (Requires: BuilderAgent, Database tools, Integration tools) |
| **SOP Dependencies** | RELEASE_MANAGEMENT.md, CHANGE_MANAGEMENT.md |
| **Governance Dependencies** | Constitution §5, Chief Architect authority |

#### Frontend Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Interfaces, user journeys, interaction design, accessibility coordination |
| **Inputs** | UI/UX specifications, component requirements, design systems |
| **Outputs** | Frontend interfaces, components, user journeys |
| **Tools Used** | (Requires: BuilderAgent, Design tools, Accessibility tools) |
| **SOP Dependencies** | RELEASE_MANAGEMENT.md, VERSIONING_STANDARD.md |
| **Governance Dependencies** | Constitution §5, Chief Architect authority |

#### Database Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Schema design, relationship management, performance review |
| **Inputs** | Data requirements, access patterns, scaling needs |
| **Outputs** | Schema designs, migration plans, performance recommendations |
| **Tools Used** | (Requires: Database tools, LinearEngine, Migration tools) |
| **SOP Dependencies** | CHANGE_MANAGEMENT.md, BACKUP_STRATEGY.md |
| **Governance Dependencies** | Constitution §5, Chief Architect authority |

#### Integration Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | API integrations, service communication, data exchange validation |
| **Inputs** | Integration specifications, API contracts, vendor requirements |
| **Outputs** | Integration implementations, validation reports |
| **Tools Used** | (Requires: Integration stubs, CRM/Email/LinkedIn/Telephony clients) |
| **SOP Dependencies** | CHANGE_MANAGEMENT.md, vendor governance SOPs |
| **Governance Dependencies** | Constitution §5, §14 (Vendor governance), Chief Architect |

---

### Quality Layer

#### QA Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Testing, validation, defect discovery |
| **Inputs** | Test plans, code changes, requirements |
| **Outputs** | Test results, defect reports, validation status |
| **Tools Used** | (Requires: pytest, test frameworks, ReviewAgent) |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, RELEASE_MANAGEMENT.md |
| **Governance Dependencies** | Constitution §3 (No self-graded homework), ADR-001 |

#### Security Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Vulnerability analysis, threat modeling, dependency auditing |
| **Inputs** | Code, dependencies, architecture, threat models |
| **Outputs** | Security reports, vulnerability assessments, audit results |
| **Tools Used** | (Requires: Security scanners, dependency checkers, SAST tools) |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, SELF_HEALING_ARCHITECTURE.md |
| **Governance Dependencies** | Constitution §7 (Secrets never agent-touchable), §3 |

#### Performance Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Profiling, benchmarking, optimization recommendations |
| **Inputs** | Performance targets, code, infrastructure metrics |
| **Outputs** | Performance reports, benchmarks, optimization plans |
| **Tools Used** | (Requires: Profilers, benchmark tools, Monitoring) |
| **SOP Dependencies** | MONITORING_AND_ALERTING.md, CONTINUOUS_IMPROVEMENT_PROGRAM.md |
| **Governance Dependencies** | Constitution §5 |

#### Accessibility Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Standards validation, accessibility review |
| **Inputs** | UI components, design specs, accessibility standards |
| **Outputs** | Accessibility reports, compliance status, remediation plans |
| **Tools Used** | (Requires: A11y testing tools, design system) |
| **SOP Dependencies** | RELEASE_MANAGEMENT.md |
| **Governance Dependencies** | Constitution §5 |

---

### Knowledge Layer

#### Knowledge Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Knowledge graph maintenance, relationship preservation, context quality |
| **Inputs** | Artifacts, relationships, updates, queries |
| **Outputs** | Knowledge graph updates, context enrichment, retrieval quality |
| **Tools Used** | (Requires: Knowledge Graph, RAG, Repository Intelligence) |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, KNOWLEDGE_LIFECYCLE.MD |
| **Governance Dependencies** | Constitution §6 (Knowledge = infrastructure), ADR-004, ADR-005, ADR-007 |

#### Documentation Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Documentation generation, validation, synchronization |
| **Inputs** | Code, specs, changes, templates |
| **Outputs** | Generated docs, validation reports, sync status |
| **Tools Used** | (Requires: Doc generators, Repository Intelligence) |
| **SOP Dependencies** | AGENT_SOP_FRAMEWORK.md, ADR-008 (Documentation-Driven) |
| **Governance Dependencies** | Constitution: "Documentation is part of product" |

#### RAG Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Embedding management, vector indexing, retrieval optimization |
| **Inputs** | Documents, queries, feedback, performance metrics |
| **Outputs** | Updated indexes, retrieval results, quality metrics |
| **Tools Used** | (Requires: VectorStore, Embedding models, RAG_ARCHITECTURE.md) |
| **SOP Dependencies** | KNOWLEDGE_LIFECYCLE.MD, RAG_ARCHITECTURE.md |
| **Governance Dependencies** | Constitution §6, ADR-005 |

---

### Operations Layer

#### Release Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Releases, versioning, change validation |
| **Inputs** | Change requests, test results, approvals |
| **Outputs** | Release artifacts, version tags, release notes |
| **Tools Used** | (Requires: CI/CD, GitHub Actions, VERSIONING_STANDARD) |
| **SOP Dependencies** | RELEASE_MANAGEMENT.md, VERSIONING_STANDARD.md, CHANGE_MANAGEMENT.md |
| **Governance Dependencies** | Constitution §5 (Reversibility), ADR-009 |

#### Monitoring Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented (stubs in core/monitoring/) |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Monitoring, alerting, operational analysis |
| **Inputs** | Metrics, logs, traces, health checks |
| **Outputs** | Alerts, dashboards, operational reports |
| **Tools Used** | (Requires: Monitoring implementation, Prometheus/Grafana) |
| **SOP Dependencies** | MONITORING_AND_ALERTING.md, SELF_HEALING_ARCHITECTURE.md |
| **Governance Dependencies** | Constitution §5, §13 |

#### Backup Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Backup creation, recovery validation, archive management |
| **Inputs** | Backup schedules, data sources, retention policies |
| **Outputs** | Backup artifacts, recovery test results, archive indexes |
| **Tools Used** | (Requires: FileManager, S3Client, Database backup tools) |
| **SOP Dependencies** | BACKUP_STRATEGY.md, DISASTER_RECOVERY.md |
| **Governance Dependencies** | Constitution §4.6 (Portfolio isolation), §11 |

---

### Governance Layer

#### Governance Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation + Archetype |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ✅ Governance Director (3 DNA, all low confidence) |
| **Capabilities** | Policy validation, governance auditing, constitutional traceability |
| **Inputs** | Agent actions, policies, constitutional provisions |
| **Outputs** | Compliance reports, audit findings, enforcement actions |
| **Tools Used** | (Requires: Constitution parser, Policy engine, Audit logs) |
| **SOP Dependencies** | ENFORCEMENT.md, ESCALATION_FRAMEWORK.md, DELEGATION_MATRIX.md |
| **Governance Dependencies** | Constitution (supreme), All ADRs, Safety Code |

#### Audit Agent
| Field | Value |
|-------|-------|
| **Source** | Documentation |
| **Runtime** | ❌ Not implemented |
| **Documentation** | ✅ AGENT_REGISTRY.md |
| **Archetype** | ❌ |
| **Capabilities** | Activity reviews, compliance validation, historical analysis |
| **Inputs** | Audit scope, logs, agent actions, governance records |
| **Outputs** | Audit reports, compliance status, recommendations |
| **Tools Used** | (Requires: Logging, Audit trail, TicketHistory) |
| **SOP Dependencies** | ESCALATION_FRAMEWORK.md, ENFORCEMENT.md |
| **Governance Dependencies** | Constitution §3 (Legible authorship), ADR-001 (Independent verification) |

---

## Archetype Agents (DNA Only - No Runtime)

### Architect Archetype (5 DNA)
- **High Confidence**: Quest Design (100%), Spec Prompt (100%)
- **Low Confidence**: Agent Prompt 2.0 (21%), Agent Prompt v1.2 (21%), Craft Prompt (26%)
- **Mapped Runtime**: StrategyAgent → Architect
- **Capabilities** (from DNA): architecture, memory_management, planning, software_engineering, task_management, web_research
- **Tool Policy**: memory_access, web_access, code_access, execution_access, parallel_execution, knowledge_access = true
- **Collaborates With**: Architect, Builder, Optimizer

### Builder Archetype (30 DNA)
- **High Confidence (11)**: AI Studio vibe-coder, Builder Prompt, Claude Code 2.0, gemini-2.5-pro, gpt-4.1, gpt-4o, gpt-5, gpt-5-mini, gpt-5-agent-prompts, openai-codex-cli, gemini-cli, google-gemini-cli
- **Low Confidence (19)**: Chat Prompt, chat-titles, claude-4-sonnet, claude-sonnet-4, Mode_Classifier, nes-tab-completion, PlaygroundAction, Poke_p1-p6 (6), Prompt, Prompts, Sonnet 4.5, Tools Wave 11, Vibe_Prompt
- **Mapped Runtime**: BuilderAgent → Builder
- **Capabilities**: software_engineering, code_generation, file_operations
- **Tool Policy**: Full access (memory, web, code, execution, parallel, knowledge)
- **Collaborates With**: Architect, Builder, Optimizer

### Orchestrator Archetype (10 DNA)
- **High Confidence (4)**: Agent loop (100%), Default Prompt (100%), Enterprise Prompt (100%), System Prompt (100%)
- **Low Confidence (6)**: Agent Prompt v1.0, Agent Prompt, claude-4-sonnet-agent-prompts, Modules, Poke agent, System
- **Mapped Runtime**: SwarmCoordinator, TaskRouter, SwarmDecisionEngine, AutonomousSwarm → Orchestrator
- **Tool Policy**: memory_access, execution_access, coordination_required = true
- **Collaborates With**: Architect, Builder, Optimizer

### Reviewer Archetype (4 DNA - All 100%)
- **All High Confidence**: DocumentAction, ExplainAction, MessageAction, PreviewAction
- **Mapped Runtime**: ReviewAgent → Reviewer
- **Governance**: verification_required, evidence_required, audit_logging = true
- **Constraints**: always_follow_policy

### Planner Archetype (4 DNA)
- **High Confidence (2)**: phase_mode_prompts (100%), planning-mode (100%)
- **Low Confidence (2)**: Agent Prompt 2025-09-03 (27%), Fast Prompt (25%)
- **Runtime**: ❌ Not implemented

### Researcher Archetype (2 DNA)
- **High Confidence (1)**: DeepWiki Prompt (100%)
- **Low Confidence (1)**: Agent CLI Prompt 2025-08-07 (24%)
- **Runtime**: ❌ Not implemented

### Governance Director Archetype (3 DNA)
- **All Low Confidence**: MKT_006_IMAGE_GEN_PROMPTING (18%), Prompt Wave 11 (22%), Quest Action (22%)
- **Runtime**: ❌ Not implemented
- **Governance**: verification_required, audit_logging = true

### Optimizer Archetype
- **DNA Count**: 0 (referenced in DNA but no files)
- **Runtime**: ❌ Not implemented

---

## Summary Statistics

| Category | Agents | With Runtime | With Archetype | Hybrid | Gaps |
|----------|--------|--------------|----------------|--------|------|
| Runtime Core | 12 | 12 | 0 | 12 | 0 |
| Documentation Only | 19 | 0 | 19 | 0 | 19 missing runtime |
| Archetype Only | 3 | 0 | 3 | 0 | 3 missing runtime |
| Hybrid (Doc+Archetype) | 2 | 0 | 2 | 0 | 2 missing runtime |
| **Total** | **36** | **12** | **24** | **12** | **24 missing runtime** |