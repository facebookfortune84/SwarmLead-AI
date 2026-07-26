# Prompt to Agent Mapping

**Generated**: 2026-07-26  
**Source**: `asset_processor/output/archetypes/`, `archetype_registry.json`, `archetype_classification_report.json`, `optimized_archetypes.json`, `core/prompts/`, `docs/agents/`

---

## Mapping Methodology

Each prompt (DNA file) is mapped to:
- **Target Agent**: Which runtime agent should consume this prompt
- **Purpose**: What capability this prompt provides
- **Capability Domain**: Execution/Coordination/Governance/Specialized
- **Confidence**: From classification report (100% = definitive archetype match)

---

## Archetype DNA Prompts (64 files)

### Architect Archetype (5 prompts → StrategyAgent / ChiefArchitect)

| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| Agent Prompt 2.0 | StrategyAgent / ChiefArchitect | Software development assistance v2 | Specialized (Architecture) | 21.18% |
| Agent Prompt v1.2 | StrategyAgent / ChiefArchitect | Software development assistance v1.2 | Specialized (Architecture) | 21.18% |
| Craft Prompt | StrategyAgent / ChiefArchitect | Craft-oriented development | Specialized (Architecture) | 26.09% |
| **Quest Design** | **StrategyAgent / ChiefArchitect** | **Quest/design-focused architecture** | **Specialized (Architecture)** | **100%** |
| **Spec Prompt** | **StrategyAgent / ChiefArchitect** | **Specification-driven architecture** | **Specialized (Architecture)** | **100%** |

**Notes**: Quest Design and Spec Prompt are high-confidence and should be primary prompts for Architect role. Versioned prompts (2.0, v1.2) are duplicates - consolidate.

---

### Builder Archetype (30 prompts → BuilderAgent / RepairAgent)

#### High-Confidence (100%) - Primary for BuilderAgent
| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| AI Studio vibe-coder | BuilderAgent | Vibe coding for AI Studio | Execution | 100% |
| **Builder Prompt** | **BuilderAgent** | **Core builder capabilities** | **Execution** | **100%** |
| **Claude Code 2.0** | **BuilderAgent** | **Claude Code 2.0 integration** | **Execution** | **100%** |
| **gemini-2.5-pro** | **BuilderAgent** | **Gemini 2.5 Pro builder** | **Execution** | **100%** |
| **gemini-cli-system-prompt** | **BuilderAgent** | **Gemini CLI builder** | **Execution** | **100%** |
| **google-gemini-cli-system-prompt** | **BuilderAgent** | **Google Gemini CLI builder** | **Execution** | **100%** |
| **gpt-4.1** | **BuilderAgent** | **GPT-4.1 builder** | **Execution** | **100%** |
| **gpt-4o** | **BuilderAgent** | **GPT-4o builder** | **Execution** | **100%** |
| **gpt-5-agent-prompts** | **BuilderAgent** | **GPT-5 agent prompts** | **Execution** | **100%** |
| **gpt-5-mini** | **BuilderAgent** | **GPT-5 mini builder** | **Execution** | **100%** |
| **gpt-5** | **BuilderAgent** | **GPT-5 builder** | **Execution** | **100%** |
| **openai-codex-cli-system-prompt-20250820** | **BuilderAgent** | **OpenAI Codex CLI builder** | **Execution** | **100%** |

#### Low-Confidence (<25%) - Archive Candidates
| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence | Action |
|-------------|--------------|---------|-------------------|------------|--------|
| Chat Prompt | BuilderAgent | Chat-oriented building | Execution | 17.65% | Archive |
| chat-titles | BuilderAgent | Chat title generation | Execution | 17.65% | Archive |
| claude-4-sonnet | BuilderAgent | Claude 4 Sonnet builder | Execution | 22.22% | Archive |
| claude-sonnet-4 | BuilderAgent | Claude Sonnet 4 builder | Execution | 17.65% | Archive |
| Mode_Classifier_Prompt | BuilderAgent | Mode classification | Execution | 17.65% | Archive |
| nes-tab-completion | BuilderAgent | Tab completion | Execution | 17.65% | Archive |
| PlaygroundAction | BuilderAgent | Playground action | Execution | 17.65% | Archive |
| Poke_p1 through Poke_p6 (6) | BuilderAgent | Poke test variants | Execution | 17.65% | **Archive - Test artifacts** |
| Prompt | BuilderAgent | Generic builder prompt | Execution | 17.65% | Consolidate |
| Prompts | BuilderAgent | Multiple prompts | Execution | 17.65% | Consolidate |
| Sonnet 4.5 Prompt | BuilderAgent | Sonnet 4.5 builder | Execution | 17.65% | Archive |
| Tools Wave 11 | BuilderAgent | Tools wave 11 | Execution | 17.65% | Archive |
| Vibe_Prompt | BuilderAgent | Vibe coding | Execution | 17.65% | Archive |

---

### Governance Director Archetype (3 prompts → GovernanceAgent)

| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| MKT_006_IMAGE_GEN_PROMPTING | GovernanceAgent | Image generation governance | Governance | 18.75% |
| Prompt Wave 11 | GovernanceAgent | Governance prompt wave 11 | Governance | 22.22% |
| Quest Action | GovernanceAgent | Quest action governance | Governance | 22.22% |

**Note**: All low confidence. Need new high-confidence Governance DNA.

---

### Orchestrator Archetype (10 prompts → TaskRouter, SwarmCoordinator, SwarmDecisionEngine, AutonomousSwarm)

#### High-Confidence (100%) - Primary for Orchestrator Runtimes
| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| **Agent loop** | TaskRouter / SwarmCoordinator | Agent loop orchestration | Coordination | 100% |
| **Default Prompt** | TaskRouter / SwarmCoordinator | Default orchestrator | Coordination | 100% |
| **Enterprise Prompt** | SwarmDecisionEngine | Enterprise orchestration | Coordination | 100% |
| **Modules** | SwarmCoordinator | Modules orchestration | Coordination | 100% |
| **System Prompt** | SwarmCoordinator / AutonomousSwarm | System-level orchestration | Coordination | 100% |

#### Low-Confidence (~16%) - Archive Candidates
| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence | Action |
|-------------|--------------|---------|-------------------|------------|--------|
| Agent Prompt v1.0 | Orchestrator runtimes | Orchestrator v1.0 | Coordination | 16.67% | Archive |
| Agent Prompt | Orchestrator runtimes | Generic orchestrator | Coordination | 16.67% | Consolidate |
| claude-4-sonnet-agent-prompts | Orchestrator runtimes | Claude 4 Sonnet agent prompts | Coordination | 16.67% | Archive |
| Poke agent | Orchestrator runtimes | Poke test agent | Coordination | 16.67% | **Archive - Test** |
| System | Orchestrator runtimes | System orchestrator | Coordination | 16.67% | Consolidate with System Prompt |

---

### Planner Archetype (4 prompts → PlannerAgent - NOT IMPLEMENTED)

| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| Agent Prompt 2025-09-03 | PlannerAgent | Planner agent | Specialized | 27.63% |
| Fast Prompt | PlannerAgent | Fast planning | Specialized | 25.81% |
| **phase_mode_prompts** | **PlannerAgent** | **Phase-mode planning** | **Specialized** | **100%** |
| **planning-mode** | **PlannerAgent** | **Planning mode** | **Specialized** | **100%** |

**Action**: Create PlannerAgent using 2 high-confidence DNA files.

---

### Researcher Archetype (2 prompts → ResearcherAgent - NOT IMPLEMENTED)

| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| Agent CLI Prompt 2025-08-07 | ResearcherAgent | Researcher CLI | Specialized | 24.56% |
| **DeepWiki Prompt** | **ResearcherAgent** | **DeepWiki research** | **Specialized** | **100%** |

**Action**: Create ResearcherAgent using DeepWiki Prompt DNA.

---

### Reviewer Archetype (4 prompts → ReviewAgent)

| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| **DocumentAction** | **ReviewAgent** | **Document review** | **Quality** | **100%** |
| **ExplainAction** | **ReviewAgent** | **Explanation review** | **Quality** | **100%** |
| **MessageAction** | **ReviewAgent** | **Message review** | **Quality** | **100%** |
| **PreviewAction** | **ReviewAgent** | **Preview review** | **Quality** | **100%** |

**All 100% confidence** - Use as 4 action modes for ReviewAgent.

---

## Runtime Prompt Components (core/prompts/)

| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| ArchetypeSelector | All Agents | Selects archetype per agent with adaptive weights | Coordination | 95% (core runtime) |
| AssetLoader | All Agents | Loads archetype assets from optimized storage | Coordination | 95% (core runtime) |
| AssetOptimizer | Build-time | Raw DNA → optimized archetypes | Build Pipeline | 95% (build pipeline) |
| AdaptiveWeights | All Agents | Dynamic weight adjustment from performance | Coordination | 90% (core runtime) |

---

## Documentation Prompts

| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| AGENT_SOP_FRAMEWORK.md | All Agents | SOP template framework | Governance | 90% |
| AGENT_REGISTRY.md | All Agents | Agent role definitions | Governance | 95% |
| AGENT_COMMUNICATION_PROTOCOL.md | All Agents | Inter-agent messaging | Coordination | 90% |
| AGENT_MEMORY_MODEL.md | All Agents | Memory architecture | Coordination | 90% |
| AGENT_OPERATING_SYSTEM.md | All Agents | Runtime environment spec | Coordination | 85% |
| AGENT_LIFECYCLE.md | All Agents | Creation, deployment, retirement | Governance | 85% |

---

## ADR-Embedded Constitutional Prompts (Immutable)

| Prompt Name | Target Agent | Purpose | Capability Domain | Confidence |
|-------------|--------------|---------|-------------------|------------|
| ADR-001 No Self-Graded Homework | All Agents | Verification separate from generation | Governance | 100% (Constitutional) |
| ADR-002 Founder Intent Preservation | All Agents | Founder intent as highest priority | Governance | 100% (Constitutional) |
| ADR-003 Constitution-First Governance | All Agents | Constitution governs all actions | Governance | 100% (Constitutional) |
| ADR-007 Repository Intelligence | Knowledge Agent | Build/maintain repository intelligence | Knowledge | 95% |
| ADR-008 Documentation-Driven | All Agents | Docs as part of product | Governance | 95% |

---

## Summary Statistics

| Category | Total Prompts | High Confidence (≥100%) | Low Confidence (<50%) | Mapped to Runtime | Unmapped (Gap) |
|----------|---------------|------------------------|----------------------|-------------------|----------------|
| Architect | 5 | 2 | 3 | 1 (StrategyAgent) | ChiefArchitect |
| Builder | 30 | 12 | 18 | 1 (BuilderAgent) | - |
| Governance Director | 3 | 0 | 3 | 0 | **GovernanceAgent** |
| Orchestrator | 10 | 5 | 5 | 4 (TaskRouter, SwarmCoordinator, SwarmDecisionEngine, AutonomousSwarm) | - |
| Planner | 4 | 2 | 2 | 0 | **PlannerAgent** |
| Researcher | 2 | 1 | 1 | 0 | **ResearcherAgent** |
| Reviewer | 4 | 4 | 0 | 1 (ReviewAgent) | - |
| Runtime Components | 4 | 4 | 0 | 4 (core/prompts/) | - |
| Documentation | 6 | 6 | 0 | 6 (all agents) | - |
| ADR Constraints | 5 | 5 | 0 | 5 (all agents) | - |
| **TOTAL** | **73** | **39** | **34** | **17 agents** | **4 gaps** |

---

## Unmapped Prompts (Gaps)

| Prompt | Archetype | Reason Unmapped |
|--------|-----------|-----------------|
| 3 Governance Director DNA | Governance Director | No GovernanceAgent runtime |
| 2 Planner DNA (high-conf) | Planner | No PlannerAgent runtime |
| 1 Researcher DNA (high-conf) | Researcher | No ResearcherAgent runtime |
| Optimizer references | Optimizer | Ghost archetype - no DNA files |

---

## Archive Candidates (23 prompts)

| Count | Prompts | Reason |
|-------|---------|--------|
| 6 | Poke_p1 through Poke_p6 | Test artifacts |
| 1 | Poke agent | Test artifact |
| 6 | GPT-4.1, 4o, 5, 5-mini, 5-agent, Sonnet 4.5, Claude 4 Sonnet, Claude Sonnet 4 | Model variants - parameterize |
| 2 | Prompt, Prompts | Generic duplicates |
| 2 | Agent Prompt 2.0, v1.2 | Versioned duplicates |
| 2 | Agent Prompt, Agent Prompt v1.0 | Versioned duplicates |
| 2 | System Prompt, System | Naming duplicates |
| 1 | chat-titles | Test artifact |
| 1 | Mode_Classifier | Test artifact |
| 1 | PlaygroundAction | Test artifact |
| 1 | nes-tab-completion | Test artifact |
| 1 | Tools Wave 11 | Test artifact |
| 1 | Vibe_Prompt | Low confidence duplicate |