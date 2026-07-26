# Branch Contracts

**Objective**: Define immutable contracts between all implementation branches. No ambiguity. No drift.

---

## Branch Architecture

```
main (protected)
├── backup/intelligence-baseline-2026-07-26 (immutable)
├── implementation/genesis-launch-ready (constitutional runtime)
│   ├── implementation/voice-and-growth (voice + growth agents)
│   └── implementation/frontend-premium (premium UX)
└── release/genesis-v1.0.0 (launch tag)
```

---

## 1. implementation/genesis-launch-ready

### Contract
| Aspect | Requirement |
|--------|-------------|
| **Base** | `backup/intelligence-baseline-2026-07-26` |
| **Merge Target** | `release/genesis-v1.0.0` |
| **Protection** | No direct pushes, PR required, 1 approval |
| **CI Gates** | All 559 tests pass, 86% coverage, constitutional compliance tests, tenant isolation tests, monetary rules tests, domain autonomy tests |

### Owned Code
```
core/middleware/tenant_context_middleware.py
core/persistence/tenant_scoped_session.py
core/memory/namespaced_long_term_memory.py
core/memory/namespaced_vector_store.py
core/auth/agent_identity.py
core/services/payment_service.py (monetary rules)
core/orchestration/task_router.py (domain gating)
core/monitoring/health_dashboard.py
core/monitoring/metrics_collector.py
core/monitoring/system_monitor.py
tests/unit/test_constitutional_compliance.py
tests/unit/test_monetary_rules.py
tests/unit/test_tenant_isolation.py
tests/unit/test_domain_autonomy.py
core/agents/governance/governance_agent.py
core/agents/audit/audit_agent.py
core/agents/monitoring/monitoring_agent.py
```

### Must Not Touch
- `frontend/src/` (separate branch)
- `core/agents/voice/` (separate branch)
- `core/agents/landing/`, `core/agents/onboarding/`, `core/agents/seo/`, `core/agents/content/`, `core/agents/growth/` (separate branch)

---

## 2. implementation/voice-and-growth

### Contract
| Aspect | Requirement |
|--------|-------------|
| **Base** | `implementation/genesis-launch-ready` (after merge) |
| **Merge Target** | `implementation/genesis-launch-ready` |
| **Protection** | PR required, 1 approval, voice integration tests pass |
| **CI Gates** | Voice latency <200ms, barge-in <100ms, session resume works, 4 flows execute, SEO pages generate, content generates |

### Owned Code
```
core/agents/voice/voice_agent.py
core/orchestration/voice_orchestrator.py
core/orchestration/voice_session_manager.py
core/memory/conversation_memory_adapter.py
core/integrations/elevenlabs/elevenlabs_client.py
core/integrations/elevenlabs/__init__.py
core/integrations/__init__.py
core/agents/voice/__init__.py
core/agents/voice/voice_analytics.py
core/agents/landing/landing_agent.py
core/agents/landing/flows/lead_qualification.py
core/agents/landing/flows/founder_discovery.py
core/agents/landing/flows/business_launch.py
core/agents/landing/flows/product_recommendation.py
core/agents/onboarding/onboarding_agent.py
core/agents/seo/seo_agent.py
core/agents/content/content_agent.py
core/agents/growth/growth_agent.py
core/agents/voice/voice_analytics.py
```

### Must Not Touch
- `frontend/src/` (separate branch)
- `core/monitoring/` (constitutional branch)
- `core/agents/governance/`, `core/agents/audit/`, `core/agents/monitoring/` (constitutional branch)
- `core/middleware/`, `core/persistence/`, `core/memory/`, `core/auth/` (constitutional branch)

---

## 3. implementation/frontend-premium

### Contract
| Aspect | Requirement |
|--------|-------------|
| **Base** | `implementation/genesis-launch-ready` (after merge) |
| **Merge Target** | `implementation/genesis-launch-ready` |
| **Protection** | PR required, 1 approval, LCP <2.5s, CLS <0.1, accessibility audit pass |
| **CI Gates** | Lighthouse CI, Playwright E2E, accessibility audit, bundle size <500KB |

### Owned Code
```
frontend/src/design-system/tokens/* (6 files)
frontend/src/design-system/components/* (8 files)
frontend/src/design-system/animations/* (5 files)
frontend/src/components/voice/* (7 files)
frontend/src/components/landing/* (5 files)
frontend/src/components/onboarding/* (5 files)
frontend/src/components/dashboard/* (6 files)
frontend/src/components/seo/* (4 files)
frontend/src/app/page.tsx (landing)
frontend/src/app/voice-demo/page.tsx
frontend/src/app/onboarding/page.tsx
frontend/src/app/pricing/page.tsx
frontend/src/app/dashboard/page.tsx
frontend/src/app/agents/page.tsx
frontend/src/app/templates/[industry]/page.tsx
frontend/src/app/use-cases/[problem]/page.tsx
frontend/src/app/templates/[type]/page.tsx
frontend/src/app/vs/[competitor]/page.tsx
frontend/src/app/glossary/[term]/page.tsx
frontend/src/app/layout.tsx (updated)
frontend/src/app/robots.ts
frontend/src/app/sitemap.ts
frontend/src/components/layout/app-shell.tsx (updated)
frontend/src/components/layout/sidebar.tsx (updated)
frontend/src/lib/api.ts (updated)
```

### Must Not Touch
- `core/` (constitutional + voice branches)
- `core/agents/` (voice + growth branches)
- `.github/workflows/` (shared, coordinate changes)

---

## Cross-Branch Dependencies

### Required Merge Order
```
1. implementation/genesis-launch-ready → release/genesis-v1.0.0
2. implementation/voice-and-growth → implementation/genesis-launch-ready
3. implementation/frontend-premium → implementation/genesis-launch-ready
```

### Dependency Graph
```
implementation/genesis-launch-ready
    │
    ├── provides: tenant context middleware
    ├── provides: monetary rules engine
    ├── provides: agent identity system
    ├── provides: domain autonomy gating
    ├── provides: monitoring infrastructure
    ├── provides: governance/audit/monitoring agents
    │
    └── required by: implementation/voice-and-growth
    │       needs: tenant context for voice sessions
    │       needs: GovernanceAgent for compliance
    │       needs: MonitoringAgent for voice metrics
    │
    └── required by: implementation/frontend-premium
            needs: tenant context for frontend
            needs: API contracts from constitutional runtime
            needs: voice WebSocket endpoints
            needs: authentication (httpOnly cookies)
```

### Conflict Zones (Coordinate)

| File | Branches | Resolution |
|------|----------|------------|
| `core/agents/base_agent.py` | constitutional, voice-and-growth | Constitutional owns base; voice extends |
| `core/orchestration/task_router.py` | constitutional, voice-and-growth | Constitutional owns domain gating; voice adds routing |
| `core/orchestration/scheduler.py` | constitutional, voice-and-growth | Constitutional owns scheduling; voice adds session mgmt |
| `core/memory/long_term_memory/long_term_memory.py` | constitutional, voice-and-growth | Constitutional owns namespace; voice adds adapter |
| `core/agents/outreach/outreach_agent.py` | constitutional, voice-and-growth | Constitutional owns base; voice specializes |
| `frontend/src/lib/api.ts` | voice-and-growth, frontend-premium | Voice adds WebSocket; frontend consumes |
| `.github/workflows/tests.yml` | All branches | Coordinate via PR comments |

---

## Merge Rules

### Never Merge Without
- [ ] All CI gates passing
- [ ] 1 approval from different branch owner
- [ ] No merge conflicts
- [ ] Updated CHANGELOG.md
- [ ] Version bump in `pyproject.toml` / `package.json`

### Fast-Forward Only
- All merges to `implementation/genesis-launch-ready` must be fast-forward
- Use `git merge --ff-only` or rebase
- No merge commits on integration branches

### Rollback Procedure
```bash
# If any branch breaks genesis-launch-ready
git checkout implementation/genesis-launch-ready
git reset --hard backup/intelligence-baseline-2026-07-26
git push --force-with-lease origin implementation/genesis-launch-ready
```

---

## Release Branch: release/genesis-v1.0.0

### Creation
```bash
git checkout implementation/genesis-launch-ready
git checkout -b release/genesis-v1.0.0
git push -u origin release/genesis-v1.0.0
```

### Gates
- [ ] All implementation branches merged
- [ ] Beta customers onboarded (min 3)
- [ ] Load test: 100 concurrent tenants, 1000 agents
- [ ] Security audit passed
- [ ] Legal/compliance review passed
- [ ] Documentation complete

### Release Tag
```bash
git tag -a v1.0.0 -m "Genesis v1.0.0 — Constitutional autonomous business launch platform"
git push origin v1.0.0
```

---

## Branch Ownership

| Branch | Owner | Backup |
|--------|-------|--------|
| `implementation/genesis-launch-ready` | Platform Lead | Chief Architect |
| `implementation/voice-and-growth` | Voice Lead | Growth Lead |
| `implementation/frontend-premium` | Frontend Lead | Design Lead |
| `release/genesis-v1.0.0` | Release Manager | CTO |

---

## Communication Protocol

| Event | Channel | Recipients |
|-------|---------|------------|
| Branch created | Slack #genesis-branches | All leads |
| PR opened | GitHub + Slack #genesis-prs | All leads |
| CI failure | GitHub + Slack #genesis-ci | Branch owner + Platform Lead |
| Merge conflict | GitHub + Slack #genesis-conflicts | Both branch owners + Platform Lead |
| Merge complete | GitHub + Slack #genesis-merges | All leads |
| Release candidate | Slack #genesis-release | All leads + CTO |

---

## Enforcement

**Any violation of these contracts = immediate halt.**

The Platform Lead has authority to:
- Revert any merge violating contracts
- Freeze any branch violating contracts
- Require rebase before any merge

**No exceptions. No "just this once."**