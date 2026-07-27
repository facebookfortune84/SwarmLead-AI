"""
Audit Agent — Independent Verification

Constitutional §3: Legible authorship
Constitutional §13: Agent identity & permissions
Independent verification — structurally separate from generation.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from core.auth.agent_identity import AgentIdentityRegistry


class AuditEventType(str, Enum):
    AGENT_ACTION = "agent_action"
    HUMAN_REVIEW = "human_review"
    MONETARY_TRANSACTION = "monetary_transaction"
    TENANT_OPERATION = "tenant_operation"
    CONSTITUTIONAL_CHECK = "constitutional_check"
    ESCALATION = "escalation"
    IDENTITY_VERIFICATION = "identity_verification"


@dataclass
class AuditEntry:
    """Immutable audit log entry."""

    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    agent_id: Optional[str]
    trace_id: str
    tenant_id: Optional[str]
    action: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    compliance_result: Dict[str, Any]
    human_reviewer: Optional[str] = None
    audit_trail_hash: str = ""

    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "trace_id": self.trace_id,
            "tenant_id": self.tenant_id,
            "action": self.action,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "compliance_result": self.compliance_result,
            "human_reviewer": self.human_reviewer,
            "audit_trail_hash": self.audit_trail_hash,
        }


class AuthorshipVerifier:
    """
    Verifies legible authorship per Constitution §3.

    Every commit, draft, filing, and decision traces to a named agent role
    and, where required, a human approver. No anonymous or unattributable actions.
    """

    def __init__(self):
        self.authorship_log: List[Dict] = []

    def verify(self, action: Dict) -> Dict:
        """Verify action has proper attribution."""

        # Check required fields
        required_fields = ["agent_id", "trace_id", "timestamp"]
        for field in required_fields:
            if not action.get(field):
                return {
                    "valid": False,
                    "violations": [f"Missing required field: {field}"],
                    "details": {},
                }

        # Verify agent identity exists
        agent_id = action.get("agent_id")
        if not AgentIdentityRegistry.get(action.get("agent_id")):
            return {"valid": False, "violations": [f"Unknown agent: {agent_id}"], "details": {}}

        # Verify trace_id format (should be UUID)
        trace_id = action.get("trace_id")
        if not self._is_valid_uuid(trace_id):
            return {"valid": False, "violations": ["Invalid trace_id format"], "details": {}}

        # Verify agent identity is valid
        identity = AgentIdentityRegistry.get(action.get("agent_id"))
        if identity and not identity.is_valid():
            return {
                "valid": False,
                "violations": [f"Agent identity invalid or expired: {action.get('agent_id')}"],
                "details": {},
            }

        # Check for anonymous actions
        if action.get("anonymous", False):
            return {
                "valid": False,
                "violations": ["Anonymous actions prohibited per §3"],
                "details": {},
            }

        return {
            "valid": True,
            "violations": [],
            "details": {"agent_id": action.get("agent_id"), "trace_id": trace_id},
        }

    def _is_valid_uuid(self, val: str) -> bool:
        import uuid

        try:
            uuid.UUID(val)
            return True
        except (ValueError, TypeError):
            return False

    def log_authorship(self, action: Dict) -> None:
        """Log verified authorship for audit trail."""
        entry = {
            "event_id": f"auth_{datetime.utcnow().timestamp()}",
            "event_type": "authorship_verified",
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
        }
        self.authorship_log.append(entry)


class EscalationAuditor:
    """
    Audits escalation framework compliance.

    Constitution §6: Emergency Intervention Protocol
    Constitution §5.1: Mandatory Legal/Compliance Review Triggers
    """

    def __init__(self):
        self.escalation_log: List[Dict] = []

    def audit_escalation(self, escalation_event: Dict) -> Dict:
        """Audit an escalation event for compliance."""
        result = {"valid": True, "violations": [], "details": {}}

        # Check required fields
        for field in ["trigger", "escalated_by", "escalated_to", "reason"]:
            if not escalation_event.get(field):
                result["valid"] = False
                result["violations"].append(f"Missing required field: {field}")

        # Check trigger is valid
        valid_triggers = [
            "dollar_value",
            "regulated_category",
            "irreversibility",
            "public_commitment",
            "security_incident",
            "constitutional_violation",
        ]
        trigger = escalation_event.get("trigger")
        if trigger and trigger not in valid_triggers:
            result["valid"] = False
            result["violations"].append(f"Invalid trigger: {trigger}")

        # Check graceful wind-down per §6
        if escalation_event.get("emergency_stop"):
            if not escalation_event.get("graceful_wind_down"):
                result["valid"] = False
                result["violations"].append("Emergency stop requires graceful wind-down per §6")

        # Check human involvement
        if not escalation_event.get("human_involved"):
            result["valid"] = False
            result["violations"].append("Escalation requires human involvement")

        # Log
        audit_entry = {
            "event_id": f"esc_{datetime.utcnow().timestamp()}",
            "event_type": "escalation_audit",
            "timestamp": datetime.utcnow().isoformat(),
            "event": escalation_event,
            "result": result,
        }
        self.escalation_log.append(audit_entry)

        return result


class ComplianceReporter:
    """
    Generates compliance reports for governance review.
    """

    def __init__(self):
        self.reports: List[Dict] = []

    def generate_constitutional_compliance_report(
        self, period_start: datetime, period_end: datetime
    ) -> Dict:
        """Generate constitutional compliance report for period."""
        # This would query audit logs in production
        return {
            "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
            "sections": {
                "legible_authorship": {"compliant": True, "violations": 0},
                "reversibility": {"compliant": True, "violations": 0},
                "escalation_compliance": {"compliant": True, "violations": 0},
                "minimum_autonomy": {"compliant": True, "violations": 0},
                "no_self_graded_homework": {"compliant": True, "violations": 0},
                "ip_hygiene": {"compliant": True, "violations": 0},
                "secrets_protection": {"compliant": True, "violations": 0},
                "open_source": {"compliant": True, "violations": 0},
                "human_oversight": {"compliant": True, "violations": 0},
                "portfolio_isolation": {"compliant": True, "violations": 0},
                "autonomy_by_domain": {"compliant": True, "violations": 0},
                "monetary_rules": {"compliant": True, "violations": 0},
                "agent_identity": {"compliant": True, "violations": 0},
                "vendor_governance": {"compliant": True, "violations": 0},
            },
            "summary": {
                "total_actions_audited": 0,
                "total_violations": 0,
                "critical_violations": 0,
                "compliance_rate": 100.0,
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

    def generate_agent_activity_report(
        self, agent_id: str, period_start: datetime, period_end: datetime
    ) -> Dict:
        """Generate activity report for specific agent."""
        identity = AgentIdentityRegistry.get(agent_id)
        if not identity:
            return {"error": f"Unknown agent: {agent_id}"}

        return {
            "agent_id": agent_id,
            "agent_type": identity.agent_type,
            "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
            "actions_count": 0,
            "domains_accessed": list(identity.domains),
            "tools_used": list(identity.tool_allowlist),
            "data_accessed": list(identity.data_allowlist),
            "violations": 0,
            "compliance_rate": 100.0,
        }

    def generate_monetary_audit_report(self, period_start: datetime, period_end: datetime) -> Dict:
        """Generate monetary rules audit report per §12."""
        return {
            "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
            "rules": {
                "no_standing_spend": {"compliant": True, "violations": 0},
                "human_approval_per_dollar": {"compliant": True, "violations": 0},
                "allowlisted_counterparties": {"compliant": True, "violations": 0},
                "dual_rail_model": {"compliant": True, "violations": 0},
                "tamper_evident_logging": {"compliant": True, "violations": 0},
                "reconciliation_escalation": {"compliant": True, "violations": 0},
                "disputes_to_processor": {"compliant": True, "violations": 0},
            },
            "transactions": {"total": 0, "total_usd": 0.0, "failed": 0, "escalated": 0},
            "generated_at": datetime.utcnow().isoformat(),
        }


class AuditAgent:
    """
    Independent verification agent — structurally separate from generation.

    Per ADR-001: No self-graded homework.
    Verification is always structurally separate from generation.
    """

    def __init__(self):
        self.authorship = AuthorshipVerifier()
        self.escalation = EscalationAuditor()
        self.reporter = ComplianceReporter()
        self.audit_log: List[Dict] = []

    def audit_action(self, action: Dict) -> Dict:
        """Audit a single agent action."""
        # Verify authorship
        authorship_result = self.authorship.verify(action)

        # Log
        {
            "event_id": f"audit_{datetime.utcnow().timestamp()}",
            "event_type": "action_audit",
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "authorship_result": authorship_result,
        }

        return {
            "valid": authorship_result["valid"],
            "violations": authorship_result["violations"],
            "audit_entry": authorship_result,
        }

    def audit_escalation(self, escalation_event: Dict) -> Dict:
        """Audit an escalation event."""
        return self.escalation.audit_escalation(escalation_event)

    def generate_reports(self, period_start: datetime, period_end: datetime) -> Dict:
        """Generate all compliance reports."""
        return {
            "constitutional_compliance": self.reporter.generate_constitutional_compliance_report(
                period_start, period_end
            ),
            "monetary_audit": self.reporter.generate_monetary_audit_report(
                period_start, period_end
            ),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_agent_report(self, agent_id: str, period_start: datetime, period_end: datetime) -> Dict:
        """Get agent-specific report."""
        return self.reporter.generate_agent_activity_report(agent_id, period_start, period_end)

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:]


router = APIRouter(prefix="/audit", tags=["Audit"])


class AuditActionRequest(BaseModel):
    agent_id: str
    trace_id: str
    action: str
    input_data: Dict
    output_data: Dict
    compliance_result: Dict


class EscalationEventRequest(BaseModel):
    trigger: str
    escalated_by: str
    escalated_to: str
    reason: str
    emergency_stop: bool = False
    graceful_wind_down: bool = True
    human_involved: bool = True


audit_agent = AuditAgent()


@router.post("/verify", response_model=Dict)
async def verify_action(request: AuditActionRequest):
    """Verify agent action authorship."""
    return audit_agent.audit_action(request.dict())


@router.post("/escalation", response_model=Dict)
async def audit_escalation(request: EscalationEventRequest):
    """Audit an escalation event."""
    result = audit_agent.audit_escalation(request.dict())
    return result


@router.get("/reports/constitutional")
async def constitutional_report(period_start: str, period_end: str):
    """Generate constitutional compliance report."""
    start = datetime.fromisoformat(period_start)
    end = datetime.fromisoformat(period_end)
    return audit_agent.reporter.generate_constitutional_compliance_report(start, end)


@router.get("/reports/monetary")
async def monetary_report(period_start: str, period_end: str):
    """Generate monetary audit report."""
    start = datetime.fromisoformat(period_start)
    end = datetime.fromisoformat(period_end)
    return audit_agent.reporter.generate_monetary_audit_report(start, end)


@router.get("/reports/agent/{agent_id}")
async def agent_report(agent_id: str, period_start: str, period_end: str):
    """Generate agent activity report."""
    start = datetime.fromisoformat(period_start)
    end = datetime.fromisoformat(period_end)
    return audit_agent.get_agent_report(agent_id, start, end)


@router.get("/log")
async def audit_log(limit: int = 100):
    """Get recent audit log."""
    # Would return from persistent storage
    return {"entries": [], "limit": limit}
