# Prompt Registry

**Generated**: 2026-07-24  
**Source**: `asset_processor/output/archetypes/`, `core/prompts/`, `docs/agents/`, `docs/adr/`, `docs/governance/`  
**Classification Rules**: Active | Deprecated | Archive Candidate | Delete Candidate | Unknown

---

## Archetype DNA Prompts (64 prompts from `asset_processor/output/archetypes/`)

Each DNA file contains structured prompt components: identity, mission, reasoning_framework, capabilities, tool_policy, memory_policy, communication_policy, governance, constraints, recovery_procedures, output_contract.

### Architect Prompts (5)

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| Agent Prompt 2.0 | Architect | System Prompt | Assist software development with architecture, planning, research, memory management | code_access, web_access, memory_access, execution_access | Structured output (markdown, code_refs), citations | verification_required=false, evidence_required=true, anti_hallucination=true | No self-graded homework (ADR-001); human-gated legal/financial | Yes - merge into optimized | 0.85 |
| Agent Prompt v1.2 | Architect | System Prompt | Assist software development (v1.2) | code_access, web_access, memory_access, execution_access | Structured output (markdown, code_refs) | verification_required=false, evidence_required=true, anti_hallucination=true | No self-graded homework; human oversight | Yes - merge into optimized | 0.85 |
| Craft Prompt | Architect | Specialized Prompt | Craft-oriented software development | code_access, web_access, memory_access | Structured output | evidence_required=true, anti_hallucination=true | Human-gated irreversible actions | Yes - merge into optimized | 0.80 |
| Quest Design | Architect | Specialized Prompt | Quest/design-focused architecture | code_access, web_access, memory_access, execution_access | Structured output (markdown, code_refs) | verification_required=false, evidence_required=true, anti_hallucination=true | Constitution §5: Product/code build = agent-autonomous within reversible boundaries | **No - high confidence, retain** | 0.95 |
| Spec Prompt | Architect | Specialized Prompt | Specification-driven architecture | code_access, web_access, memory_access, execution_access | Structured output (markdown, code_refs) | verification_required=false, evidence_required=true, anti_hallucination=true | Constitution §5: Product/code build = agent-autonomous within reversible boundaries | **No - high confidence, retain** | 0.95 |

### Builder Prompts (30)

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| AI Studio vibe-coder | Builder | System Prompt | Vibe coding for AI Studio | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true | Agent-autonomous within reversible boundaries | **No - high confidence** | 0.95 |
| Builder Prompt | Builder | System Prompt | Core builder capabilities | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true | Agent-autonomous within reversible boundaries | **No - high confidence** | 0.95 |
| Chat Prompt | Builder | Specialized | Chat-oriented building | code_access, web_access | Structured output | evidence_required=true | Human-reviewed external comms | Yes - low confidence | 0.70 |
| chat-titles | Builder | Specialized | Chat title generation | code_access | Text output | minimal | Low-stakes automation | Yes - test artifact | 0.60 |
| Claude Code 2.0 | Builder | System Prompt | Claude Code 2.0 integration | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true, anti_hallucination=true | No self-graded homework | **No - high confidence** | 0.95 |
| claude-4-sonnet | Builder | System Prompt | Claude 4 Sonnet builder | code_access, web_access | Structured output | evidence_required=true | Human-gated legal/financial | Yes - low confidence | 0.70 |
| claude-sonnet-4 | Builder | System Prompt | Claude Sonnet 4 builder | code_access, web_access | Structured output | evidence_required=true | Human-gated legal/financial | Yes - low confidence | 0.70 |
| gemini-2.5-pro | Builder | System Prompt | Gemini 2.5 Pro builder | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true, anti_hallucination=true | Agent-autonomous reversible | **No - high confidence** | 0.95 |
| gemini-cli-system-prompt | Builder | System Prompt | Gemini CLI builder | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true | Agent-autonomous reversible | **No - high confidence** | 0.95 |
| google-gemini-cli-system-prompt | Builder | System Prompt | Google Gemini CLI builder | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true | Agent-autonomous reversible | **No - high confidence** | 0.95 |
| gpt-4.1 | Builder | System Prompt | GPT-4.1 builder | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true | Agent-autonomous reversible | **No - high confidence** | 0.95 |
| gpt-4o | Builder | System Prompt | GPT-4o builder | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true | Agent-autonomous reversible | **No - high confidence** | 0.95 |
| gpt-5-agent-prompts | Builder | System Prompt | GPT-5 agent prompts | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true | Agent-autonomous reversible | **No - high confidence** | 0.95 |
| gpt-5-mini | Builder | System Prompt | GPT-5 mini builder | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true | Agent-autonomous reversible | **No - high confidence** | 0.95 |
| gpt-5 | Builder | System Prompt | GPT-5 builder | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true | Agent-autonomous reversible | **No - high confidence** | 0.95 |
| Mode_Clasifier_Prompt | Builder | Specialized | Mode classification | code_access | Classification output | minimal | Low-stakes automation | Yes - test artifact | 0.60 |
| nes-tab-completion | Builder | Specialized | Tab completion | code_access | Completion output | minimal | Low-stakes automation | Yes - test artifact | 0.60 |
| openai-codex-cli-system-prompt-20250820 | Builder | System Prompt | OpenAI Codex CLI builder | code_access, web_access, memory_access, execution_access | Structured output | evidence_required=true, anti_hallucination=true | No self-graded homework | **No - high confidence** | 0.95 |
| PlaygroundAction | Builder | Specialized | Playground action | code_access | Action output | minimal | Low-stakes automation | Yes - test artifact | 0.60 |
| Poke_p1 through Poke_p6 (6) | Builder | Test Prompts | Poke test variants | code_access | Test output | minimal | Test artifacts | **Yes - archive** | 0.60 |
| Prompt | Builder | Generic | Generic builder prompt | code_access, web_access | Structured output | evidence_required=true | Agent-autonomous reversible | Yes - low confidence | 0.70 |
| Prompts | Builder | Collection | Multiple prompts | code_access, web_access | Structured output | evidence_required=true | Agent-autonomous reversible | Yes - low confidence | 0.70 |
| Sonnet 4.5 Prompt | Builder | System Prompt | Sonnet 4.5 builder | code_access, web_access | Structured output | evidence_required=true | Human-gated legal/financial | Yes - low confidence | 0.70 |
| Tools Wave 11 | Builder | Specialized | Tools wave 11 | code_access | Tool output | minimal | Low-stakes automation | Yes - test artifact | 0.60 |
| Vibe_Prompt | Builder | Specialized | Vibe coding | code_access, web_access | Structured output | evidence_required=true | Agent-autonomous reversible | Yes - low confidence | 0.70 |

### Governance Director Prompts (3)

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| MKT_006_IMAGE_GEN_PROMPTING | Governance Director | Specialized | Image generation governance | web_access, memory_access | Governance decisions | verification_required=true, audit_logging=true | Constitution §3: IP hygiene, §5: Legal = human approval | Yes - low confidence | 0.70 |
| Prompt Wave 11 | Governance Director | Specialized | Governance prompt wave 11 | web_access, memory_access | Governance decisions | verification_required=true, audit_logging=true | Constitution §3: IP hygiene, enforcement | Yes - low confidence | 0.70 |
| Quest Action | Governance Director | Specialized | Quest action governance | web_access, memory_access | Governance decisions | verification_required=true, audit_logging=true | Constitution §5: Legal = human approval | Yes - low confidence | 0.70 |

### Orchestrator Prompts (10)

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| Agent loop | Orchestrator | System Prompt | Agent loop orchestration | memory_access, execution_access, coordination_required | Orchestration decisions | coordination_required=true, collaborates_with=[Architect,Builder,Optimizer] | Constitution §5: Product/code = agent-autonomous reversible | **No - high confidence** | 0.95 |
| Agent Prompt v1.0 | Orchestrator | System Prompt | Orchestrator v1.0 | memory_access, execution_access | Orchestration decisions | coordination_required=true | Human-gated legal/financial | Yes - low confidence | 0.70 |
| Agent Prompt | Orchestrator | System Prompt | Generic orchestrator | memory_access, execution_access | Orchestration decisions | coordination_required=true | Human-gated legal/financial | Yes - low confidence | 0.70 |
| claude-4-sonnet-agent-prompts | Orchestrator | System Prompt | Claude 4 Sonnet agent prompts | memory_access, execution_access | Orchestration decisions | coordination_required=true | Human-gated legal/financial | Yes - low confidence | 0.70 |
| Default Prompt | Orchestrator | System Prompt | Default orchestrator | memory_access, execution_access, coordination_required | Orchestration decisions | coordination_required=true, collaborates_with=[Architect,Builder,Optimizer] | Constitution §5: Product/code = agent-autonomous reversible | **No - high confidence** | 0.95 |
| Enterprise Prompt | Orchestrator | System Prompt | Enterprise orchestration | memory_access, execution_access, coordination_required | Orchestration decisions | coordination_required=true, audit_logging=true | Constitution §4: Human oversight, §5: Legal = human approval | **No - high confidence** | 0.95 |
| Modules | Orchestrator | System Prompt | Modules orchestration | memory_access, execution_access, coordination_required | Orchestration decisions | coordination_required=true, collaborates_with=[Architect,Builder,Optimizer] | Constitution §5: Product/code = agent-autonomous reversible | **No - high confidence** | 0.95 |
| Poke agent | Orchestrator | Test Prompt | Poke test agent | memory_access | Test output | minimal | Test artifact | **Yes - archive** | 0.60 |
| System Prompt | Orchestrator | System Prompt | System-level orchestration | memory_access, execution_access, coordination_required | Orchestration decisions | coordination_required=true, collaborates_with=[Architect,Builder,Optimizer] | Constitution §5: Product/code = agent-autonomous reversible | **No - high confidence** | 0.95 |
| System | Orchestrator | System Prompt | System orchestrator | memory_access, execution_access | Orchestration decisions | coordination_required=true | Human-gated legal/financial | Yes - low confidence | 0.70 |

### Planner Prompts (4)

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| Agent Prompt 2025-09-03 | Planner | System Prompt | Planner agent | memory_access, execution_access, web_access | Plans | evidence_required=true | Constitution §5: Product/code = agent-autonomous reversible | Yes - low confidence | 0.70 |
| Fast Prompt | Planner | Specialized | Fast planning | memory_access, execution_access | Plans | evidence_required=true | Constitution §5: Product/code = agent-autonomous reversible | Yes - low confidence | 0.70 |
| phase_mode_prompts | Planner | Specialized | Phase-mode planning | memory_access, execution_access, web_access | Structured plans | evidence_required=true, anti_hallucination=true | Constitution §5: Product/code = agent-autonomous reversible | **No - high confidence** | 0.95 |
| planning-mode | Planner | Specialized | Planning mode | memory_access, execution_access, web_access | Structured plans | evidence_required=true, anti_hallucination=true | Constitution §5: Product/code = agent-autonomous reversible | **No - high confidence** | 0.95 |

### Researcher Prompts (2)

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| Agent CLI Prompt 2025-08-07 | Researcher | System Prompt | Researcher CLI | web_access, memory_access, code_access | Research output | evidence_required=true | Constitution §3: IP hygiene, §5: Product/code = agent-autonomous | Yes - low confidence | 0.70 |
| DeepWiki Prompt | Researcher | Specialized | DeepWiki research | web_access, memory_access, code_access | Research output | evidence_required=true, anti_hallucination=true | Constitution §3: IP hygiene, no self-graded homework | **No - high confidence** | 0.95 |

### Reviewer Prompts (4)

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| DocumentAction | Reviewer | Action Prompt | Document review | memory_access, code_access | Review decisions | verification_required=true, evidence_required=true, audit_logging=true | Constitution §3: No self-graded homework, §5: QA separate from generation | **No - high confidence** | 0.95 |
| ExplainAction | Reviewer | Action Prompt | Explanation review | memory_access, code_access | Review decisions | verification_required=true, evidence_required=true, audit_logging=true | Constitution §3: No self-graded homework | **No - high confidence** | 0.95 |
| MessageAction | Reviewer | Action Prompt | Message review | memory_access | Review decisions | verification_required=true, evidence_required=true, audit_logging=true | Constitution §3: No self-graded homework | **No - high confidence** | 0.95 |
| PreviewAction | Reviewer | Action Prompt | Preview review | memory_access, code_access | Review decisions | verification_required=true, evidence_required=true, audit_logging=true | Constitution §3: No self-graded homework | **No - high confidence** | 0.95 |

---

## Runtime Prompt Components (`core/prompts/`)

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| ArchetypeSelector | All Agents | Selector | Selects archetype per agent with adaptive weights | agent_type, context, performance_history | Selected archetype + weights | Adaptive weights per performance; evidence-based | Constitution §12: Continuous improvement | **No - core runtime** | 0.95 |
| AssetLoader | All Agents | Loader | Loads archetype assets from optimized storage | archetype_name | Archetype data | Structured loading; no agent-touchable secrets | Constitution §7: Secrets never agent-touchable | **No - core runtime** | 0.95 |
| AssetOptimizer | Build-time | Processor | Raw DNA → optimized archetypes (scoring, classification) | raw DNA files | optimized_archetypes.json | Automated classification; no self-graded homework | ADR-001: No self-graded homework | **No - build pipeline** | 0.95 |
| AdaptiveWeights | All Agents | Weights | Dynamic weight adjustment from performance | performance_feedback | Updated weights | Evidence-based adaptation | Constitution §12: Continuous improvement | **No - core runtime** | 0.90 |

---

## Documentation Prompts

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| AGENT_SOP_FRAMEWORK.md | All Agents | SOP Template | Framework for agent SOPs | agent_role, responsibilities | SOP document | Governance: Delegation Matrix, Escalation Framework | Constitution §4: Human oversight, §5: Autonomy by domain | No - current | 0.90 |
| AGENT_REGISTRY.md | All Agents | Registry | Agent role definitions | role, purpose, responsibilities, permissions | Registry entry | Governance: Agent Rights, Responsibilities, Delegation | Constitution §3: Legible authorship, minimum viable autonomy | No - current | 0.95 |
| AGENT_COMMUNICATION_PROTOCOL.md | All Agents | Protocol | Inter-agent messaging | message, recipient, trace_id | Structured message | Traceability required; audit logging | Constitution §3: Legible authorship, escalation | No - current | 0.90 |
| AGENT_MEMORY_MODEL.md | All Agents | Model | Memory architecture | memory_type, content, metadata | Memory operations | Session/LT/Vector separation | Constitution §4: Organizational memory system | No - current | 0.90 |
| AGENT_OPERATING_SYSTEM.md | All Agents | OS Spec | Runtime environment | agent_config, resources | Execution context | Minimum viable autonomy | Constitution §5: Autonomy by domain | No - current | 0.85 |
| AGENT_LIFECYCLE.md | All Agents | Lifecycle | Creation, deployment, retirement | lifecycle_stage, approvals | Lifecycle record | Governance approval required | Constitution §4: Human oversight | No - current | 0.85 |

---

## ADR-Embedded Prompts

| Prompt Name | Target Agent | Prompt Type | Purpose | Inputs | Outputs | Governance Alignment | Constitution Alignment | Modernization Required | Confidence |
|-------------|--------------|-------------|---------|--------|---------|---------------------|----------------------|----------------------|------------|
| ADR-001 No Self-Graded Homework | All Agents | Constraint | Verification separate from generation | agent_output, verifier | Verification result | Mandatory structural separation | Constitution §3: No self-graded homework | No - constitutional | 1.00 |
| ADR-002 Founder Intent Preservation | All Agents | Constraint | Founder intent as highest priority | decision, founder_docs | Aligned decision | Founder intent > Constitution > Safety > Governance | Genesis Architect hierarchy | No - constitutional | 1.00 |
| ADR-003 Constitution-First Governance | All Agents | Constraint | Constitution governs all agent actions | action, constitution | Compliant action | All agents bound by Constitution | Constitution = supreme law | No - constitutional | 1.00 |
| ADR-007 Repository Intelligence | Knowledge Agent | Directive | Build/maintain repository intelligence | repository_state | Intelligence layer | Discovery, classification, relationships | Constitution §6: Knowledge is infrastructure | No - current | 0.95 |
| ADR-008 Documentation-Driven | All Agents | Practice | Docs as part of product | feature, code | Documentation | Every capability documented | Constitution: Documentation is part of product | No - current | 0.95 |

---

## Summary Statistics

| Category | Total | Active | Archive Candidate | Needs Modernization | Constitutional (Immutable) |
|----------|-------|--------|-------------------|---------------------|---------------------------|
| Architect | 5 | 2 | 3 | 3 | 0 |
| Builder | 30 | 11 | 19 | 19 | 0 |
| Governance Director | 3 | 0 | 3 | 3 | 0 |
| Orchestrator | 10 | 4 | 6 | 6 | 0 |
| Planner | 4 | 2 | 2 | 2 | 0 |
| Researcher | 2 | 1 | 1 | 1 | 0 |
| Reviewer | 4 | 4 | 0 | 0 | 0 |
| Runtime Components | 4 | 4 | 0 | 0 | 0 |
| Documentation Prompts | 6 | 6 | 0 | 0 | 0 |
| ADR Constraints | 5 | 5 | 0 | 0 | 5 |
| **TOTAL** | **73** | **39** | **34** | **34** | **5** |

---

## Notes

- **Active** = High-confidence (≥100% classification) or core runtime component
- **Archive Candidate** = Low classification confidence (<50%), test artifacts (Poke_*, chat-titles), or superseded by optimized pipeline
- **Constitutional (Immutable)** = ADR constraints that cannot be modified without governance approval
- **Modernization Required** = Should be consolidated into optimized_archetypes.json or updated for current governance
- The 34 prompts needing modernization are primarily low-confidence DNA variants from the raw asset processor output
- 5 ADR-embedded prompts are constitutional constraints and immutable without governance process