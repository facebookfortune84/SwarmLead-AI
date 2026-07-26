# Archetype Family Tree

**Generated**: 2026-07-26  
**Source**: `asset_processor/output/archetypes/`, `archetype_registry.json`, `archetype_classification_report.json`, `optimized_archetypes.json`

---

## Archetype Classification Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORGANIZATIONAL INTELLIGENCE                   │
│                 (Genesis Autonomous Swarm)                       │
└─────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────┬───────────┴───────────┬───────────────┐
        ▼               ▼                       ▼               ▼
┌───────────────┐ ┌───────────────┐     ┌───────────────┐ ┌───────────────┐
│  EXECUTION    │ │  COORDINATION │     │  GOVERNANCE   │ │  SPECIALIZED  │
│  FAMILY       │ │  FAMILY       │     │  FAMILY       │ │  FAMILY       │
└───────────────┘ └───────────────┘     └───────────────┘ └───────────────┘
        │               │                       │               │
   ┌────┴────┐      ┌────┴────┐           ┌─────┴─────┐   ┌─────┴─────┐
   ▼         ▼      ▼         ▼           ▼           ▼   ▼           ▼
Builder   Repair   Orchestrator  Swarm    Governance  Planner    Researcher
Agent     Agent    Coordinator   Runtime  Director    Agent      Agent
(30 DNA)  (0 DNA)  (10 DNA)      (0 DNA)  (3 DNA)     (4 DNA)    (2 DNA)
                              ▲
                              │
                       ┌──────┴──────┐
                       ▼             ▼
                 SwarmDecision   SwarmEvaluator
                 Engine          (0 DNA)
```

---

## Family 1: Execution Family

### Parent Archetype: **Builder** (30 DNA files)

**Purpose**: Code generation, implementation, software engineering

**High-Confidence Members (11, 100% classification)**:
| DNA File | Source | Capabilities |
|----------|--------|--------------|
| AI Studio vibe-coder_dna.json | AI Studio | vibe coding, rapid prototyping |
| Builder Prompt_dna.json | Core builder | General software development |
| Claude Code 2.0_dna.json | Anthropic | Code generation, CLI integration |
| gemini-2.5-pro_dna.json | Google | Advanced reasoning, coding |
| gpt-4.1_dna.json | OpenAI | Coding, analysis |
| gpt-4o_dna.json | OpenAI | Multimodal coding |
| gpt-5_dna.json | OpenAI | Next-gen coding |
| gpt-5-mini_dna.json | OpenAI | Efficient coding |
| gpt-5-agent-prompts_dna.json | OpenAI | Agentic workflows |
| openai-codex-cli-system-prompt-20250820_dna.json | OpenAI | Codex CLI integration |
| gemini-cli-system-prompt_dna.json | Google | Gemini CLI |
| google-gemini-cli-system-prompt_dna.json | Google | Google Gemini CLI |

**Low-Confidence Members (19, <25% classification)**:
- Chat Prompt, chat-titles (chat-oriented)
- claude-4-sonnet, claude-sonnet-4 (model-specific)
- Mode_Classifier_Prompt (classification)
- nes-tab-completion (completion)
- PlaygroundAction (playground)
- Poke_p1 through Poke_p6 (6 test variants)
- Prompt, Prompts (generic)
- Sonnet 4.5 Prompt (model-specific)
- Tools Wave 11 (tool-focused)
- Vibe_Prompt (vibe coding)

**Shared Capabilities** (from high-confidence DNA):
- `software_engineering`, `code_generation`, `file_operations`
- Full tool access: memory, web, code, execution, parallel, knowledge
- Collaborates with: Architect, Builder, Optimizer

**Derived Runtime**: `BuilderAgent` (core/orchestration/builder_agent.py)

**Duplicate Detection**: 
- `Prompt_dna.json` + `Prompts_dna.json` → generic duplicates
- `Poke_p1` through `Poke_p6` → 6 identical test artifacts
- `chat-titles` + `Chat Prompt` → chat specialization duplicates
- Multiple model-specific variants (GPT-4.1, 4o, 5, 5-mini, 5-agent) → model variants, not capability variants

---

### Child: **Repair** (0 DNA files - referenced in Builder DNA)

**Purpose**: Automated code repair, refactoring

**Derived Runtime**: `RepairAgent` (core/orchestration/repair_agent.py)

**Gap**: No dedicated DNA files. Uses BuilderAgent infrastructure with repair-specific prompts.

**Overlap with Builder**: Both have code_access, execution_access. Repair is specialized Builder.

---

## Family 2: Coordination Family

### Parent Archetype: **Orchestrator** (10 DNA files)

**Purpose**: Multi-agent coordination, task routing, decision making

**High-Confidence Members (4, 100% classification)**:
| DNA File | Purpose | Key Traits |
|----------|---------|------------|
| Agent loop_dna.json | Core orchestration loop | coordination_required, collaborates_with=[Architect,Builder,Optimizer] |
| Default Prompt_dna.json | Default coordinator | coordination_required, collaborates_with=[Architect,Builder,Optimizer] |
| Enterprise Prompt_dna.json | Enterprise orchestration | coordination_required, audit_logging=true |
| System Prompt_dna.json | System-level orchestration | coordination_required, collaborates_with=[Architect,Builder,Optimizer] |

**Low-Confidence Members (6, ~16% classification)**:
- Agent Prompt v1.0, Agent Prompt (generic)
- claude-4-sonnet-agent-prompts (model-specific)
- Modules_dna.json (modular coordination)
- Poke agent_dna.json (test)
- System_dna.json (generic system)

**Shared Capabilities**:
- `coordination`, `consensus_building`, `task_routing`, `decision_making`
- Tool policy: memory_access, execution_access, coordination_required=true
- Collaborates with: Architect, Builder, Optimizer

**Derived Runtimes** (4 agents share this archetype):
- `TaskRouter` - routes tasks to agents
- `SwarmCoordinator` - coordinates agent collectives
- `SwarmDecisionEngine` - collective decision making
- `AutonomousSwarm` - self-organizing swarms

**Duplicate Detection**:
- `Agent Prompt` + `Agent Prompt v1.0` → versioned duplicates
- `System Prompt` + `System_dna.json` → naming variants
- `Modules_dna.json` → modular variant of System

---

### Child: **Swarm Runtime** (0 DNA - emergent)

**Members**:
- `SwarmCoordinator` - coordination logic
- `SwarmDecisionEngine` - collective decisions
- `SwarmEvaluator` - decision evaluation
- `AutonomousSwarm` - lifecycle management

**Shared Infrastructure**: AgentManager, TaskRouter, Scheduler

---

## Family 3: Governance Family

### Parent Archetype: **Governance Director** (3 DNA files)

**Purpose**: Policy enforcement, constitutional compliance, governance auditing

**All Members Low Confidence (18-22%)**:
| DNA File | Confidence | Purpose |
|----------|------------|---------|
| MKT_006_IMAGE_GEN_PROMPTING_dna.json | 18.75% | Image generation governance |
| Prompt Wave 11_dna.json | 22.22% | Governance prompt wave |
| Quest Action_dna.json | 22.22% | Quest action governance |

**Shared Traits**:
- Governance: verification_required=true, audit_logging=true
- Tool policy: web_access, memory_access only (no code/execution)
- Collaborates with: Architect, Builder, Optimizer (per DNA) but governance role suggests oversight

**Derived Runtime**: ❌ **NOT IMPLEMENTED** - Critical gap

**Conflict**: Constitution §13 requires Governance Agent with per-role allowlists. No runtime exists.

**Duplicate Detection**: None - only 3 distinct files

---

## Family 4: Specialized Family

### **Architect** (5 DNA files)

**Purpose**: Architecture, planning, research, technical direction

**High-Confidence (2, 100%)**:
| DNA File | Confidence | Purpose |
|----------|------------|---------|
| Quest Design_dna.json | 100% | Quest/design-focused architecture |
| Spec_Prompt_dna.json | 100% | Specification-driven architecture |

**Low-Confidence (3, 21-26%)**:
| DNA File | Confidence | Purpose |
|----------|------------|---------|
| Agent Prompt 2.0_dna.json | 21.18% | Software development assistance v2 |
| Agent Prompt v1.2_dna.json | 21.18% | Software development assistance v1.2 |
| Craft Prompt_dna.json | 26.09% | Craft-oriented development |

**Shared Capabilities** (from high-confidence):
- `architecture`, `planning`, `research`, `software_engineering`, `task_management`
- Tool policy: full access (memory, web, code, execution, parallel, knowledge)
- Collaborates with: Architect, Builder, Optimizer

**Derived Runtime**: `StrategyAgent` → maps to Architect archetype (hybrid)

**Duplicate Detection**:
- `Agent Prompt 2.0` + `Agent Prompt v1.2` → versioned duplicates
- `Quest Design` + `Spec Prompt` → distinct specializations (design vs spec)

---

### **Reviewer** (4 DNA files - ALL 100%)

**Purpose**: Review actions (document, explain, message, preview)

**All High-Confidence (100%)**:
| DNA File | Action Type | Governance |
|----------|-------------|------------|
| DocumentAction_dna.json | Document review | verification_required, evidence_required, audit_logging |
| ExplainAction_dna.json | Explanation review | verification_required, evidence_required, audit_logging |
| MessageAction_dna.json | Message review | verification_required, evidence_required, audit_logging |
| PreviewAction_dna.json | Preview review | verification_required, evidence_required, audit_logging |

**Shared Traits**:
- Tool policy: ALL FALSE (no tool access - pure review)
- Memory policy: read only, long_term_memory=true
- Constraints: `always_follow_policy`
- Governance: Full verification, evidence, audit logging

**Derived Runtime**: `ReviewAgent` (core/orchestration/review_agent.py)

**Duplicate Detection**: None - 4 distinct action types

---

### **Planner** (4 DNA files)

**Purpose**: Planning, phase-mode execution, structured planning

**High-Confidence (2, 100%)**:
| DNA File | Confidence | Purpose |
|----------|------------|---------|
| phase_mode_prompts_dna.json | 100% | Phase-mode planning |
| planning-mode_dna.json | 100% | Planning mode execution |

**Low-Confidence (2, 25-27%)**:
| DNA File | Confidence | Purpose |
|----------|------------|---------|
| Agent Prompt 2025-09-03_dna.json | 27.63% | Planner agent |
| Fast Prompt_dna.json | 25.81% | Fast planning |

**Derived Runtime**: ❌ **NOT IMPLEMENTED** - Gap

**Duplicate Detection**: 
- `phase_mode_prompts` + `planning-mode` → similar phase-based planning
- `Agent Prompt 2025-09-03` + `Fast Prompt` → generic vs fast variants

---

### **Researcher** (2 DNA files)

**Purpose**: Research, deep investigation, CLI-based research

**High-Confidence (1, 100%)**:
| DNA File | Confidence | Purpose |
|----------|------------|---------|
| DeepWiki Prompt_dna.json | 100% | DeepWiki research |

**Low-Confidence (1, 24%)**:
| DNA File | Confidence | Purpose |
|----------|------------|---------|
| Agent CLI Prompt 2025-08-07_dna.json | 24.56% | CLI-based research |

**Derived Runtime**: ❌ **NOT IMPLEMENTED** - Gap

---

### **Optimizer** (0 DNA files)

**Referenced in**: All high-confidence DNA files collaborate_with: `["Architect", "Builder", "Optimizer"]`

**Status**: **GHOST ARCHETYPE** - Referenced but no DNA files exist

**Implication**: All archetypes expect an Optimizer peer that doesn't exist

---

## Cross-Family Shared Capabilities

| Capability | Families | Archetypes |
|------------|----------|------------|
| `collaborates_with: [Architect, Builder, Optimizer]` | Execution, Coordination, Governance, Architect, Builder, Orchestrator, Reviewer, Planner, Researcher | Universal reference triad |
| `memory_access: true` | Execution, Coordination, Architect, Builder, Orchestrator | Most except Reviewer/Governance |
| `web_access: true` | Execution, Architect, Builder, Orchestrator, Planner, Researcher | Most |
| `code_access: true` | Execution, Architect, Builder | Technical archetypes |
| `execution_access: true` | Execution, Architect, Builder, Orchestrator | Technical + Coordination |
| `verification_required: true` | Reviewer (all), Governance Director (all) | Quality + Governance |
| `evidence_required: true` | Reviewer (all), Governance Director (all) | Quality + Governance |

---

## Duplicate Archetype Analysis

### Exact/Functional Duplicates

| Duplicate Group | Files | Recommendation |
|-----------------|-------|----------------|
| Poke Test Variants (Builder) | Poke_p1 through Poke_p6 (6 files) | **Archive** - test artifacts |
| Poke Test Variants (Orchestrator) | Poke agent_dna.json (1 file) | **Archive** - test artifact |
| Generic Prompt Variants (Builder) | Prompt_dna.json, Prompts_dna.json | **Consolidate** - same purpose |
| Versioned Prompts (Architect) | Agent Prompt 2.0, Agent Prompt v1.2 | **Consolidate** - keep latest |
| Versioned Prompts (Orchestrator) | Agent Prompt, Agent Prompt v1.0 | **Consolidate** - keep latest |
| System Variants (Orchestrator) | System Prompt_dna.json, System_dna.json | **Consolidate** - naming variant |
| Model-Specific Variants (Builder) | 8 GPT/Gemini/Claude variants | **Parameterize** - single template with model config |

### Overlapping Responsibilities

| Overlap | Archetypes | Conflict |
|---------|------------|----------|
| Code Generation | Builder, Repair, Architect (partial) | Repair is specialized Builder; Architect does design not implementation |
| Coordination | Orchestrator, Swarm Coordinator, TaskRouter, Scheduler | 4 runtimes for 1 archetype - consolidate |
| Planning | Architect (planning capability), Planner (dedicated) | Planner not implemented; Architect does planning |
| Review | Reviewer (4 actions), QA Agent (doc) | QA Agent not implemented; Reviewer covers code review |
| Governance | Governance Director, Audit Agent, Governance Agent (doc) | 3 documented, 1 partial archetype, 0 runtime |

---

## Unmapped Archetypes (No Runtime)

| Archetype | DNA Count | High-Confidence | Status |
|-----------|-----------|-----------------|--------|
| Planner | 4 | 2 | **Gap** - No PlannerAgent |
| Researcher | 2 | 1 | **Gap** - No ResearcherAgent |
| Governance Director | 3 | 0 | **Gap** - No GovernanceAgent |
| Optimizer | 0 | 0 | **Ghost** - Referenced but missing |

---

## Archetype Consolidation Recommendations

### Target: 8 Archetypes → 6 Runtime Archetypes

| Target Runtime Archetype | Source DNA | Consolidation |
|--------------------------|------------|---------------|
| **Builder** | Builder (11 high-conf) + Repair (0) | Merge Repair into Builder as mode |
| **Architect** | Architect (2 high-conf) | StrategyAgent enhancement |
| **Orchestrator** | Orchestrator (4 high-conf) | Unify TaskRouter, SwarmCoordinator, SwarmDecisionEngine, AutonomousSwarm |
| **Reviewer** | Reviewer (4 high-conf) | ReviewAgent with 4 action modes |
| **Planner** | Planner (2 high-conf) | **New**: PlannerAgent |
| **Researcher** | Researcher (1 high-conf) | **New**: ResearcherAgent |
| **Governance** | Governance Director (3 low-conf) | **New**: GovernanceAgent (needs new DNA) |
| **Optimizer** | None | **Investigate** - create or remove references |

### Archive Candidates (23 DNA files)
- 6 Poke_p* (Builder test artifacts)
- 1 Poke agent (Orchestrator test)
- 6 Model-specific variants (Builder) → parameterize
- 2 Versioned Architect prompts
- 2 Versioned Orchestrator prompts
- 1 System_dna duplicate
- 2 Generic Prompt/Prompts
- 2 Phase-mode/planning-mode (similar) → keep both as distinct modes
- 1 chat-titles (Builder)
- 1 Mode_Classifier (Builder)
- 1 PlaygroundAction (Builder)
- 1 nes-tab-completion (Builder)
- 1 Tools Wave 11 (Builder)
- 1 Vibe_Prompt (Builder)

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total DNA Files | 64 |
| Archetype Families | 4 (Execution, Coordination, Governance, Specialized) |
| Archetype Types | 8 |
| High-Confidence DNA (≥100%) | 20 |
| Low-Confidence DNA (<50%) | 44 |
| Implemented Runtimes | 12 (5 hybrid mapped) |
| Unmapped Archetypes | 4 (Planner, Researcher, Governance Director, Optimizer) |
| Duplicate/Test Artifacts | ~23 (36%) |
| Consolidation Potential | 64 → ~25 active prompts |