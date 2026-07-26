# Constitutional Runtime Execution Pack

**Branch**: `implementation/constitutional-runtime`  
**Base Commit**: `2f3cb56`  
**Target**: Enforce Constitution in runtime — tenant isolation, monetary rules, agent identity, domain autonomy, governance enforcement  
**Swarm**: 5 agents (Infra, Payments, Auth, Governance, Monitoring)  
**Duration**: Parallel execution, zero handoffs

---

## 1. Tenant Context Middleware (PBI-001)

### Files to Create
```
core/middleware/tenant_context.py          # NEW: Extract tenant_id from JWT
core/persistence/tenant_session.py         # NEW: Tenant-scoped DB sessions
core/memory/namespaced_long_term_memory.py # NEW: tenant:{id}:memory keys
core/memory/namespaced_vector_store.py     # NEW: tenant:{id}:vector keys
core/auth/agent_identity.py                # NEW: Unique agent IDs, scoped JWTs
core/auth/allowlist_config.yaml            # NEW: Per-role tool allowlists
```

### Implementation Spec

**core/middleware/tenant_context.py**
```python
# Extract tenant_id from validated JWT, attach to request.state
from fastapi import Request, HTTPException
from core.auth.jwt_handler import decode_token

async def tenant_context_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return await call_next(request)  # Public endpoints
    
    token = auth_header.split(" ")[1]
    try:
        payload = decode_token(token)
        tenant_id = payload.get("tenant_id")
        agent_id = payload.get("agent_id")  # For agent-to-agent
        if not tenant_id:
            raise HTTPException(401, "Missing tenant_id in token")
        request.state.tenant_id = tenant_id
        request.state.agent_id = agent_id
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {e}")
    
    return await call_next(request)
```

**core/persistence/tenant_session.py**
```python
# Per-tenant SQLAlchemy session factory
from sqlalchemy.orm import sessionmaker
from core.persistence.session import engine

def get_tenant_session(tenant_id: str):
    # Option A: Shared DB with RLS (Row Level Security)
    session = SessionLocal()
    session.execute(text(f"SET LOCAL app.current_tenant = '{tenant_id}'"))
    return session

# Option B: Separate DB per tenant (for strict isolation)
def get_tenant_engine(tenant_id: str):
    url = f"postgresql://swarm:password@localhost:5432/swarm_{tenant_id}"
    return create_engine(url)
```

### Tests Required
- `tests/unit/test_tenant_context_middleware.py` — Token extraction, missing tenant_id, invalid token
- `tests/unit/test_tenant_session.py` — RLS enforcement, cross-tenant access denied

---

## 2. Monetary Rules Engine (PBI-006 through PBI-010)

### Files to Modify
```
core/services/payment_service.py             # EXTEND: Add 7 rules
core/services/monetary_rules.py              # NEW: Rules engine
core/services/reconciliation_job.py          # NEW: Celery periodic task
core/models/usage.py                         # EXTEND: agent_compute_hours field
core/services/allowlist_service.py           # NEW: Counterparty allowlists
```

### Implementation Spec

**core/services/monetary_rules.py**
```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class RailType(Enum):
    CUSTOMER_CARD = "stripe_card"
    AGENTIC_M2M = "agentic_stablecoin"

@dataclass
class MonetaryRuleConfig:
    session_cap_usd: float = 100.0
    allowlisted_counterparties: set = frozenset()
    dual_rail_required: bool = True
    audit_log_required: bool = True
    reconciliation_interval_minutes: int = 60

class MonetaryRulesEngine:
    def __init__(self, config: MonetaryRuleConfig):
        self.config = config
    
    def authorize_spend(self, agent_id: str, amount_usd: float, counterparty: str, rail: RailType) -> bool:
        # Rule 1: No standing spend authority
        if not self._has_active_session(agent_id):
            return False
        
        # Rule 2: Session cap
        if self._session_spend(agent_id) + amount_usd > self.config.session_cap_usd:
            return False
        
        # Rule 3: Allowlisted counterparties only
        if counterparty not in self.config.allowlisted_counterparties:
            return False
        
        # Rule 4: Dual-rail model
        if self.config.dual_rail_required:
            if rail == RailType.CUSTOMER_CARD and not self._is_customer_payment(counterparty):
                return False
            if rail == RailType.AGENTIC_M2M and self._is_customer_payment(counterparty):
                return False
        
        # Rule 5: Audit logging (always)
        self._audit_log(agent_id, amount_usd, counterparty, rail)
        
        return True
    
    def reconcile(self) -> ReconciliationReport:
        # Rule 6: Reconciliation as escalation trigger
        discrepancies = self._find_discrepancies()
        if discrepancies:
            self._escalate(discrepancies)
        return ReconciliationReport(discrepancies)
```

### Tests Required
- `tests/unit/test_monetary_rules.py` — 7 rules × 3 scenarios = 21 test cases

---

## 3. Domain Autonomy Gating (PBI-011)

### Files to Modify
```
core/orchestration/task_router.py              # EXTEND: domain_allowed check
core/orchestration/agent_domain_config.yaml    # NEW: Agent -> allowed domains
core/agents/base_agent.py                      # EXTEND: domain property
```

### Implementation Spec

**core/orchestration/task_router.py**
```python
# Add domain check before routing
async def route(self, task_name: str, input_data: dict, context: dict, trace_id: str):
    agent_name = self._get_route(task_name)
    agent = self.agent_manager.get_agent(agent_name)
    
    # NEW: Domain autonomy gating
    task_domain = self._classify_domain(task_name, input_data)
    if not self._domain_allowed(agent, task_domain):
        raise DomainViolationError(f"Agent {agent_name} not authorized for domain {task_domain}")
    
    return await agent.execute(input_data, context, trace_id)

def _domain_allowed(self, agent, domain: str) -> bool:
    allowed = self.domain_config.get(agent.name, {}).get("domains", [])
    return domain in allowed or "*" in allowed
```

**core/orchestration/agent_domain_config.yaml**
```yaml
StrategyAgent:
  domains: ["product_code", "simulation"]
OutreachAgent:
  domains: ["external_comms"]
BuilderAgent:
  domains: ["product_code"]
RepairAgent:
  domains: ["product_code"]
ReviewAgent:
  domains: ["product_code"]
GovernanceAgent:
  domains: ["*"]  # Full oversight
PaymentAgent:
  domains: ["financial"]
```

---

## 4. Governance Agent (PBI-016)

### Files to Create
```
core/agents/governance/
├── __init__.py
├── governance_agent.py
├── constitution_engine.py
├── template_registry.py
├── friction_tiers.py
├── trigger_evaluator.py
└── monetary_rules.py
```

### Implementation Spec

**core/agents/governance/constitution_engine.py**
```python
# Constitution as code — YAML/JSON, not PDF
class ConstitutionEngine:
    def __init__(self, constitution_path: str = "docs/governance/constitution.yaml"):
        self.rules = self._load_constitution(constitution_path)
    
    def check(self, action: AgentAction) -> ComplianceResult:
        # §3: Legible authorship
        if not action.agent_id or not action.trace_id:
            return ComplianceResult(False, "§3: Missing agent_id or trace_id")
        
        # §4.6: Portfolio isolation
        if action.accesses_data and not action.tenant_scoped:
            return ComplianceResult(False, "§4.6: Cross-tenant data access")
        
        # §5: Autonomy by domain
        if not self._domain_allowed(action.agent, action.domain):
            return ComplianceResult(False, f"§5: Domain {action.domain} not allowed for {action.agent}")
        
        # §12: Monetary rules
        if action.spend_usd and not self.monetary_rules.authorize(...):
            return ComplianceResult(False, "§12: Monetary rule violation")
        
        # §13: Agent identity
        if not action.agent_credentials or not action.allowlist_match:
            return ComplianceResult(False, "§13: Invalid agent identity")
        
        return ComplianceResult(True, "Compliant")
```

### Governance Agent Registration
```python
# In AgentManager initialization
agent_manager.register_agent(
    GovernanceAgent(
        name="governance",
        constitution_engine=ConstitutionEngine(),
        template_registry=TemplateRegistry(),
        friction_tiers=FrictionTiers(),
        trigger_evaluator=TriggerEvaluator(),
        monetary_rules=MonetaryRulesEngine()
    )
)
```

---

## 5. Audit Agent (PBI-017)

### Files to Create
```
core/agents/audit/
├── __init__.py
├── audit_agent.py
├── authorship_verifier.py
├── escalation_auditor.py
└── compliance_reporter.py
```

---

## 5. Monitoring Agent (PBI-018)

### Files to Create/Implement
```
core/monitoring/
├── __init__.py
├── health_dashboard.py          # IMPLEMENT: /health, /ready endpoints
├── metrics_collector.py         # IMPLEMENT: Prometheus /metrics
├── system_monitor.py            # IMPLEMENT: DB, Redis, agent health
├── alert_evaluator.py           # NEW: Alert rules
├── self_healer.py               # NEW: Auto-recovery triggers
├── compliance_runner.py         # NEW: Runs compliance test suite
└── alert_rules.yaml             # NEW: Alert definitions
```

---

## Parallel Execution Map

| Agent | Task | Depends On | Can Start |
|-------|------|------------|-----------|
| **InfraAgent** | Tenant middleware, DB scoping, memory namespaces, agent identity | None | **Immediate** |
| **PaymentsAgent** | 7 monetary rules, allowlists, dual-rail, reconciliation | PaymentService exists | **Immediate** |
| **InfraAgent** | Domain gating in TaskRouter, agent domain config | TaskRouter exists | **Immediate** |
| **InfraAgent** | Monitoring stubs → health, metrics, alerts, compliance runner | Stubs exist | **Immediate** |
| **SecurityAgent** | Cloud LLM fallback, httpOnly cookies, rate limiting, secret rotation | Auth system exists | **Immediate** |
| **GovAgent** | Constitution engine, template registry, friction tiers, triggers, monetary enforcement | Tenant context (A) | After InfraAgent |
| **AuditAgent** | Authorship verifier, escalation auditor, compliance reporter | GovAgent | After GovAgent |
| **MonitoringAgent** | Health checks, metrics, alerts, self-healer, compliance runner | Infra monitoring | **Immediate** |

---

## Acceptance Criteria

| Criterion | Verification |
|-----------|--------------|
| Cross-tenant DB access denied | Integration test: Tenant A cannot read Tenant B data |
| Monetary rules enforced | 21 test scenarios pass |
| Domain gating works | TaskRouter rejects unauthorized domain tasks |
| Governance pre-checks run | Every agent action checked before execution |
| Audit trail complete | All actions have trace_id, agent_id, tenant_id |
| Monitoring operational | /health, /metrics, alerts firing, self-healing triggers |

---

## Definition of Done

- [ ] All 5 infrastructure files created and tested
- [ ] 7 monetary rules implemented and tested (21 scenarios)
- [ ] Domain autonomy gating active in TaskRouter
- [ ] Monitoring endpoints live: `/health`, `/ready`, `/metrics`
- [ ] Constitutional compliance tests passing (10+ scenarios)
- [ ] GovernanceAgent, AuditAgent, MonitoringAgent registered and functional
- [ ] All streams A-E passing in CI