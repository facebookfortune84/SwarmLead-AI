# Repository Cleanup Report

**Date:** 2026-07-26
**Audit scope:** Full repository scan

---

## SECTION 1 — Dead Code (REMOVE)

### `integrations/` (root level)
5 files, 4 empty subdirectories (crm, email, linkedin, telephony), all with only `__init__.py`. No runtime code references any file in this package. Real integrations live in `core/integrations/elevenlabs/` and `infrastructure/`.
- **Action:** DELETE entire directory

### `scripts/`
Contains only `__init__.py`. No runtime code references it.
- **Action:** DELETE entire directory

### `archive/frontend-v1/`
Empty directory.
- **Action:** DELETE directory

### `core/agents/landing/flows/`
Empty directory.
- **Action:** DELETE directory

### `core/persistence/tenant_session/`
Empty directory.
- **Action:** DELETE directory

### `data_vault/`
Empty directory (archetypes/, logs/, training/ — all empty).
- **Action:** DELETE entire directory

---

## SECTION 2 — Stray Root Files (RELOCATE)

### `fix_encoding.py`
Utility script at repository root. Not referenced by any runtime code.
- **Action:** MOVE to `scripts/` (before deleting scripts/ entirely) or delete if not needed

### `migration_state.json`
Alembic migration metadata. Belongs with migrations.
- **Action:** KEEP at root

---

## SECTION 3 — Historical Archives (ARCHIVE)

### `archive/migration_artifacts/`
SQL backup, migration tools, migration reports from SQLite→Postgres migration. Historical value only.
- **Action:** ARCHIVE — move contents to `archive/migration/` or delete backup SQL

---

## SECTION 4 — Untracked Empty Directories (CLEAN UP)

These are empty and untracked:
- `asset_processor/output/archetypes/executive/`
- `asset_processor/output/archetypes/memory_manager/`
- `asset_processor/output/archetypes/optimizer/`
- `project-handoff/agent-bootstrap/`
- `project-handoff/architecture/`
- `project-handoff/handoff-package/`
- `project-handoff/knowledge-graph/`
- `project-handoff/production-sprint/`

- **Action:** DELETE all empty directories

---

## SECTION 5 — Gitignore Gaps (FIX)

### `.mypy_cache/`
Not in `.gitignore`. Should be added.
- **Action:** ADD to `.gitignore`

### `data/swarmlead.db`
Already gitignored by `*.db` pattern ✅

### `__pycache__/`
Already gitignored ✅

### `.aider*`
Already gitignored ✅

### `logs/`
Already gitignored ✅

### `venv/`
Already gitignored (via `venv/` pattern) ✅

### `asset_processor/output/`
Not gitignored. All 58 archetype DNA JSON files (112KB) are untracked — they are generated artifacts.
- **Action:** Already untracked. No action needed unless they should be excluded.

---

## SECTION 6 — Asset System (REVIEW)

### `asset_processor/output/archetypes/`
58 DNA JSON files (112KB total), 10 archetype categories. These are agent prompt files used by the asset system. The runtime code (`core/prompts/asset_loader.py`) references `assets/optimized/optimized_archetypes.json`, not these raw DNAs.
- **Action:** See Phase 2 for archive plan

### `assets/optimized/`
2 files: `archetype_weights.json`, `optimized_archetypes.json`. These ARE referenced by runtime.
- **Action:** KEEP

### `assets/raw/`
3 files: `agent_registry.json`, `archetype_classification_report.json`, `archetype_registry.json`.
- **Action:** KEEP

---

## SECTION 7 — Documentation Organization

### `docs/` vs `project-handoff/`
- `docs/` — 53 markdown files (ADR, agents, founder, governance, knowledge, operations). These are living architectural documentation.
- `project-handoff/` — 23 entries including sprint reviews, release docs, launch reports, planning artifacts. Some subdirectories are empty or obsolete.
- **Action:** Keep both directories. `docs/` = living docs. `project-handoff/` = release/handoff artifacts. The structure is correct.
- **Action:** DELETE empty project-handoff subdirectories (agent-bootstrap/, architecture/, handoff-package/, knowledge-graph/, production-sprint/)

---

## SECTION 8 — Summary of Actions

| # | Item | Action | Risk |
|---|---|---|---|
| 1 | `integrations/` | DELETE | None (dead code) |
| 2 | `scripts/` | DELETE | None (empty) |
| 3 | `archive/frontend-v1/` | DELETE | None (empty) |
| 4 | `core/agents/landing/flows/` | DELETE | None (empty) |
| 5 | `core/persistence/tenant_session/` | DELETE | None (empty) |
| 6 | `data_vault/` | DELETE | None (empty) |
| 7 | `fix_encoding.py` | DELETE or move | Low (stray utility) |
| 8 | `.mypy_cache/` → `.gitignore` | ADD | None |
| 9 | Empty project-handoff subdirs | DELETE | None |
| 10 | `asset_processor/output/archetypes/` | ARCHIVE to D:\ | Low (generated artifacts, not referenced by runtime) |

All actions are safe — no runtime code, tests, or configurations reference any of these items.
