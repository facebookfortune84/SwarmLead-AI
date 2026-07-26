# SOP Registry

**Generated**: 2026-07-24  
**Source**: `docs/operations/`, `docs/governance/CONSTITUTION.md`, `docs/agents/AGENT_SOP_FRAMEWORK.md`, archetype DNA recovery_procedures  
**Classification Rules**: Active | Deprecated | Archive Candidate | Delete Candidate | Unknown

---

## Operations SOPs (`docs/operations/`)

| SOP Name | Role | Purpose | Coverage | Dependencies | Related Agents | Governance References | Improvement Required | Confidence |
|----------|------|---------|----------|--------------|----------------|----------------------|---------------------|------------|
| VERSIONING_STANDARD | Release Agent | Semantic versioning rules (MAJOR.MINOR.PATCH) | All releases | RELEASE_MANAGEMENT, CHANGE_MANAGEMENT | Release Agent, Program Director | Constitution §5: Product/code = agent-autonomous reversible | No - current standard | 0.95 |
| RELEASE_MANAGEMENT | Release Agent | Release process: Plan→Build→Review→Test→Approve→Release→Monitor→Document | All release categories (Major/Minor/Patch/Emergency) | VERSIONING_STANDARD, CHANGE_MANAGEMENT, BACKUP_STRATEGY | Release Agent, QA Agent, Security Agent, Governance Agent | Constitution §5: Autonomy by domain; §6: Emergency Intervention | Add automated gate checks | 0.90 |
| MONITORING_AND_ALERTING | Monitoring Agent | Operational visibility: app health, infrastructure, agent systems, knowledge systems | 4 monitoring areas, 4 alert levels | SELF_HEALING_ARCHITECTURE, DISASTER_RECOVERY | Monitoring Agent, all agent types | Constitution §5: Autonomy by domain; §13: Agent identity | Implement actual monitoring (currently stubs) | 0.70 |
| DISASTER_RECOVERY | Backup Agent | Restore organizational capability after catastrophic failure | 5 priority tiers, 6-step recovery process | BACKUP_STRATEGY, CONSTITUTION | Backup Agent, Governance Agent, Knowledge Agent | Constitution §4.7: Simulation-only fallback; §6: Emergency Intervention | Define specific RPO/RTO per tier | 0.80 |
| BACKUP_STRATEGY | Backup Agent | Protect organizational knowledge: source code, docs, governance, knowledge graphs, RAG, registries, configs, DBs | 8 backup categories, 3 types (full/incremental/governance/knowledge) | DISASTER_RECOVERY, CONSTITUTION | Backup Agent, Knowledge Agent | Constitution §4.6: Portfolio isolation; §11: Forward-defined sections | Test recovery regularly (principle: untested backup is not a backup) | 0.85 |
| CHANGE_MANAGEMENT | Program Director | Control organizational evolution: Standard/Significant/Major/Constitutional changes | 4 change categories, required docs, reviews | RELEASE_MANAGEMENT, CONSTITUTION | Program Director, Architect, Governance Agent, Security Agent | Constitution §3: Reversibility over speed; §5: Autonomy by domain | Automate change categorization | 0.80 |
| CONTINUOUS_IMPROVEMENT_PROGRAM | All Agents | Kaizen cycle: Observe→Analyze→Prioritize→Implement→Validate→Document→Preserve | 7 improvement sources, 6 success metrics | MONITORING_AND_ALERTING, tests, audits | All agents (especially QA, Performance, Security) | Constitution §12: Continuous Improvement Framework (ADR-012) | Integrate with test failure analysis | 0.85 |
| SELF_HEALING_ARCHITECTURE | All Agents | Auto-recovery: Detect→Diagnose→Attempt→Validate→Escalate | 6 targets, mandatory escalation rules | MONITORING_AND_ALERTING, DISASTER_RECOVERY | All agents, Repair Agent, Monitoring Agent | Constitution §5: Financial/legal = human-mediated; §6: Emergency protocol | Implement actual healing (currently stubs in core/monitoring/) | 0.65 |

---

## Governance SOPs (Constitution Sections)

| SOP Name | Role | Purpose | Coverage | Dependencies | Related Agents | Governance References | Improvement Required | Confidence |
|----------|------|---------|----------|--------------|----------------|----------------------|---------------------|------------|
| Human Oversight - Legal Officer | Program Director | Requesting user = legal officer of record for every company | All company creation | INFORMED_LIABILITY_CONSENT | Program Director, Governance Agent | Constitution §4.1: Legal Officer of Record | Codify in agent permissions | 0.95 |
| Informed Liability Consent | Program Director | Explicit consent before building (not just launch) | All projects | LEGAL_REVIEW_TRIGGERS | Program Director, Governance Agent | Constitution §4.2: Informed Liability Consent | Automate consent tracking | 0.90 |
| External Representation Authority | All Agents | Agents sign only within pre-approved templates | Contracts, commitments | DELEGATION_MATRIX | All agents with external comms | Constitution §4.3: External Representation | Template registry needed | 0.85 |
| Approval Friction Model | All Agents | Fast low-friction vs genuine review by domain | 6 risk domains | DELEGATION_MATRIX | All agents | Constitution §4.4: Approval Friction Model | Implement friction tiers in orchestrator | 0.80 |
| Real-Launch Identity Verification | Program Director | KYC at real-launch (entity registration, banking, payments) | Real-launch step | LEGAL_REVIEW_TRIGGERS | Program Director, Governance Agent | Constitution §4.5: Real-Launch Identity Verification | Integrate with formation services | 0.75 |
| Portfolio Isolation | All Agents | Structural data isolation between users' companies | All multi-tenant data | BACKUP_STRATEGY, DEPLOYMENT | All agents, Tenant Service | Constitution §4.6: Confidentiality & Portfolio Isolation | **Critical** - DB currently shared | 0.60 |
| Simulation-Only Fallback | All Agents | Build/simulate free; real-launch locked without consent | All projects | INFORMED_LIABILITY_CONSENT | All agents | Constitution §4.7: Simulation-Only Fallback | Technical enforcement needed | 0.70 |
| Autonomy by Domain | All Agents | 6 domains with differentiated autonomy postures | Product/code, Security, Financial, Legal, External comms, Simulation | DELEGATION_MATRIX, AGENT_REGISTRY | All agents | Constitution §5: Autonomy by Domain | **Critical** - enforce in orchestrator | 0.65 |
| Legal/Compliance Review Triggers | Governance Agent | OR-gate triggers: dollar value, regulated category, irreversibility, public commitment | All real-world actions | EXTERNAL_REPRESENTATION | Governance Agent, Legal Review (human) | Constitution §5.1: Mandatory Legal/Compliance Review | Set dollar thresholds (Phase 3) | 0.70 |
| Emergency Intervention | Program Director | Graceful wind-down for live companies | Emergency stop | CONSTITUTION | Program Director, all agents | Constitution §6: Emergency Intervention Protocol | Define "graceful" technically | 0.75 |
| Monetary Transaction Rules | Payment Agent | No standing spend; human approval per $; allowlisted counterparties; dual-rail; audit logging | All monetary transactions | PAYMENT_SERVICE, STRIPE | Payment Agent, Governance Agent | Constitution §12: Monetary Transaction Rules | Implement session caps, allowlists | 0.65 |
| Agent Identity & Permissions | All Agents | Unique non-shared identity; least privilege; scoped revocable credentials; explicit allowlists | All agent operations | AGENT_REGISTRY, ORCHESTRATION | All agents | Constitution §13: Agent Identity & Permissions | **Critical** - per-role allowlists (Phase 2) | 0.60 |
| Third-Party Vendor Governance | Governance Agent | Security/liability review for all vendors; periodic reassessment; fail-closed | All external dependencies | INTEGRATIONS | Governance Agent, Security Agent | Constitution §14: Third-Party Protocol & Vendor Governance | Vendor registry needed | 0.70 |
| Licensed Service Boundaries | All Agents | Genesis prepares/drafts/routes; never performs licensed functions | 8 licensed tasks | EXTERNAL_REPRESENTATION | All agents, Legal Review (human) | Constitution §10: Licensed Third-Party Service Boundaries | Document in agent SOPs | 0.80 |

---

## Agent SOP Framework

| SOP Name | Role | Purpose | Coverage | Dependencies | Related Agents | Governance References | Improvement Required | Confidence |
|----------|------|---------|----------|--------------|----------------|----------------------|---------------------|------------|
| AGENT_SOP_FRAMEWORK | All Agents | Standard structure for all agent SOPs: Purpose, Authority, Responsibilities, Inputs, Outputs, Escalation, Success Metrics, Governance Refs | All agent SOPs | AGENT_REGISTRY, CONSTITUTION | All agents | Constitution §3: Legible authorship; §5: Autonomy by domain | Create per-agent SOPs from this template | 0.90 |

---

## Archetype DNA Recovery Procedures (SOPs embedded in DNA)

| SOP Name | Role | Purpose | Coverage | Dependencies | Related Agents | Governance References | Improvement Required | Confidence |
|----------|------|---------|----------|--------------|----------------|----------------------|---------------------|------------|
| expand_context | Architect, Builder, Orchestrator, Planner, Researcher | Recovery: expand context when stuck | All DNA files with recovery_procedures | memory_access, web_access | All agents | DNA governance: verification_required, evidence_required | Standardize across archetypes | 0.80 |
| (various per archetype) | Per Archetype | Archetype-specific recovery | Per DNA file | Per archetype tool_policy | Per archetype | DNA governance field | Consolidate into runtime recovery | 0.70 |

---

## Summary Statistics

| Category | Count | Active | Needs Implementation | Critical Gap |
|----------|-------|--------|---------------------|--------------|
| Operations | 8 | 8 | 2 (monitoring, self-healing stubs) | Monitoring implementation |
| Governance (Constitution) | 14 | 0 (not codified) | 14 | Portfolio isolation, Autonomy enforcement, Agent permissions |
| Agent Framework | 1 | 0 (template only) | 33 (per-agent SOPs needed) | Per-agent SOP creation |
| DNA Recovery | 8+ | 0 (not in runtime) | 8+ | Runtime integration |
| **TOTAL** | **31+** | **8** | **23+** | **Portfolio isolation, Agent permissions, Monitoring** |

---

## Notes

- **Active** = Documented and referenced in operations
- **Needs Implementation** = Documented but not enforced in code (stubs, missing logic)
- **Critical Gap** = Constitutional requirement with no technical enforcement
- The 14 Constitution SOPs are governance requirements that must be implemented in orchestration/agent permissions
- Portfolio isolation (§4.6) and Agent permissions (§13) are the highest-priority gaps
- Monitoring and self-healing have documentation but 0-byte implementation files in `core/monitoring/`