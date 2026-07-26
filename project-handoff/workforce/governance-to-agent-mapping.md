# Governance to Agent Mapping

**Generated**: 2026-07-26  
**Sources**: `docs/governance/CONSTITUTION.md`, `docs/adr/`, `docs/founder/`, `docs/governance/`, `docs/agents/AGENT_REGISTRY.md`, `docs/agents/AGENT_SOP_FRAMEWORK.md`, `docs/operations/`, `docs/knowledge/`

---

## Mapping Principle

Each governance artifact maps to agents that must:
1. **Enforce** it (active compliance checking)
2. **Reference** it (decision justification via self-citation)
3. **Report** on it (audit trail)

---

## Constitution → Agent Mapping (40KB, 532 lines)

### Section 1-2: Mission & Purpose
| Constitutional Provision | Primary Agent | Supporting Agents | Enforcement |
|--------------------------|---------------|-------------------|-------------|
| Mission: Turn request → launched company | Program Director | All execution agents | Strategic alignment review |
| Free/open-source swarm | Governance Agent | All agents | License scanning (CI) |
| Human-gated: every $, legal action, binding commitment | Payment Agent, Governance Agent, Legal Review (Human) | Program Director | Friction model + human gates |

### Section 3: Core Values (8 Values)

| Value | Constitutional Text | Applicable Agents | Verification Mechanism |
|-------|---------------------|-------------------|------------------------|
| **Legible authorship** | "Every commit, draft, filing, decision traces to a named agent role and, where required, a human approver. No anonymous or unattributable actions, ever." | **ALL AGENTS** | Audit Agent reviews logs for trace_id, agent_id, action_type |
| **Reversibility over speed** | "Between a faster irreversible action and a slower reversible one, Genesis defaults to reversible — unless a human has pre-approved the irreversible path." | All agents (Orchestrator gates) | TaskRouter: reversible-first routing; escalation for irreversible |
| **Escalate uncertainty** | "An agent unsure whether something is in-scope treats that uncertainty as a signal to escalate, not a problem to quietly solve." | All agents | Confidence scoring + SwarmDecisionEngine escalation |
| **Minimum viable autonomy** | "Agents get the least authority needed to do their job well; autonomy expands deliberately over time, never by default." | AgentManager, Orchestrator | Per-role permission allowlists (Constitution §13) |
| **No self-graded homework** | "No agent has final authority to approve its own output as safe, correct, or ready to launch. Verification is always structurally separate from generation." | **Builder↔Reviewer, Strategy↔QA, Orchestrator↔Evaluator** | ADR-001: structural separation enforced in workflows |
| **IP & licensing hygiene** | "No agent introduces code, dependencies, or assets with unclear or incompatible licensing — checked structurally (automated scanning), not trusted to judgment." | All agents (CI) | GitHub Actions: license scanning; Security Agent audit |
| **Secrets never agent-touchable** | "No agent handles credentials, API keys, banking credentials, or production secrets directly. Secret access is mediated by a non-AI system at all times." | **ALL AGENTS** | ConfigLoader, JWTHandler, AuthMiddleware mediate all secrets |
| **Open-source core, always** | "Core swarm logic, agent orchestration, and decision-making code must remain open-source and auditable. Closed third-party APIs acceptable, but swarm's own reasoning never a black box." | Governance Agent, Security Agent | Dependency audit; no closed-source core deps |

### Section 4: Human Oversight Philosophy

| Subsection | Provision | Primary Agent | Implementation |
|------------|-----------|---------------|----------------|
| **4.1 Legal Officer** | Requesting user = accountable legal officer | Program Director (tracks), Governance Agent (validates) | User consent registry |
| **4.2 Informed Liability Consent** | Explicit consent before building (not just launch) | Program Director, Governance Agent | Consent tracking system |
| **4.3 External Representation** | Agents sign only within pre-approved templates | All agents with external comms | Template registry + Governance Agent approval |
| **4.4 Approval Friction Model** | Fast (routine) vs Genuine review (legal/financial/launch) | Orchestrator (TaskRouter) | Friction tier gating |
| **4.5 Real-Launch Identity Verification** | KYC at real-launch (entity registration, banking, payments) | Program Director, Governance Agent | Formation service integration |
| **4.6 Portfolio Isolation** | **Structural data isolation between users' companies** | **ALL AGENTS** - **CRITICAL GAP** | Tenant-scoped memory, DB, storage |
| **4.7 Simulation-Only Fallback** | Decline consent → simulation mode (real-launch locked) | All agents respect mode flag | Mode flag in context |

### Section 5: Autonomy by Domain (6 Domains)

| Domain | Default Posture | Primary Agents | Orchestrator Enforcement |
|--------|----------------|----------------|-------------------------|
| **Product/code build** | Agent-autonomous within reversible boundaries | BuilderAgent, RepairAgent, StrategyAgent, OutreachAgent, ReviewAgent | Reversible-only gating |
| **Security & secrets** | Human-mediated, always — no agent exception | **ALL AGENTS** (via ConfigLoader/JWTHandler) | Non-AI secret mediation |
| **Financial transactions** | **Every $ requires human approval — no autonomous spending** | Payment Agent, Governance Agent, Human Review | Session caps, allowlists, dual-rail |
| **Legal entity & contracts** | Human approval required, gated by §4.5 identity verification | Governance Agent, Program Director, Legal Review (Human) | Template gating + human review |
| **External-facing communication** | AI-drafted, human-reviewed before publish | OutreachAgent, Notification Agent, all external comms | Human review gate |
| **Company concept/simulation** | Fully agent-autonomous — free to build/iterate | StrategyAgent, BuilderAgent, PlannerAgent, ResearcherAgent | No gate until real-world action |

#### Section 5.1: Mandatory Legal/Compliance Review Triggers
| Trigger | Affected Agents | Escalation Target |
|---------|----------------|-------------------|
| Dollar-value (single transaction or cumulative) | Payment Agent, all agents initiating spend | Governance Agent → Human Legal Review |
| Regulated category (healthcare, finance, legal, minors, etc.) | StrategyAgent, BuilderAgent, Integration Agent | Governance Agent → Human Legal Review |
| Irreversibility (entity registration, signed contracts, published terms, first live transaction) | All agents attempting real-world actions | Governance Agent → Human Legal Review |
| Public commitment (launch announcement, marketing claims) | OutreachAgent, Documentation Agent | Governance Agent → Human Review |

### Section 6: Emergency Intervention Protocol
| Provision | Primary Agent | Implementation |
|-----------|---------------|----------------|
| Graceful wind-down for live companies | Program Director, All Agents | Emergency stop flag; honor existing commitments |
| Full immediate stop = last resort | Program Director | Emergency override |

### Section 7: Scale & Portfolio Governance
| Provision | Primary Agent | Implementation |
|-----------|---------------|----------------|
| No hard cap on companies in review | Program Director | Queue management |
| Review quality over throughput | Governance Agent, Legal Review | Quality gates |

### Section 8: Success Metrics
| Metric | Accountable Agent(s) |
|--------|---------------------|
| Concept-to-launch cycle time | Program Director, all execution agents |
| % launched companies requiring no emergency intervention in 90 days | Governance Agent, Audit Agent |
| Governance health: % agent actions with clear attribution | **All Agents** (Constitution §3) |
| Near-misses caught before real-world impact | Governance Agent, Audit Agent |
| Trust trajectory: autonomy expansion without near-miss increase | Program Director, Governance Agent |
| Accessibility: companies launched by users who couldn't afford traditional services | Program Director, Product Strategist |

### Section 9: Monetization & Revenue Mechanics
| Layer | Agent Impact |
|-------|--------------|
| Self-host (free) | All agents runnable locally |
| Genesis Cloud subscription | Program Director tracks |
| Usage overage ($1.50/agent-compute-hour) | All agents (metered via UsageEvent) |
| Real-Launch Facilitation Fee ($299) | Payment Agent, Program Director |
| Revenue Share (5%, capped 2x, 7yr) | Payment Agent, Governance Agent |

### Section 12: Monetary Transaction Rules (CRITICAL - NOT IMPLEMENTED)
| Rule | Agents | Status |
|------|--------|--------|
| **1. No standing spend authority** | Payment Agent, all agents | ❌ Session-based only |
| **2. Every $ requires human approval** | Payment Agent, Governance Agent | ❌ Friction model needed |
| **3. Allowlisted counterparties only** | Payment Agent, Integration Agent | ❌ Allowlist missing |
| **4. Dual-rail model** (card for customer payments, agentic/stablecoin for M2M) | Payment Agent | ❌ Not implemented |
| **5. Tamper-evident audit logging** | Payment Agent, Audit Agent | ❌ TicketHistory only |
| **6. Reconciliation as escalation trigger** | Payment Agent, Governance Agent | ❌ Not implemented |
| **7. Disputes route to licensed processor** | Payment Agent | ✅ Stripe handles |

### Section 13: Agent Identity & Permissions (CRITICAL - PHASE 2)
| Requirement | Agents | Status |
|-------------|--------|--------|
| Unique, non-shared identity per agent | **ALL AGENTS** | ❌ Not implemented |
| Least-privilege by default | **ALL AGENTS** | ❌ Not implemented |
| Scoped, revocable credentials (per-task/session) | **ALL AGENTS** | ❌ Not implemented |
| Explicit tool/API allowlists per role | **ALL AGENTS** | ❌ Not implemented |
| New agent roles require review before deployment | Program Director, Governance Agent | ❌ Not implemented |

### Section 14: Third-Party Protocol & Vendor Governance
| Requirement | Agents | Status |
|-------------|--------|--------|
| Security/liability review for new vendors | Governance Agent, Security Agent | ❌ Vendor registry missing |
| Periodic reassessment | Governance Agent | ❌ Not implemented |
| Fail-closed for Financial/Legal domains | Payment Agent, Governance Agent | ❌ Not implemented |

---

## ADR Mapping (12 ADRs)

| ADR | Title | Constitutional Link | Primary Enforcing Agent(s) |
|-----|-------|---------------------|---------------------------|
| **ADR-001** | No Self-Graded Homework | §3 Value #5 | Builder↔Reviewer, Strategy↔QA, Orchestrator↔Evaluator |
| **ADR-002** | Founder Intent Preservation | Founder Intent > Constitution | All agents (hierarchy) |
| **ADR-003** | Constitution-First Governance | Constitution = supreme | Governance Agent, All agents |
| **ADR-004** | Organizational Memory System | §6 (Knowledge = infrastructure) | Knowledge Agent, Documentation Agent, RAG Agent |
| **ADR-005** | Knowledge Graph Architecture | §6, ADR-004 | Knowledge Agent, RAG Agent |
| **ADR-006** | Agent Organization Architecture | §13, AGENT_REGISTRY.md | Program Director, AgentManager |
| **ADR-007** | Repository Intelligence Layers | §6, §3 (Discoverability) | Knowledge Agent, Documentation Agent |
| **ADR-008** | Documentation-Driven Development | "Documentation is part of product" | All agents |
| **ADR-009** | Single-Machine-First Infrastructure | §3 (Reversibility), §7 (Accessibility) | All agents (local-first config) |
| **ADR-010** | Open-Source-First Strategy | §3 Value #8 | Governance Agent, Security Agent |
| **ADR-011** | Human Authority Preservation | §4, §5, §12 | Program Director, Governance Agent |
| **ADR-012** | Continuous Improvement Framework | §12 | All agents (AdaptiveWeights, CI/CD) |

---

## Founder Intent Mapping (13 Documents)

| Document | Key Principle | Agent Obligation |
|----------|---------------|------------------|
| **vision.md** | Democratize enterprise capabilities | All agents: accessibility-first |
| **mission.md** | Amplify human capability, not replace | All agents: human-in-the-loop |
| **engineering_principles.md** | No placeholders, no debt by neglect, docs=product, testing=evidence, reversibility, discoverability, knowledge=infrastructure | All agents |
| **founder_intent.md** | Detailed vision/constraints | All agents (highest priority per Genesis Architect) |
| **founder_story.md** | Origin narrative | Documentation Agent |
| **philosophy.md** | (Empty - Archive Candidate) | N/A |
| **product_principles.md** | Product design principles | Product Strategist, BuilderAgent |
| **roadmap_end_state.md** | Target architecture | Chief Architect, Program Director |
| **success_definition.md** | Success metrics | Program Director, Governance Agent |
| **north_star.md** | Guiding metric | All agents |
| **customer_promises.md** | Commitments to users | All agents |
| **anti_patterns.md** | Explicit anti-patterns to avoid | All agents |
| **future_of_genesis.md** | Long-term evolution | Program Director, Chief Architect |

**Hierarchy** (per Genesis Architect): Founder Intent → Constitution → Safety Code → Governance → ADRs → Knowledge Systems → Repository Intelligence → Agent Organization → Operations → Implementation

---

## Governance Documents Mapping (7 Docs)

| Document | Purpose | Primary Enforcing Agent(s) |
|----------|---------|---------------------------|
| **CONSTITUTION.md** | Supreme law | Governance Agent (primary), All agents |
| **AGENT_RIGHTS.md** | Agent entitlements | Governance Agent, Audit Agent |
| **AGENT_RESPONSIBILITIES.md** | Agent duties | Governance Agent, All agents |
| **DELEGATION_MATRIX.md** | Authority delegation | Program Director, Governance Agent |
| **ENFORCEMENT.md** | Enforcement mechanisms | Governance Agent, Audit Agent |
| **ESCALATION_FRAMEWORK.md** | Escalation paths | All agents (must escalate per framework) |
| **SAFETY_CODE.md** | Safety protocols | Governance Agent, Security Agent |

---

## Knowledge System Mapping (6 Docs)

| Document | Purpose | Implementing Agent(s) |
|----------|---------|----------------------|
| **REPOSITORY_INTELLIGENCE_SPEC.md** | Discovery, classification, relationships, change awareness, RAG support | Knowledge Agent, Documentation Agent |
| **KNOWLEDGE_GRAPH_SPEC.md** | Nodes, edges, scope (code/doc/governance/agent/operational/knowledge) | Knowledge Agent, RAG Agent |
| **NODE_TYPES.md** | Node type definitions | Knowledge Agent |
| **EDGE_TYPES.md** | Relationship type definitions | Knowledge Agent |
| **KNOWLEDGE_LIFECYCLE.MD** | Creation, validation, deprecation | Knowledge Agent, Documentation Agent |
| **RAG_ARCHITECTURE.md** | Retrieval-augmented generation architecture | Knowledge Agent, RAG Agent |

---

## Operations SOPs Mapping (8 Docs)

| SOP | Purpose | Enforcing Agent(s) |
|-----|---------|-------------------|
| **VERSIONING_STANDARD.md** | Semantic versioning | Release Agent |
| **RELEASE_MANAGEMENT.md** | Release process (7 gates, workflow) | Release Agent, QA Agent, Security Agent, Governance Agent |
| **MONITORING_AND_ALERTING.md** | 4 areas, 4 alert levels | Monitoring Agent |
| **DISASTER_RECOVERY.md** | 5 priorities, 6-step process | Backup Agent, Governance Agent, Knowledge Agent |
| **BACKUP_STRATEGY.md** | 8 categories, 3 types | Backup Agent, Knowledge Agent |
| **CHANGE_MANAGEMENT.md** | 4 categories, docs, reviews | Program Director, Architect, Governance Agent, Security Agent |
| **CONTINUOUS_IMPROVEMENT_PROGRAM.md** | 7-step cycle, 6 sources, 6 metrics | All agents (especially QA, Performance, Security) |
| **SELF_HEALING_ARCHITECTURE.md** | 6 targets, hierarchy, mandatory escalation | All agents, Repair Agent, Monitoring Agent |

---

## Agent SOP Framework

| Framework Section | Applies To | Status |
|-------------------|------------|--------|
| Purpose | All 33 documented agents | Template only |
| Authority | All agents | Not codified per role |
| Responsibilities | All agents | Not codified per role |
| Inputs | All agents | Not codified per role |
| Outputs | All agents | Not codified per role |
| Escalation Conditions | All agents | Not codified per role |
| Success Metrics | All agents | Not codified per role |
| Governance References | All agents | Constitution, Delegation Matrix |

**Gap**: 33 agents × 7 SOP sections = **231 per-agent SOPs needed**, 0 created.

---

## Compliance Coverage Matrix

| Governance Layer | Total Artifacts | Mapped to Agents | Enforced in Runtime | Gaps |
|-----------------|-----------------|------------------|---------------------|------|
| Founder Intent | 13 | 13 | 0 (hierarchy only) | No runtime enforcement |
| Constitution | 1 (532 lines) | 33 | 0 (values only) | §4.6, §5, §12, §13, §14 not enforced |
| ADRs | 12 | 12 | Partial (ADR-001, ADR-003) | Most not enforced |
| Governance Docs | 7 | 7 | 0 | No runtime enforcement |
| Knowledge | 6 | 3 | 0 | Knowledge/RAG/Documentation agents not implemented |
| Operations | 8 | 0 | 2 (Monitoring, Self-Healing stubs) | Monitoring/Backup/Release agents not implemented |
| Agent Framework | 1 | 33 | 0 | 231 per-agent SOPs needed |
| **TOTAL** | **54** | **68** | **2** | **Critical: Constitution §4.6, §5, §12, §13, §14** |

---

## Critical Governance Gaps by Agent

| Agent | Missing Governance Enforcement |
|-------|-------------------------------|
| **ALL AGENTS** | §4.6 Portfolio isolation (tenant-scoped memory/DB/storage), §5 Domain autonomy gating, §13 Agent identity/permissions, §13 Least-privilege allowlists |
| **Program Director** | §4.1 Legal officer tracking, §4.2 Consent registry, §4.5 Identity verification integration, §6 Emergency protocol |
| **Governance Agent** | Constitution enforcement engine, §4.3 Template registry, §4.4 Friction tiers, §5.1 Trigger evaluation, §12 Monetary rules, §13 Allowlists, §14 Vendor registry |
| **Payment Agent** | §12 Rules 1-7 (session caps, human approval, allowlists, dual-rail, audit logging, reconciliation, dispute routing) |
| **Monitoring Agent** | MONITORING_AND_ALERTING.md implementation, SELF_HEALING_ARCHITECTURE data source |
| **Audit Agent** | §3 Legible authorship verification, ESCALATION_FRAMEWORK.md compliance |
| **Security Agent** | IP hygiene scanning, §14 Vendor governance, §3 Value #7 IP hygiene |
| **Deployment Agent** | §4.5 Identity verification, §4.6 Portfolio isolation (containers), §10 Licensed boundaries |
| **Backup Agent** | BACKUP_STRATEGY.md, DISASTER_RECOVERY.md implementation |
| **Release Agent** | VERSIONING_STANDARD, RELEASE_MANAGEMENT, CHANGE_MANAGEMENT enforcement |
| **All Agents** | §4.7 Simulation-only mode flag, §13 Scoped credentials, §13 Tool allowlists |

---

## Governance Enforcement Priority

| Priority | Governance Area | Agents Required | Blockers |
|----------|-----------------|-----------------|----------|
| **P0** | §4.6 Portfolio Isolation | All agents + Infrastructure | Tenant-scoped DB, memory, storage |
| **P0** | §5 Domain Autonomy | Orchestrator + All agents | Domain gating in TaskRouter |
| **P0** | §12 Monetary Rules | Payment Agent + Governance Agent | Session caps, allowlists, dual-rail, audit logging |
| **P0** | §13 Agent Identity | All agents + Auth System | Unique IDs, scoped credentials, allowlists |
| **P0** | §4.6 Portfolio Isolation | Deployment Agent + Tenant Service | Container-per-tenant, DB isolation |
| **P1** | §4.4 Friction Model | TaskRouter + Orchestrator | Fast vs genuine review tiers |
| **P1** | §4.3 Template Registry | Governance Agent | External representation allowlists |
| **P1** | §14 Vendor Governance | Governance Agent + Security Agent | Vendor registry + review process |
| **P1** | §13 Agent Identity | All agents + Auth System | Phase 2 implementation |
| **P2** | Operations SOPs | Monitoring, Backup, Release agents | Agent implementations |

---

## Notes

- **2 of 54 governance artifacts** have any runtime enforcement (ADR-001 structural separation, ADR-003 constitutional hierarchy)
- **33 documented agents** have **0** per-agent SOPs created
- **Constitution §4.6, §5, §12, §13, §14** are the highest-impact unimplemented provisions
- **Agent identity (§13)** and **Portfolio isolation (§4.6)** are architectural prerequisites for most other governance
- **Monetary rules (§12)** have **zero** runtime enforcement despite being "every $ requires human approval"
- **Founder Intent** hierarchy established but no runtime enforcement mechanism