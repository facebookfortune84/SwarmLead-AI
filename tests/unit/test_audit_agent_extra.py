import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

# Ensure repo root is on sys.path so `core` package can be imported in tests
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from core.agents.audit.audit_agent import (
    AuditActionRequest,
    AuditAgent,
    AuditEntry,
    AuditEventType,
    AuthorshipVerifier,
    ComplianceReporter,
    EscalationAuditor,
    EscalationEventRequest,
    agent_report,
    audit_agent,
    audit_escalation,
    audit_log,
    constitutional_report,
    monetary_report,
    verify_action,
)
from core.auth.agent_identity import AgentDomain, AgentIdentity, AgentIdentityRegistry

VALID_UUID = "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture(autouse=True)
def registered_identities():
    AgentIdentityRegistry._identities.clear()
    AgentIdentityRegistry.register(
        AgentIdentity(
            agent_id="strategy_agent",
            agent_type="StrategyAgent",
            display_name="Strategy Agent",
            domains={AgentDomain.PRODUCT_CODE, AgentDomain.SIMULATION},
            tool_allowlist={"call_llm", "read_memory"},
            data_allowlist={"strategy", "market_data"},
        )
    )
    yield
    AgentIdentityRegistry._identities.clear()


def make_action(**overrides):
    action = {
        "agent_id": "strategy_agent",
        "trace_id": VALID_UUID,
        "timestamp": datetime.utcnow().isoformat(),
        "anonymous": False,
    }
    action.update(overrides)
    return action


def make_escalation(**overrides):
    escalation = {
        "trigger": "dollar_value",
        "escalated_by": "payment_agent",
        "escalated_to": "governance_agent",
        "reason": "Spend exceeds threshold",
        "emergency_stop": False,
        "graceful_wind_down": True,
        "human_involved": True,
    }
    escalation.update(overrides)
    return escalation


# ---------------------------------------------------------------------------
# AuditEventType enum
# ---------------------------------------------------------------------------


def test_audit_event_type_values():
    assert AuditEventType.AGENT_ACTION.value == "agent_action"
    assert AuditEventType.HUMAN_REVIEW.value == "human_review"
    assert AuditEventType.MONETARY_TRANSACTION.value == "monetary_transaction"
    assert AuditEventType.TENANT_OPERATION.value == "tenant_operation"
    assert AuditEventType.CONSTITUTIONAL_CHECK.value == "constitutional_check"
    assert AuditEventType.ESCALATION.value == "escalation"
    assert AuditEventType.IDENTITY_VERIFICATION.value == "identity_verification"


# ---------------------------------------------------------------------------
# AuditEntry
# ---------------------------------------------------------------------------


def test_audit_entry_to_dict():
    ts = datetime(2024, 1, 1, 12, 0, 0)
    entry = AuditEntry(
        event_id="evt_1",
        event_type=AuditEventType.AGENT_ACTION,
        timestamp=ts,
        agent_id="strategy_agent",
        trace_id=VALID_UUID,
        tenant_id="tenant_1",
        action="generate",
        input_data={"prompt": "hi"},
        output_data={"text": "ok"},
        compliance_result={"valid": True},
        human_reviewer="human@example.com",
        audit_trail_hash="abc123",
    )
    result = entry.to_dict()
    assert result["event_id"] == "evt_1"
    assert result["event_type"] == "agent_action"
    assert result["timestamp"] == "2024-01-01T12:00:00"
    assert result["agent_id"] == "strategy_agent"
    assert result["trace_id"] == VALID_UUID
    assert result["tenant_id"] == "tenant_1"
    assert result["action"] == "generate"
    assert result["input_data"] == {"prompt": "hi"}
    assert result["output_data"] == {"text": "ok"}
    assert result["compliance_result"] == {"valid": True}
    assert result["human_reviewer"] == "human@example.com"
    assert result["audit_trail_hash"] == "abc123"


def test_audit_entry_defaults():
    entry = AuditEntry(
        event_id="evt_2",
        event_type=AuditEventType.ESCALATION,
        timestamp=datetime.utcnow(),
        agent_id=None,
        trace_id="t",
        tenant_id=None,
        action="escalate",
        input_data={},
        output_data={},
        compliance_result={},
    )
    assert entry.human_reviewer is None
    assert entry.audit_trail_hash == ""


# ---------------------------------------------------------------------------
# AuthorshipVerifier
# ---------------------------------------------------------------------------


def test_authorship_verify_valid():
    verifier = AuthorshipVerifier()
    result = verifier.verify(make_action())
    assert result["valid"] is True
    assert result["violations"] == []
    assert result["details"]["agent_id"] == "strategy_agent"
    assert result["details"]["trace_id"] == VALID_UUID


@pytest.mark.parametrize("field", ["agent_id", "trace_id", "timestamp"])
def test_authorship_verify_missing_required_field(field):
    verifier = AuthorshipVerifier()
    action = make_action()
    action[field] = None
    result = verifier.verify(action)
    assert result["valid"] is False
    assert f"Missing required field: {field}" in result["violations"]


def test_authorship_verify_empty_action():
    verifier = AuthorshipVerifier()
    result = verifier.verify({})
    assert result["valid"] is False
    assert result["violations"] == ["Missing required field: agent_id"]


def test_authorship_verify_unknown_agent():
    verifier = AuthorshipVerifier()
    result = verifier.verify(make_action(agent_id="ghost_agent"))
    assert result["valid"] is False
    assert "Unknown agent: ghost_agent" in result["violations"]


def test_authorship_verify_invalid_trace_id_format():
    verifier = AuthorshipVerifier()
    result = verifier.verify(make_action(trace_id="trace_123"))
    assert result["valid"] is False
    assert "Invalid trace_id format" in result["violations"]


def test_authorship_verify_expired_identity():
    verifier = AuthorshipVerifier()
    expired = AgentIdentity(
        agent_id="expired_agent",
        agent_type="TestAgent",
        display_name="Expired",
        expires_at=datetime(2020, 1, 1),
        is_active=True,
    )
    AgentIdentityRegistry.register(expired)
    result = verifier.verify(make_action(agent_id="expired_agent"))
    assert result["valid"] is False
    assert "Agent identity invalid or expired: expired_agent" in result["violations"]


def test_authorship_verify_anonymous():
    verifier = AuthorshipVerifier()
    result = verifier.verify(make_action(anonymous=True))
    assert result["valid"] is False
    assert "Anonymous actions prohibited per §3" in result["violations"]


def test_is_valid_uuid_variants():
    verifier = AuthorshipVerifier()
    assert verifier._is_valid_uuid(VALID_UUID) is True
    assert verifier._is_valid_uuid("not-a-uuid") is False
    assert verifier._is_valid_uuid("") is False
    assert verifier._is_valid_uuid(None) is False


def test_log_authorship_appends_entry():
    verifier = AuthorshipVerifier()
    action = make_action()
    verifier.log_authorship(action)
    assert len(verifier.authorship_log) == 1
    entry = verifier.authorship_log[0]
    assert entry["event_type"] == "authorship_verified"
    assert entry["action"] == action
    assert entry["event_id"].startswith("auth_")


# ---------------------------------------------------------------------------
# EscalationAuditor
# ---------------------------------------------------------------------------


def test_escalation_audit_valid():
    auditor = EscalationAuditor()
    result = auditor.audit_escalation(make_escalation())
    assert result["valid"] is True
    assert result["violations"] == []


@pytest.mark.parametrize("field", ["trigger", "escalated_by", "escalated_to", "reason"])
def test_escalation_audit_missing_required_field(field):
    auditor = EscalationAuditor()
    escalation = make_escalation()
    escalation[field] = ""
    result = auditor.audit_escalation(escalation)
    assert result["valid"] is False
    assert f"Missing required field: {field}" in result["violations"]


def test_escalation_audit_invalid_trigger():
    auditor = EscalationAuditor()
    result = auditor.audit_escalation(make_escalation(trigger="bogus_trigger"))
    assert result["valid"] is False
    assert "Invalid trigger: bogus_trigger" in result["violations"]


def test_escalation_audit_emergency_stop_requires_wind_down():
    auditor = EscalationAuditor()
    result = auditor.audit_escalation(
        make_escalation(emergency_stop=True, graceful_wind_down=False)
    )
    assert result["valid"] is False
    assert "Emergency stop requires graceful wind-down per §6" in result["violations"]


def test_escalation_audit_emergency_stop_with_wind_down():
    auditor = EscalationAuditor()
    result = auditor.audit_escalation(make_escalation(emergency_stop=True, graceful_wind_down=True))
    assert result["valid"] is True


def test_escalation_audit_requires_human_involvement():
    auditor = EscalationAuditor()
    result = auditor.audit_escalation(make_escalation(human_involved=False))
    assert result["valid"] is False
    assert "Escalation requires human involvement" in result["violations"]


def test_escalation_audit_logs_entry():
    auditor = EscalationAuditor()
    escalation = make_escalation()
    auditor.audit_escalation(escalation)
    assert len(auditor.escalation_log) == 1
    entry = auditor.escalation_log[0]
    assert entry["event_type"] == "escalation_audit"
    assert entry["event"] == escalation
    assert entry["result"]["valid"] is True
    assert entry["event_id"].startswith("esc_")


# ---------------------------------------------------------------------------
# ComplianceReporter
# ---------------------------------------------------------------------------


def test_generate_constitutional_report():
    reporter = ComplianceReporter()
    start = datetime.utcnow() - timedelta(days=7)
    end = datetime.utcnow()
    report = reporter.generate_constitutional_compliance_report(start, end)
    assert report["period"] == {
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
    assert report["sections"]["legible_authorship"] == {"compliant": True, "violations": 0}
    assert report["sections"]["monetary_rules"] == {"compliant": True, "violations": 0}
    assert report["summary"]["compliance_rate"] == 100.0
    assert "generated_at" in report


def test_generate_agent_activity_report_known_agent():
    reporter = ComplianceReporter()
    start = datetime.utcnow() - timedelta(days=7)
    end = datetime.utcnow()
    report = reporter.generate_agent_activity_report("strategy_agent", start, end)
    assert report["agent_id"] == "strategy_agent"
    assert report["agent_type"] == "StrategyAgent"
    assert report["period"]["start"] == start.isoformat()
    assert report["actions_count"] == 0
    assert set(report["domains_accessed"]) == {
        AgentDomain.PRODUCT_CODE,
        AgentDomain.SIMULATION,
    }
    assert set(report["tools_used"]) == {"call_llm", "read_memory"}
    assert set(report["data_accessed"]) == {"strategy", "market_data"}
    assert report["compliance_rate"] == 100.0


def test_generate_agent_activity_report_unknown_agent():
    reporter = ComplianceReporter()
    report = reporter.generate_agent_activity_report("nobody", datetime.utcnow(), datetime.utcnow())
    assert report == {"error": "Unknown agent: nobody"}


def test_generate_monetary_report():
    reporter = ComplianceReporter()
    start = datetime.utcnow() - timedelta(days=30)
    end = datetime.utcnow()
    report = reporter.generate_monetary_audit_report(start, end)
    assert report["period"]["start"] == start.isoformat()
    assert report["rules"]["no_standing_spend"] == {"compliant": True, "violations": 0}
    assert report["rules"]["dual_rail_model"] == {"compliant": True, "violations": 0}
    assert report["transactions"] == {"total": 0, "total_usd": 0.0, "failed": 0, "escalated": 0}
    assert "generated_at" in report


# ---------------------------------------------------------------------------
# AuditAgent
# ---------------------------------------------------------------------------


def test_audit_agent_init():
    agent = AuditAgent()
    assert isinstance(agent.authorship, AuthorshipVerifier)
    assert isinstance(agent.escalation, EscalationAuditor)
    assert isinstance(agent.reporter, ComplianceReporter)
    assert agent.audit_log == []


def test_audit_action_valid():
    agent = AuditAgent()
    result = agent.audit_action(make_action())
    assert result["valid"] is True
    assert result["violations"] == []
    assert result["audit_entry"]["valid"] is True


def test_audit_action_invalid():
    agent = AuditAgent()
    result = agent.audit_action(make_action(anonymous=True))
    assert result["valid"] is False
    assert "Anonymous" in result["violations"][0]


def test_audit_escalation_delegates():
    agent = AuditAgent()
    result = agent.audit_escalation(make_escalation())
    assert result["valid"] is True


def test_generate_reports():
    agent = AuditAgent()
    start = datetime.utcnow() - timedelta(days=7)
    end = datetime.utcnow()
    reports = agent.generate_reports(start, end)
    assert "constitutional_compliance" in reports
    assert "monetary_audit" in reports
    assert "generated_at" in reports
    assert reports["constitutional_compliance"]["period"]["start"] == start.isoformat()


def test_get_agent_report():
    agent = AuditAgent()
    report = agent.get_agent_report("strategy_agent", datetime.utcnow(), datetime.utcnow())
    assert report["agent_id"] == "strategy_agent"


def test_get_audit_log_empty():
    agent = AuditAgent()
    assert agent.get_audit_log() == []


def test_get_audit_log_limit():
    agent = AuditAgent()
    agent.audit_log = [{"n": i} for i in range(10)]
    assert len(agent.get_audit_log(3)) == 3
    assert agent.get_audit_log(3)[0] == {"n": 7}
    assert agent.get_audit_log() == agent.audit_log


def test_get_audit_log_zero_limit():
    agent = AuditAgent()
    agent.audit_log = [{"n": i} for i in range(5)]
    assert agent.get_audit_log(0) == agent.audit_log


@pytest.mark.asyncio
async def test_run_verify_with_action():
    agent = AuditAgent()
    result = await agent.run({"verify": True, "action": make_action()})
    assert result["valid"] is True


@pytest.mark.asyncio
async def test_run_verify_without_action_builds_fallback():
    agent = AuditAgent()
    result = await agent.run(
        {"verify": True, "agent_id": "strategy_agent", "trace_id": VALID_UUID},
        trace_id=VALID_UUID,
    )
    assert "valid" in result
    assert result["valid"] is True


@pytest.mark.asyncio
async def test_run_verify_fallback_unknown_agent():
    agent = AuditAgent()
    result = await agent.run({"verify": True})
    assert result["valid"] is False
    assert "Missing required field: trace_id" in result["violations"]


@pytest.mark.asyncio
async def test_run_verify_uses_trace_id_arg():
    agent = AuditAgent()
    result = await agent.run({"verify": True, "agent_id": "strategy_agent"}, trace_id=VALID_UUID)
    assert result["valid"] is True


@pytest.mark.asyncio
async def test_run_summary():
    agent = AuditAgent()
    result = await agent.run()
    assert result["role"] == "Audit Agent"
    assert "constitutional_compliance" in result["reports"]
    assert "ADR-001" in result["summary"]


# ---------------------------------------------------------------------------
# Router endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_action_endpoint():
    request = AuditActionRequest(
        agent_id="strategy_agent",
        trace_id=VALID_UUID,
        action="generate",
        input_data={},
        output_data={},
        compliance_result={},
    )
    result = await verify_action(request)
    assert "valid" in result
    assert result["valid"] is False
    assert any("timestamp" in v for v in result["violations"])


@pytest.mark.asyncio
async def test_audit_escalation_endpoint():
    request = EscalationEventRequest(
        trigger="dollar_value",
        escalated_by="payment_agent",
        escalated_to="governance_agent",
        reason="threshold",
    )
    result = await audit_escalation(request)
    assert result["valid"] is True


@pytest.mark.asyncio
async def test_constitutional_report_endpoint():
    result = await constitutional_report("2024-01-01", "2024-01-08")
    assert "sections" in result
    assert result["period"]["start"] == "2024-01-01T00:00:00"


@pytest.mark.asyncio
async def test_monetary_report_endpoint():
    result = await monetary_report("2024-01-01", "2024-01-08")
    assert "rules" in result
    assert "transactions" in result


@pytest.mark.asyncio
async def test_agent_report_endpoint_known():
    result = await agent_report("strategy_agent", "2024-01-01", "2024-01-08")
    assert result["agent_id"] == "strategy_agent"


@pytest.mark.asyncio
async def test_agent_report_endpoint_unknown():
    result = await agent_report("nobody", "2024-01-01", "2024-01-08")
    assert result == {"error": "Unknown agent: nobody"}


@pytest.mark.asyncio
async def test_audit_log_endpoint():
    result = await audit_log(limit=50)
    assert result == {"entries": [], "limit": 50}
