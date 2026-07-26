# Asset Registry

**Generated**: 2026-07-24  
**Source**: `assets/`, `asset_processor/`, `asset_processor/output/`, `docs/`  
**Classification Rules**: Active | Deprecated | Archive Candidate | Delete Candidate | Unknown

---

## Raw Assets (`assets/raw/`)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| agent_registry.json | `assets/raw/agent_registry.json` | Registry (JSON) | Canonical agent registry with 3 agents (memory_manager, governance_director, architect) and scored variants from SymbioticOS pipeline | archetype_classification_report.json, archetype_registry.json | Source for runtime agent definitions; superseded by optimized_archetypes.json | Archive Candidate | 0.95 |
| archetype_registry.json | `assets/raw/archetype_registry.json` | Registry (JSON) | 58 archetype DNA files mapped to 7 archetypes with confidence scores | agent_registry.json, archetype_classification_report.json | Input to asset_optimizer.py; source for optimized_archetypes.json | Archive Candidate | 0.95 |
| archetype_classification_report.json | `assets/raw/archetype_classification_report.json` | Classification Report (JSON) | Detailed scoring of 58 source files across 10 archetype categories with per-archetype scores | archetype_registry.json, agent_registry.json | Validates archetype assignments; used by asset_optimizer for weighting | Archive Candidate | 0.95 |

---

## Optimized Assets (`assets/optimized/`)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| optimized_archetypes.json | `assets/optimized/optimized_archetypes.json` | Optimized Prompts (JSON) | 6 condensed archetype prompts (researcher, orchestrator, architect, planner, builder, reviewer) with merged text and scores | archetype_registry.json, archetype_classification_report.json, archetype_weights.json | Consumed by ArchetypeSelector at runtime; replaces raw DNA files for production | Active | 0.90 |
| archetype_weights.json | `assets/optimized/archetype_weights.json` | Weights (JSON) | Adaptive weight configuration for archetype selection (65 bytes) | adaptive_weights.py, optimized_archetypes.json | Used by AdaptiveWeights class for dynamic weight adjustment | Active | 0.90 |

---

## Archetype DNA Files (`asset_processor/output/archetypes/`)

### Architect (5 files)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| Agent Prompt 2.0_dna.json | `asset_processor/output/archetypes/architect/Agent Prompt 2.0_dna.json` | DNA (JSON) | Architect v2.0: software development assistance with architecture, planning, research capabilities | asset_optimizer.py, archetype_selector.py | Classified as "architect" (21.18% confidence); superseded by optimized_archetypes.json | Archive Candidate | 0.85 |
| Agent Prompt v1.2_dna.json | `asset_processor/output/archetypes/architect/Agent Prompt v1.2_dna.json` | DNA (JSON) | Architect v1.2: similar capabilities to v2.0 | asset_optimizer.py, archetype_selector.py | Classified as "architect" (21.18% confidence); predecessor to v2.0 | Archive Candidate | 0.85 |
| Craft Prompt_dna.json | `asset_processor/output/archetypes/architect/Craft Prompt_dna.json` | DNA (JSON) | Craft-oriented architect prompt | asset_optimizer.py, archetype_selector.py | Classified as "architect" (26.09% confidence) | Archive Candidate | 0.80 |
| Quest Design_dna.json | `asset_processor/output/archetypes/architect/Quest Design_dna.json` | DNA (JSON) | Quest/design-focused architect prompt | asset_optimizer.py, archetype_selector.py | **High confidence (100%)** architect classification; strong signal | Active | 0.95 |
| Spec_Prompt_dna.json | `asset_processor/output/archetypes/architect/Spec_Prompt_dna.json` | DNA (JSON) | Specification-focused architect prompt | asset_optimizer.py, archetype_selector.py | **High confidence (100%)** architect classification; strong signal | Active | 0.95 |

### Builder (30 files)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| AI Studio vibe-coder_dna.json | `asset_processor/output/archetypes/builder/AI Studio vibe-coder_dna.json` | DNA (JSON) | Builder archetype for AI Studio vibe coding | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| Builder Prompt_dna.json | `asset_processor/output/archetypes/builder/Builder Prompt_dna.json` | DNA (JSON) | Core builder prompt | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| Chat Prompt_dna.json | `asset_processor/output/archetypes/builder/Chat Prompt_dna.json` | DNA (JSON) | Chat-oriented builder | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| chat-titles_dna.json | `asset_processor/output/archetypes/builder/chat-titles_dna.json` | DNA (JSON) | Chat title generation | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| Claude Code 2.0_dna.json | `asset_processor/output/archetypes/builder/Claude Code 2.0_dna.json` | DNA (JSON) | Claude Code 2.0 builder prompt | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| claude-4-sonnet_dna.json | `asset_processor/output/archetypes/builder/claude-4-sonnet_dna.json` | DNA (JSON) | Claude 4 Sonnet builder | asset_optimizer.py, archetype_selector.py | Low confidence (22.22%) builder | Archive Candidate | 0.70 |
| claude-sonnet-4_dna.json | `asset_processor/output/archetypes/builder/claude-sonnet-4_dna.json` | DNA (JSON) | Claude Sonnet 4 builder | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| gemini-2.5-pro_dna.json | `asset_processor/output/archetypes/builder/gemini-2.5-pro_dna.json` | DNA (JSON) | Gemini 2.5 Pro builder | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| gemini-cli-system-prompt_dna.json | `asset_processor/output/archetypes/builder/gemini-cli-system-prompt_dna.json` | DNA (JSON) | Gemini CLI system prompt builder | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| google-gemini-cli-system-prompt_dna.json | `asset_processor/output/archetypes/builder/google-gemini-cli-system-prompt_dna.json` | DNA (JSON) | Google Gemini CLI builder | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| gpt-4.1_dna.json | `asset_processor/output/archetypes/builder/gpt-4.1_dna.json` | DNA (JSON) | GPT-4.1 builder | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| gpt-4o_dna.json | `asset_processor/output/archetypes/builder/gpt-4o_dna.json` | DNA (JSON) | GPT-4o builder | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| gpt-5-agent-prompts_dna.json | `asset_processor/output/archetypes/builder/gpt-5-agent-prompts_dna.json` | DNA (JSON) | GPT-5 agent prompts builder | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| gpt-5-mini_dna.json | `asset_processor/output/archetypes/builder/gpt-5-mini_dna.json` | DNA (JSON) | GPT-5 mini builder | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| gpt-5_dna.json | `asset_processor/output/archetypes/builder/gpt-5_dna.json` | DNA (JSON) | GPT-5 builder | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| Mode_Clasifier_Prompt_dna.json | `asset_processor/output/archetypes/builder/Mode_Clasifier_Prompt_dna.json` | DNA (JSON) | Mode classifier builder | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| nes-tab-completion_dna.json | `asset_processor/output/archetypes/builder/nes-tab-completion_dna.json` | DNA (JSON) | NES tab completion builder | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| openai-codex-cli-system-prompt-20250820_dna.json | `asset_processor/output/archetypes/builder/openai-codex-cli-system-prompt-20250820_dna.json` | DNA (JSON) | OpenAI Codex CLI builder | asset_optimizer.py, archetype_selector.py | **100% confidence** builder classification | Active | 0.95 |
| PlaygroundAction_dna.json | `asset_processor/output/archetypes/builder/PlaygroundAction_dna.json` | DNA (JSON) | Playground action builder | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| Poke_p1_dna.json through Poke_p6_dna.json (6 files) | `asset_processor/output/archetypes/builder/Poke_p*_dna.json` | DNA (JSON) | Poke test prompts (p1-p6) | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder; likely test artifacts | Archive Candidate | 0.60 |
| Prompt_dna.json | `asset_processor/output/archetypes/builder/Prompt_dna.json` | DNA (JSON) | Generic builder prompt | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| Prompts_dna.json | `asset_processor/output/archetypes/builder/Prompts_dna.json` | DNA (JSON) | Multiple prompts collection | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| Sonnet 4.5 Prompt_dna.json | `asset_processor/output/archetypes/builder/Sonnet 4.5 Prompt_dna.json` | DNA (JSON) | Sonnet 4.5 builder | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| Tools Wave 11_dna.json | `asset_processor/output/archetypes/builder/Tools Wave 11_dna.json` | DNA (JSON) | Tools wave 11 builder | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |
| Vibe_Prompt_dna.json | `asset_processor/output/archetypes/builder/Vibe_Prompt_dna.json` | DNA (JSON) | Vibe coding builder | asset_optimizer.py, archetype_selector.py | Low confidence (17.65%) builder | Archive Candidate | 0.70 |

### Governance Director (3 files)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| MKT_006_IMAGE_GEN_PROMPTING_dna.json | `asset_processor/output/archetypes/governance_director/MKT_006_IMAGE_GEN_PROMPTING_dna.json` | DNA (JSON) | Image generation governance prompting | asset_optimizer.py, archetype_selector.py | Low confidence (18.75%) governance_director | Archive Candidate | 0.70 |
| Prompt Wave 11_dna.json | `asset_processor/output/archetypes/governance_director/Prompt Wave 11_dna.json` | DNA (JSON) | Governance prompt wave 11 | asset_optimizer.py, archetype_selector.py | Low confidence (22.22%) governance_director | Archive Candidate | 0.70 |
| Quest Action_dna.json | `asset_processor/output/archetypes/governance_director/Quest Action_dna.json` | DNA (JSON) | Quest action governance | asset_optimizer.py, archetype_selector.py | Low confidence (22.22%) governance_director | Archive Candidate | 0.70 |

### Orchestrator (10 files)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| Agent loop_dna.json | `asset_processor/output/archetypes/orchestrator/Agent loop_dna.json` | DNA (JSON) | Agent loop orchestration | asset_optimizer.py, archetype_selector.py | **100% confidence** orchestrator classification | Active | 0.95 |
| Agent Prompt v1.0_dna.json | `asset_processor/output/archetypes/orchestrator/Agent Prompt v1.0_dna.json` | DNA (JSON) | Orchestrator v1.0 | asset_optimizer.py, archetype_selector.py | Low confidence (16.67%) orchestrator | Archive Candidate | 0.70 |
| Agent Prompt_dna.json | `asset_processor/output/archetypes/orchestrator/Agent Prompt_dna.json` | DNA (JSON) | Generic orchestrator prompt | asset_optimizer.py, archetype_selector.py | Low confidence (16.67%) orchestrator | Archive Candidate | 0.70 |
| claude-4-sonnet-agent-prompts_dna.json | `asset_processor/output/archetypes/orchestrator/claude-4-sonnet-agent-prompts_dna.json` | DNA (JSON) | Claude 4 Sonnet agent prompts | asset_optimizer.py, archetype_selector.py | Low confidence (16.67%) orchestrator | Archive Candidate | 0.70 |
| Default Prompt_dna.json | `asset_processor/output/archetypes/orchestrator/Default Prompt_dna.json` | DNA (JSON) | Default orchestrator prompt | asset_optimizer.py, archetype_selector.py | **100% confidence** orchestrator classification | Active | 0.95 |
| Enterprise Prompt_dna.json | `asset_processor/output/archetypes/orchestrator/Enterprise Prompt_dna.json` | DNA (JSON) | Enterprise orchestrator | asset_optimizer.py, archetype_selector.py | **100% confidence** orchestrator classification | Active | 0.95 |
| Modules_dna.json | `asset_processor/output/archetypes/orchestrator/Modules_dna.json` | DNA (JSON) | Modules orchestration | asset_optimizer.py, archetype_selector.py | **100% confidence** orchestrator classification | Active | 0.95 |
| Poke agent_dna.json | `asset_processor/output/archetypes/orchestrator/Poke agent_dna.json` | DNA (JSON) | Poke test agent | asset_optimizer.py, archetype_selector.py | Low confidence (16.67%) orchestrator | Archive Candidate | 0.60 |
| System Prompt_dna.json | `asset_processor/output/archetypes/orchestrator/System Prompt_dna.json` | DNA (JSON) | System-level orchestrator | asset_optimizer.py, archetype_selector.py | **100% confidence** orchestrator classification | Active | 0.95 |
| System_dna.json | `asset_processor/output/archetypes/orchestrator/System_dna.json` | DNA (JSON) | System orchestrator | asset_optimizer.py, archetype_selector.py | Low confidence (16.67%) orchestrator | Archive Candidate | 0.70 |

### Planner (4 files)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| Agent Prompt 2025-09-03_dna.json | `asset_processor/output/archetypes/planner/Agent Prompt 2025-09-03_dna.json` | DNA (JSON) | Planner agent prompt | asset_optimizer.py, archetype_selector.py | Low confidence (27.63%) planner | Archive Candidate | 0.70 |
| Fast Prompt_dna.json | `asset_processor/output/archetypes/planner/Fast Prompt_dna.json` | DNA (JSON) | Fast planning prompt | asset_optimizer.py, archetype_selector.py | Low confidence (25.81%) planner | Archive Candidate | 0.70 |
| phase_mode_prompts_dna.json | `asset_processor/output/archetypes/planner/phase_mode_prompts_dna.json` | DNA (JSON) | Phase-mode planning prompts | asset_optimizer.py, archetype_selector.py | **100% confidence** planner classification | Active | 0.95 |
| planning-mode_dna.json | `asset_processor/output/archetypes/planner/planning-mode_dna.json` | DNA (JSON) | Planning mode prompt | asset_optimizer.py, archetype_selector.py | **100% confidence** planner classification | Active | 0.95 |

### Researcher (2 files)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| Agent CLI Prompt 2025-08-07_dna.json | `asset_processor/output/archetypes/researcher/Agent CLI Prompt 2025-08-07_dna.json` | DNA (JSON) | Researcher CLI prompt | asset_optimizer.py, archetype_selector.py | Low confidence (24.56%) researcher | Archive Candidate | 0.70 |
| DeepWiki Prompt_dna.json | `asset_processor/output/archetypes/researcher/DeepWiki Prompt_dna.json` | DNA (JSON) | DeepWiki research prompt | asset_optimizer.py, archetype_selector.py | **100% confidence** researcher classification | Active | 0.95 |

### Reviewer (4 files)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| DocumentAction_dna.json | `asset_processor/output/archetypes/reviewer/DocumentAction_dna.json` | DNA (JSON) | Document review action | asset_optimizer.py, archetype_selector.py | **100% confidence** reviewer classification | Active | 0.95 |
| ExplainAction_dna.json | `asset_processor/output/archetypes/reviewer/ExplainAction_dna.json` | DNA (JSON) | Explanation review action | asset_optimizer.py, archetype_selector.py | **100% confidence** reviewer classification | Active | 0.95 |
| MessageAction_dna.json | `asset_processor/output/archetypes/reviewer/MessageAction_dna.json` | DNA (JSON) | Message review action | asset_optimizer.py, archetype_selector.py | **100% confidence** reviewer classification | Active | 0.95 |
| PreviewAction_dna.json | `asset_processor/output/archetypes/reviewer/PreviewAction_dna.json` | DNA (JSON) | Preview review action | asset_optimizer.py, archetype_selector.py | **100% confidence** reviewer classification | Active | 0.95 |

---

## Processor Assets (`asset_processor/`)

| Name | Location | Type | Purpose | Dependencies | Relationships | Status | Confidence |
|------|----------|------|---------|--------------|---------------|--------|------------|
| asset_optimizer.py | `core/prompts/asset_optimizer.py` | Processor (Python) | Converts raw DNA → optimized archetypes; scoring, classification, extraction | asset_loader.py, archetype_selector.py, adaptive_weights.py | Core pipeline component; produces optimized_archetypes.json | Active | 0.95 |
| asset_loader.py | `core/prompts/asset_loader.py` | Loader (Python) | Loads archetype assets from assets/raw/ and assets/optimized/ | optimized_archetypes.json, archetype_weights.json | Used by ArchetypeSelector at runtime | Active | 0.95 |
| archetype_selector.py | `core/prompts/archetype_selector.py` | Selector (Python) | Selects appropriate archetype per agent with adaptive weights | asset_loader.py, adaptive_weights.py | Runtime archetype resolution | Active | 0.95 |
| adaptive_weights.py | `core/prompts/adaptive_weights.py` | Weights (Python) | Dynamic weight adjustment based on performance feedback | archetype_weights.json | Feeds ArchetypeSelector for continuous improvement | Active | 0.90 |

---

## Summary Statistics

| Category | Total | Active | Archive Candidate | Deprecated | Delete Candidate | Unknown |
|----------|-------|--------|-------------------|------------|------------------|---------|
| Raw Registries | 3 | 0 | 3 | 0 | 0 | 0 |
| Optimized Assets | 2 | 2 | 0 | 0 | 0 | 0 |
| Architect DNA | 5 | 2 | 3 | 0 | 0 | 0 |
| Builder DNA | 30 | 11 | 19 | 0 | 0 | 0 |
| Governance Director DNA | 3 | 0 | 3 | 0 | 0 | 0 |
| Orchestrator DNA | 10 | 4 | 6 | 0 | 0 | 0 |
| Planner DNA | 4 | 2 | 2 | 0 | 0 | 0 |
| Researcher DNA | 2 | 1 | 1 | 0 | 0 | 0 |
| Reviewer DNA | 4 | 4 | 0 | 0 | 0 | 0 |
| Processor Components | 4 | 4 | 0 | 0 | 0 | 0 |
| **TOTAL** | **67** | **30** | **37** | **0** | **0** | **0** |

---

## Notes

- **Active** = Currently consumed by runtime (optimized_archetypes.json, high-confidence DNA files, processor components)
- **Archive Candidate** = Superseded by optimized pipeline, low classification confidence, or test artifacts (Poke_*, chat-titles, etc.)
- **No Deprecated/Delete Candidate** assets identified; all have traceability to source
- **Confidence** based on archetype_classification_report.json scores (100% = definitive classification)
- The 30 "Active" DNA files are the high-confidence (≥100% or clear signal) sources feeding optimized_archetypes.json
- The 37 "Archive Candidate" DNA files are low-confidence or test variants retained for provenance