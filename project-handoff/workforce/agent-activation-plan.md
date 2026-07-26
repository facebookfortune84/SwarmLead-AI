# Agent Activation Plan

**Generated**: 2026-07-26  
**Purpose**: Determine how documented agents become runtime agents using existing archetype intelligence

---

## Activation State Classification

| State | Definition |
|-------|------------|
| **Active** | Runtime implementation exists and is used |
| **Archetype Ready** | High-confidence DNA exists, runtime mappable |
| **Archetype Partial** | Some high-confidence DNA, needs consolidation |
| **Doc Only** | Documented in AGENT_REGISTRY.md, no DNA |
| **Missing** | Neither runtime nor archetype exists |

---

## Documented Agents (33 from AGENT_REGISTRY.md)

### Executive Layer

| Agent | Current State | Runtime Exists? | Archetype Exists? | Missing Components | Activation Difficulty | Priority | Recommended Runtime Mapping |
|-------|---------------|-----------------|-------------------|-------------------|----------------------|----------|----------------------------|
| Program Director | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, permissions, activation logic | High | P0 (Critical) | New: `core/agents/executive/program_director.py` extending BaseAgent; maps to Orchestrator archetype |
| Chief Architect | Archetype Ready | ❌ | ✅ Architect (2 high-confidence DNA) | Runtime class, activation logic, permission allowlists | Medium | P0 | Map to StrategyAgent enhancement or new `core/agents/executive/chief_architect.py` using Architect DNA (Quest Design, Spec Prompt) |
| Product Strategist | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, activation logic | High | P1 | New: `core/agents/executive/product_strategist.py`; consider Planner archetype DNA |

### Engineering Layer

| Agent | Current State | Runtime Exists? | Archetype Exists? | Missing Components | Activation Difficulty | Priority | Recommended Runtime Mapping |
|-------|---------------|-----------------|-------------------|-------------------|----------------------|----------|----------------------------|
| Backend Agent | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, permissions | Medium | P1 | Extend BuilderAgent with Backend specialization; use Builder high-confidence DNA |
| Frontend Agent | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, permissions | Medium | P1 | Extend BuilderAgent with Frontend specialization; use Builder high-confidence DNA |
| Database Agent | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, permissions | Medium | P2 | New: `core/agents/engineering/database_agent.py`; could use Architect DNA for schema design |
| Integration Agent | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, permissions | Medium | P2 | Extend BuilderAgent with Integration specialization; use Builder DNA |

### Quality Layer

| Agent | Current State | Runtime Exists? | Archetype Exists? | Missing Components | Activation Difficulty | Priority | Recommended Runtime Mapping |
|-------|---------------|-----------------|-------------------|-------------------|----------------------|----------|----------------------------|
| QA Agent | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, test framework integration | Medium | P1 | New: `core/agents/quality/qa_agent.py`; could use Reviewer DNA pattern |
| Security Agent | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, security tooling | High | P0 | New: `core/agents/quality/security_agent.py`; needs security tool integration |
| Performance Agent | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, profiling tools | Medium | P2 | New: `core/agents/quality/performance_agent.py`; could use Orchestrator DNA for benchmarking coordination |
| Accessibility Agent | Doc Only | ❌ | ❌ | Runtime class, archetype DNA, a11y tooling | Medium | P2 | New: `core/agents/quality/accessibility_agent.py` |

### Knowledge Layer

| Agent | Current State | Runtime Exists? | Archetype Exists? | Missing Components | Activation Difficulty | Priority | Recommended Runtime Mapping |
|-------|---------------|-----------------|-------------------|-------------------|----------------------|----------|----------------------------|
| Knowledge Agent | Doc Only | ❌ | ❌ | Runtime class, Knowledge Graph integration, RAG integration | High | P1 | New: `core/agents/knowledge/knowledge_agent.py`; implements ADR-004, ADR-005 |
| Documentation Agent | Doc Only | ❌ | ❌ | Runtime class, doc generation pipeline, sync logic | Medium | P1 | New: `core/agents/knowledge/documentation_agent.py`; implements ADR-008 |
| RAG Agent | Doc Only | ❌ | ❌ | Runtime class, embedding pipeline, vector index management | High | P1 | New: `core/agents/knowledge/rag_agent.py`; implements RAG_ARCHITECTURE.md |

### Operations Layer

| Agent | Current State | Runtime Exists? | Archetype Exists? | Missing Components | Activation Difficulty | Priority | Recommended Runtime Mapping |
|-------|---------------|-----------------|-------------------|-------------------|----------------------|----------|----------------------------|
| Release Agent | Doc Only | ❌ | ❌ | Runtime class, release pipeline integration, versioning | Medium | P1 | New: `core/agents/operations/release_agent.py`; uses VERSIONING_STANDARD.md, RELEASE_MANAGEMENT.md |
| Monitoring Agent | Doc Only | ❌ | ❌ | Runtime class, monitoring implementation (stubs exist), alerting | High | P0 | New: `core/agents/operations/monitoring_agent.py`; implements MONITORING_AND_ALERTING.md, SELF_HEALING_ARCHITECTURE.md |
| Backup Agent | Doc Only | ❌ | ❌ | Runtime class, backup orchestration, recovery validation | Medium | P1 | New: `core/agents/operations/backup_agent.py`; implements BACKUP_STRATEGY.md, DISASTER_RECOVERY.md |

### Governance Layer

| Agent | Current State | Runtime Exists? | Archetype Exists? | Missing Components | Activation Difficulty | Priority | Recommended Runtime Mapping |
|-------|---------------|-----------------|-------------------|-------------------|----------------------|----------|----------------------------|
| Governance Agent | Archetype Partial | ❌ | ✅ Governance Director (3 DNA, all low confidence) | Runtime class, high-confidence DNA consolidation, constitutional enforcement engine | High | P0 | New: `core/agents/governance/governance_agent.py`; consolidate Governance Director DNA; enforce Constitution §13 |
| Audit Agent | Doc Only | ❌ | ❌ | Runtime class, audit logging integration, compliance checks | High | P0 | New: `core/agents/governance/audit_agent.py`; implements Constitution §3, §13; independent verification |

---

## Runtime Agents (12 Implemented)

| Agent | Current State | Activation Status | Notes |
|-------|---------------|-------------------|-------|
| BaseAgent | Active | ✅ Base class | Abstract - not directly instantiable |
| StrategyAgent | Active | ✅ | Maps to Architect archetype (hybrid) |
| OutreachAgent | Active | ✅ | No archetype mapping - gap |
| BuilderAgent | Active | ✅ | Maps to Builder archetype (hybrid) |
| RepairAgent | Active | ✅ | No archetype mapping - gap |
| ReviewAgent | Active | ✅ | Maps to Reviewer archetype (hybrid) |
| AgentManager | Active | ✅ | Orchestration role |
| TaskRouter | Active | ✅ | Maps to Orchestrator archetype (hybrid) |
| Scheduler | Active | ✅ | No archetype mapping |
| SwarmCoordinator | Active | ✅ | Maps to Orchestrator archetype (hybrid) |
| SwarmDecisionEngine | Active | ✅ | Maps to Orchestrator archetype (hybrid) |
| SwarmEvaluator | Active | ✅ | No archetype mapping |
| AutonomousSwarm | Active | ✅ | Maps to Orchestrator archetype (hybrid) |

---

## Archetype Agents (8 Types, 64 DNA Files)

| Archetype | DNA Count | High Confidence (100%) | Runtime Mapped? | Activation Plan |
|-----------|-----------|------------------------|-----------------|-----------------|
| Architect | 5 | 2 (Quest Design, Spec Prompt) | ✅ StrategyAgent | Consolidate 2 high-confidence into single Architect runtime |
| Builder | 30 | 11 | ✅ BuilderAgent | Consolidate 11 high-confidence into BuilderAgent prompt config |
| Orchestrator | 10 | 4 (Agent loop, Default, Enterprise, System Prompt) | ✅ 4 runtime agents | Consolidate 4 high-confidence into Orchestrator base config |
| Reviewer | 4 | 4 (all) | ✅ ReviewAgent | Use all 4 as action-specific prompts for ReviewAgent |
| Planner | 4 | 2 (phase_mode, planning-mode) | ❌ | **Create PlannerAgent** using 2 high-confidence DNA |
| Researcher | 2 | 1 (DeepWiki) | ❌ | **Create ResearcherAgent** using DeepWiki DNA |
| Governance Director | 3 | 0 | ❌ | **Create GovernanceAgent** - consolidate 3 low-confidence DNA |
| Optimizer | 0 | 0 | ❌ | Referenced in DNA but no files - investigate |

---

## Activation Priority Matrix

| Priority | Agents | Rationale |
|----------|--------|-----------|
| **P0 - Constitutional** | Governance Agent, Audit Agent, Monitoring Agent, Security Agent | Constitution §13 (Agent Identity), §3 (No self-graded), §5 (Autonomy), §4.6 (Portfolio isolation) require enforcement |
| **P1 - Core Capability** | Program Director, Chief Architect, Backend/Frontend/Database Agents, QA Agent, Knowledge/RAG/Documentation Agents, Release/Backup Agents | Required for documented architecture to function |
| **P2 - Enhancement** | Product Strategist, Integration Agent, Performance/Accessibility Agents, Planner/Researcher Agents | Valuable but not blocking |

---

## Missing Runtime Implementations (24 agents)

| Category | Count | Agents |
|----------|-------|--------|
| Executive | 3 | Program Director, Chief Architect, Product Strategist |
| Engineering | 4 | Backend, Frontend, Database, Integration |
| Quality | 4 | QA, Security, Performance, Accessibility |
| Knowledge | 3 | Knowledge, Documentation, RAG |
| Operations | 3 | Release, Monitoring, Backup |
| Governance | 2 | Governance, Audit |
| Archetype-Only | 3 | Planner, Researcher, Governance Director, Optimizer (4 total, Optimizer has no DNA) |

---

## Recommended Activation Sequence

### Phase 1: Constitutional Enforcement (P0)
1. **GovernanceAgent** - Consolidate Governance Director DNA, implement Constitution enforcement engine
2. **AuditAgent** - Independent verification, constitutional audit logging
3. **MonitoringAgent** - Implement monitoring stubs, enable SELF_HEALING_ARCHITECTURE
4. **SecurityAgent** - Vulnerability scanning, dependency auditing, threat modeling

### Phase 2: Core Architecture (P0-P1)
5. **ProgramDirector** - Top of hierarchy, strategic coordination
6. **ChiefArchitect** - Enhance StrategyAgent with Architect DNA (Quest Design, Spec Prompt)
7. **KnowledgeAgent** - ADR-004/005 implementation, Knowledge Graph
8. **RAGAgent** - Embedding management, vector indexing (RAG_ARCHITECTURE.md)
9. **DocumentationAgent** - ADR-008 compliance, doc generation/sync

### Phase 3: Engineering & Quality (P1)
10. **BackendAgent** / **FrontendAgent** - BuilderAgent specializations
11. **DatabaseAgent** - Schema design, migration management
12. **QAAgent** - Test orchestration, validation (Reviewer DNA pattern)
13. **ReleaseAgent** / **BackupAgent** - Operations SOPs

### Phase 4: Archetype Activations (P1-P2)
14. **PlannerAgent** - Use phase_mode_prompts + planning-mode DNA
15. **ResearcherAgent** - Use DeepWiki Prompt DNA
16. **IntegrationAgent** - BuilderAgent specialization
17. **PerformanceAgent** / **AccessibilityAgent** - Quality specializations

### Phase 5: Optimizer (Investigation)
18. **OptimizerAgent** - Investigate why referenced in DNA but no files exist

---

## Activation Difficulty Scoring

| Difficulty | Criteria | Examples |
|------------|----------|----------|
| **Low** | High-confidence DNA exists, clear runtime pattern, minimal new infrastructure | PlannerAgent, ResearcherAgent, ReviewAgent enhancements |
| **Medium** | Some DNA exists, needs new runtime class, clear responsibilities | BackendAgent, FrontendAgent, ReleaseAgent, BackupAgent |
| **High** | No DNA, complex infrastructure, constitutional enforcement | GovernanceAgent, AuditAgent, MonitoringAgent, SecurityAgent, KnowledgeAgent, RAGAgent |
| **Critical** | Constitutional mandate, cross-cutting, requires platform changes | ProgramDirector, ChiefArchitect, Portfolio isolation, Agent Identity (§13) |

---

## Key Blockers

1. **No Activation Mechanism**: AGENT_REGISTRY.md has no instantiation logic
2. **No Permission Allowlists**: Constitution §13 requires per-role tool/data allowlists (Phase 2)
3. **Portfolio Isolation**: Constitution §4.6 not implemented - agents lack tenant scoping
3. **Agent Identity**: Constitution §13 - unique non-shared identities, scoped credentials missing
4. **Archetype Consolidation**: 64 DNA files need consolidation into runtime configs
5. **Monitoring Stubs**: 0-byte files in `core/monitoring/` block SELF_HEALING_ARCHITECTURE