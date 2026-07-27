# Sprint 2 Closeout: Legacy Test Recovery & Governance Integration

**Date:** 2026-07-26
**Branch:** `implementation/constitutional-runtime`
**Head:** `392f9e8` (Sprint 1 baseline) + uncommitted Sprint 2 changes

---

## Executive Summary

Sprint 2 recovered 27 legacy unit tests (AgentManager, Scheduler, TaskRouter) and brought them into the constitutional runtime architecture. All 78 tests now pass — 27 legacy + 51 constitutional compliance — a 100% pass rate. No regressions were introduced.

---

## What Was Done

### 1. AgentManager Rewrite (`core/orchestration/agent_manager.py`)

| Change | Detail |
|---|---|
| `register_agent` | Now validates agent identity via `AgentIdentityRegistry.get()` before registration. Rejects missing/invalid identities per §13. |
| Domain resolution | When no domain is passed, derives domain from the agent's identity (first `AgentDomain` enum value), defaulting to `"simulation"`. |
| `execute_agent` | Calls `agent(input_data, context)` for both sync and async handlers (async wrapped via `await`). No longer looks for `.run()` method. |
| Governance integration | Runs `governance_agent.pre_check()` before every execution. Rejects non-compliant actions with error message. |
| Fixture compatibility | Works with `conftest.py` fixture order: `AgentManager()` created first (loads `DEFAULT_AGENT_CONFIG`), then test identities registered via `_register_test_identities()`. |

### 2. Scheduler Fix (`core/orchestration/scheduler.py`)

| Change | Detail |
|---|---|
| Handler invocation | Changed from `task.handler(**task.context)` to `task.handler(task.context, ctx)` — passes context dict as first arg and metadata dict as second. Matches `handler(data, context)` convention used by AgentManager. |
| Immediate execution | `schedule()` still uses `asyncio.ensure_future` for immediate tasks; the fix was only in the calling convention. |

### 3. TaskRouter Fix (`core/orchestration/task_router.py`)

| Change | Detail |
|---|---|
| `_domain_allowed` | Rewired from `self.domain_config` lookup to `AgentIdentityRegistry` lookup, ensuring domain autonomy checks go through the same identity registry used by GovernanceAgent. |
| `get_agent_for_domain` | Fixed return value — was returning the domain name instead of the agent name. Now returns `agent` (the agent name). |
| `register_agent_domains` | Unchanged. Domain config now used for route fallback lookup, not for permission checks. |

### 4. GovernanceAgent (`core/agents/governance/governance_agent.py`)

| Change | Detail |
|---|---|
| Identity loading | `__init__` now loads `DEFAULT_AGENT_CONFIG` only if `AgentIdentityRegistry._identities` is empty (additive, not destructive). Prevents wiping identities already loaded by `AgentManager.__init__`. |
| Removed | Redundant `AgentIdentityRegistry.load_from_config()` call. |

### 5. Test Infrastructure (`tests/`)

| File | Change |
|---|---|
| `conftest.py` | Added `reset_identity_registry` (autouse fixture), `_register_test_identities()`, and `agent_manager` fixture that orders: reset → AgentManager → register test identities. Added `router` fixture. |
| `test_agent_manager.py` | 10 tests: registration, execution (async + sync), identity enforcement, duplicate/missing identity errors, unregister. |
| `test_scheduler.py` | 8 tests: schedule/execute, list, cancel, sync handlers, failure isolation, voice session lifecycle, cleanup. |
| `test_task_router.py` | 9 tests: route resolution, missing routes, domain classification, domain gating, violations, unregister, duplicates. |

---

## Test Results

| Test Suite | Tests | Passed | Failed |
|---|---|---|---|
| `test_agent_manager.py` | 10 | 10 | 0 |
| `test_scheduler.py` | 8 | 8 | 0 |
| `test_task_router.py` | 9 | 9 | 0 |
| `test_constitutional_compliance.py` | 51 | 51 | 0 |
| **Total** | **78** | **78** | **0** |

---

## Key Architectural Decisions

1. **AgentIdentityRegistry as single source of truth** for domain permissions. Both `TaskRouter._domain_allowed` and `GovernanceAgent.pre_check` use it, ensuring consistent enforcement.
2. **GovernanceAgent is additive** — it doesn't clear identities on init, preventing race conditions with AgentManager setup.
3. **Handler convention standardized** to `handler(input_data, context)` across AgentManager and Scheduler.
4. **Domain auto-resolution** — agents default to their identity's first domain when none is specified at registration time.

---

## Remaining Work (Post-Sprint 2)

1. **Wire GovernanceAgent/AuditAgent/MonitoringAgent** into AgentManager execution path (Phase 3)
2. **Security hardening** — JWT auth, rate limiting, input sanitization
3. **Voice system integration** — ElevenLabs STT/TTS pipeline
4. **Frontend validation** — React form validation, error boundaries, auth flows
5. **Full regression suite** — Run all `tests/` including integration tests

---

## Files Changed

```
M  core/agents/governance/governance_agent.py      (identity loading fix)
M  core/orchestration/agent_manager.py              (rewrite: identity validation, domain resolution, governance integration)
M  core/orchestration/scheduler.py                  (handler calling convention fix)
M  core/orchestration/task_router.py                (domain_allowed via identity registry, get_agent_for_domain fix)
M  tests/conftest.py                                (fixture infrastructure for identity registration)
M  tests/unit/test_agent_manager.py                 (10 new tests)
M  tests/unit/test_scheduler.py                     (8 new tests)
M  tests/unit/test_task_router.py                   (9 new tests)
M  data/long_term_memory.json                       (state changes)
```

---

## Rollback

To revert Sprint 2 changes:

```bash
git checkout 392f9e8 -- core/ core/agents/governance/ tests/ data/long_term_memory.json
```
