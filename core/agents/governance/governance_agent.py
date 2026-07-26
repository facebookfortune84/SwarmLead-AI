"""
Governance Agent -- Constitution Enforcement Engine

Constitutional §3, §4, §5, §12, §13, §14 enforcement.
Pre-execution checks on all agent actions.
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import yaml

from core.auth.agent_identity import AgentIdentity, AgentDomain, AgentIdentityRegistry, DEFAULT_AGENT_CONFIG
from core.monitoring.metrics_collector import record_agent_task


class ComplianceResult:
    """Result of constitutional compliance check."""
    def __init__(self, compliant: bool, violation: str = "", article: str = "", details: Dict = None):
        self.compliant = compliant
        self.violation = violation
        self.article = article
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            "compliant": self.compliant,
            "violation": self.violation,
            "article": self.article,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class ConstitutionEngine:
    """
    Constitution as code -- enforces all constitutional provisions programmatically.
    Reads Constitution YAML, not PDFs.
    """
    
    def __init__(self, constitution_path: str = "docs/governance/constitution.yaml"):
        self.rules = self._load_constitution(constitution_path)
        self.monetary_rules = None  # Injected by GovernanceAgent
    
    def _load_constitution(self, path: str) -> Dict:
        """Load Constitution from YAML."""
        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._default_rules()
    
    def _default_rules(self) -> Dict:
        return {
            "sections": {
                "3": {  # Core Values
                    "legible_authorship": True,
                    "reversibility": True,
                    "escalate_uncertainty": True,
                    "minimum_viable_autonomy": True,
                    "no_self_graded_homework": True,
                    "ip_hygiene": True,
                    "secrets_never_agent_touchable": True,
                    "open_source_core": True,
                },
                "4": {  # Human Oversight
                    "4.1": {"legal_officer_required": True},
                    "4.2": {"informed_consent_required": True},
                    "4.3": {"external_representation_templates_only": True},
                    "4.4": {"friction_model": {"fast": ["routine"], "genuine": ["legal", "financial", "launch"]}},
                    "4.5": {"kyc_at_real_launch": True},
                    "4.6": {"portfolio_isolation": True},
                    "4.7": {"simulation_fallback": True},
                },
                "5": {  # Autonomy by Domain
                    "product_code": "autonomous_reversible",
                    "security_secrets": "human_mediated",
                    "financial": "human_approval",
                    "legal_contracts": "human_approval_kyc",
                    "external_comms": "ai_drafted_human_reviewed",
                    "simulation": "fully_autonomous",
                },
                "12": {  # Monetary Rules
                    "no_standing_spend": True,
                    "human_approval_per_dollar": True,
                    "allowlisted_counterparties_only": True,
                    "dual_rail_model": True,
                    "tamper_evident_logging": True,
                    "reconciliation_escalation": True,
                    "disputes_to_processor": True,
                },
                "13": {  # Agent Identity
                    "unique_nonshared_identity": True,
                    "least_privilege_default": True,
                    "scoped_revocable_credentials": True,
                    "explicit_tool_allowlists": True,
                    "new_roles_require_review": True,
                },
                "14": {  # Vendor Governance
                    "security_liability_review": True,
                    "periodic_reassessment": True,
                    "fail_closed_financial_legal": True,
},
            }
        }
     
    def check_action(self, action: "AgentAction") -> "ComplianceResult":
        """Check if action complies with Constitution."""
        
        # §3: Legible authorship
        if not action.agent_id or not action.trace_id:
            return ComplianceResult(False, "Missing agent_id or trace_id", "§3", {
                "agent_id": action.agent_id,
                "trace_id": action.trace_id
            })
        
        # §4.6: Portfolio isolation
        if action.accesses_data and not action.tenant_scoped:
            return ComplianceResult(False, "Cross-tenant data access without tenant scoping", "§4.6", {
                "accesses_data": action.accesses_data,
                "tenant_scoped": action.tenant_scoped
            })
        
        # §5: Autonomy by domain
        if action.domain:
            allowed = self._check_domain_autonomy(action.agent_id, action.domain)
            if not allowed:
                return ComplianceResult(False, f"Domain {action.domain} not allowed for agent", "§5", {
                    "agent_id": action.agent_id,
                    "domain": action.domain
                })
        
        # §12: Monetary rules
        if action.spend_usd:
            if not self._check_monetary_rules(action):
                return ComplianceResult(False, "Monetary rule violation", "§12", {
                    "spend_usd": action.spend_usd,
                    "counterparty": action.counterparty
                })
        
        # §13: Agent identity
        if not action.agent_identity_valid:
            return ComplianceResult(False, "Invalid or missing agent identity", "§13", {
                "agent_id": action.agent_id
            })
        
        return ComplianceResult(True, "Compliant")
    
    def _check_domain_autonomy(self, agent_id: str, domain: str) -> bool:
        """Check if agent has autonomy in domain per §5."""
        identity = AgentIdentityRegistry.get(agent_id)
        if not identity:
            return False
        
        domain_map = {
            "product_code": AgentDomain.PRODUCT_CODE,
            "security_secrets": AgentDomain.SECURITY_SECRETS,
            "financial": AgentDomain.FINANCIAL,
            "legal_contracts": AgentDomain.LEGAL_CONTRACTS,
            "external_comms": AgentDomain.EXTERNAL_COMMS,
            "simulation": AgentDomain.SIMULATION,
        }
        
        required_domain = domain_map.get(domain)
        if not required_domain:
            return False
        
        return identity.has_domain(required_domain)
    
    def _check_monetary_rules(self, action: "AgentAction") -> bool:
        """Check monetary rules per §12."""
        if not self.monetary_rules:
            return False
        
        return self.monetary_rules.authorize_spend(
            agent_id=action.agent_id,
            amount_usd=action.spend_usd,
            counterparty=action.counterparty,
            rail=action.rail_type
        )


class TemplateRegistry:
    """Pre-approved templates for external representation (§4.3)."""
    
    def __init__(self):
        self.templates: Dict[str, str] = {}
        self._load_defaults()
    
    def _load_defaults(self):
        self.templates = {
            "ndas": "Standard NDA template...",
            "service_agreements": "Service agreement template...",
            "employment_offers": "Employment offer template...",
            "vendor_contracts": "Vendor contract template...",
            "press_releases": "Press release template...",
        }
    
    def get_template(self, name: str) -> Optional[str]:
        return self.templates.get(name)
    
    def validate_action_uses_template(self, action: "AgentAction") -> bool:
        """Check if external action uses pre-approved template."""
        if action.domain == "external_comms" and action.external_content:
            return any(template in action.external_content for template in self.templates.values())
        return True


class FrictionTiers:
    """Approval friction model per §4.4."""
    
    def __init__(self):
        self.tiers = {
            "fast": {
                "domains": ["product_code", "simulation"],
                "actions": ["code_generation", "analysis", "planning", "drafting"],
                "approval": "automatic",
                "human_review": False,
            },
            "genuine": {
                "domains": ["financial", "legal_contracts", "security_secrets"],
                "actions": ["spending", "contracts", "secrets_access", "legal_filings"],
                "approval": "human_required",
                "human_review": True,
            }
        }
    
    def get_tier(self, domain: str, action: str) -> str:
        for tier_name, tier_config in self.tiers.items():
            if domain in tier_config["domains"] or action in tier_config["actions"]:
                return tier_name
        return "genuine"


class TriggerEvaluator:
    """Evaluates mandatory legal/compliance review triggers per §5.1."""
    
    TRIGGERS = {
        "dollar_value": {"threshold_usd": 10000, "cumulative": True},
        "regulated_category": ["healthcare", "finance", "legal", "insurance", "minors", "controlled_substances"],
        "irreversibility": ["entity_registration", "signed_contracts", "published_terms", "first_live_transaction"],
        "public_commitment": ["launch_announcement", "marketing_claims"],
    }
    
    def evaluate(self, action: "AgentAction") -> List[str]:
        triggered = []
        
        if action.spend_usd:
            if action.spend_usd >= self.TRIGGERS["dollar_value"]["threshold_usd"]:
                triggered.append("dollar_value")
            if action.cumulative_spend_usd and action.cumulative_spend_usd >= self.TRIGGERS["dollar_value"]["threshold_usd"]:
                triggered.append("dollar_value_cumulative")
        
        if action.category in self.TRIGGERS["regulated_category"]:
            triggered.append("regulated_category")
        
        if action.action_type in self.TRIGGERS["irreversibility"]:
            triggered.append("irreversibility")
        
        if action.action_type in self.TRIGGERS["public_commitment"]:
            triggered.append("public_commitment")
        
        return triggered


@dataclass
class AgentAction:
    """Represents an agent action to be validated."""
    agent_id: str
    domain: str
    trace_id: str
    action_type: str
    tenant_scoped: bool = True
    accesses_data: bool = False
    spend_usd: Optional[float] = None
    cumulative_spend_usd: Optional[float] = None
    counterparty: Optional[str] = None
    rail_type: Optional[str] = None
    category: Optional[str] = None
    action_type: Optional[str] = None
    external_content: Optional[str] = None
    agent_identity_valid: bool = True
    agent_identity: Optional["AgentIdentity"] = None
    human_review_completed: bool = False
    audit_logged: bool = False


class GovernanceAgent:
    """
    Constitution enforcement agent.
    
    Runs pre-execution checks on all agent actions.
    """
    
    def __init__(self):
        self.constitution = ConstitutionEngine()
        self.templates = TemplateRegistry()
        self.friction = FrictionTiers()
        self.triggers = TriggerEvaluator()
        self.monetary_rules = None  # Set by PaymentService
        
        # Load default identities if registry is empty
        from core.auth.agent_identity import AgentIdentityRegistry, DEFAULT_AGENT_CONFIG
        if not AgentIdentityRegistry._identities:
            AgentIdentityRegistry.load_from_config(DEFAULT_AGENT_CONFIG)
    
    def pre_check(self, action: AgentAction) -> "ComplianceResult":
        """Pre-execution compliance check."""
        
        # Run constitutional compliance check
        result = self.constitution.check_action(action)
        if not result.compliant:
            return result
        
        # Check template compliance for external actions
        if action.domain == "external_comms":
            # Template validation would go here
            pass
        
        # Evaluate triggers
        triggers = self.triggers.evaluate(action)
        if triggers:
            if not action.human_review_completed:
                return ComplianceResult(False, f"Triggers require genuine review: {triggers}", "§5.1", {"triggers": triggers})
        
        # Determine friction tier
        tier = self.friction.get_tier(action.domain, action.action_type)
        if tier == "genuine" and not action.human_review_completed:
            return ComplianceResult(False, "Genuine review required", "§4.4", {"tier": "genuine"})
        
        return ComplianceResult(True, "Pre-check passed")
    
    def post_check(self, action: AgentAction, result: Any) -> "ComplianceResult":
        """Post-execution audit check."""
        if action.spend_usd and not self.monetary_rules.verify_audit_log(action):
            return ComplianceResult(False, "Missing audit log for spend", "§12.5")
        
        if not action.audit_logged:
            return ComplianceResult(False, "Action not audit logged", "§3")
        
        return ComplianceResult(True, "Post-check passed")
    
    def register_monetary_rules(self, rules_engine):
        """Register monetary rules engine."""
        self.monetary_rules = rules_engine
        self.constitution.monetary_rules = rules_engine


governance_agent = GovernanceAgent()