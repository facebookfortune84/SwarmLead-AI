"""
Agent Identity System

Constitutional §13: Every agent must have unique, non-shared identity with
scoped credentials and explicit tool allowlists.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


class AgentDomain(Enum):
    """Constitutional §5: Autonomy by Domain"""

    PRODUCT_CODE = "product_code"
    SECURITY_SECRETS = "security_secrets"
    FINANCIAL = "financial"
    LEGAL_CONTRACTS = "legal_contracts"
    EXTERNAL_COMMS = "external_comms"
    SIMULATION = "simulation"


@dataclass
class AgentIdentity:
    """Unique, non-shared agent identity with scoped credentials."""

    agent_id: str
    agent_type: str
    display_name: str
    domains: Set[AgentDomain] = field(default_factory=set)
    tool_allowlist: Set[str] = field(default_factory=set)
    data_allowlist: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True

    # Constitutional §13: Scoped, revocable credentials
    credentials: Dict[str, str] = field(default_factory=dict)
    last_used: Optional[datetime] = None
    use_count: int = 0

    def is_valid(self) -> bool:
        """Check if identity is valid and not expired."""
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def has_domain(self, domain: AgentDomain) -> bool:
        """Check if agent has autonomy in given domain."""
        return domain in self.domains

    def can_use_tool(self, tool_name: str) -> bool:
        """Check if agent has explicit tool permission."""
        return tool_name in self.tool_allowlist or "*" in self.tool_allowlist

    def can_access_data(self, data_type: str) -> bool:
        """Check if agent has explicit data access permission."""
        return data_type in self.data_allowlist or "*" in self.data_allowlist

    def record_use(self) -> None:
        """Record agent usage for audit trail."""
        self.last_used = datetime.utcnow()
        self.use_count += 1


class AgentIdentityRegistry:
    """Central registry for all agent identities."""

    _identities: Dict[str, AgentIdentity] = {}
    _allowlist_config: Dict[str, Dict] = {}

    @classmethod
    def register(cls, identity: AgentIdentity, agent_id: Optional[str] = None) -> None:
        """Register a new agent identity."""
        agent_id = agent_id or identity.agent_id
        if agent_id in cls._identities:
            raise ValueError(f"Agent {agent_id} already registered")
        cls._identities[agent_id] = identity

    @classmethod
    def get(cls, agent_id: str) -> Optional[AgentIdentity]:
        """Get agent identity by ID."""
        return cls._identities.get(agent_id)

    @classmethod
    def get_all(cls) -> List[AgentIdentity]:
        """Get all registered identities."""
        return list(cls._identities.values())

    @classmethod
    def get_by_domain(cls, domain: AgentDomain) -> List[AgentIdentity]:
        """Get all agents with autonomy in a domain."""
        return [i for i in cls._identities.values() if domain in i.domains]

    @classmethod
    def revoke(cls, agent_id: str) -> bool:
        """Revoke agent identity (Constitutional §13: revocable credentials)."""
        if agent_id in cls._identities:
            cls._identities[agent_id].is_active = False
            return True
        return False

    @classmethod
    def load_from_config(cls, config: Dict) -> None:
        """Load agent identities and allowlists from config."""
        cls._allowlist_config = config
        # Clear existing identities to allow re-registration (useful for tests)
        cls._identities.clear()
        for agent_config in config.get("agents", []):
            domains = agent_config.get("domains", [])

            # Handle "*" wildcard for all domains
            if "*" in domains:
                domains = [d for d in AgentDomain]
            else:
                # Convert string domains to AgentDomain enums
                normalized_domains = []
                for d in domains:
                    if isinstance(d, str):
                        try:
                            normalized_domains.append(AgentDomain(d))
                        except ValueError:
                            # Skip invalid domain strings
                            pass
                    else:
                        normalized_domains.append(d)
                domains = normalized_domains

            identity = AgentIdentity(
                agent_id=agent_config["agent_id"],
                agent_type=agent_config["agent_type"],
                display_name=agent_config["display_name"],
                domains={d for d in domains},
                tool_allowlist=set(agent_config.get("tool_allowlist", [])),
                data_allowlist=set(agent_config.get("data_allowlist", [])),
            )
            cls.register(identity)

    @classmethod
    def validate_tool_access(cls, agent_id: str, tool_name: str) -> bool:
        """Validate agent has explicit permission to use tool."""
        identity = cls.get(agent_id)
        if not identity:
            return False
        return identity.can_use_tool(tool_name)

    @classmethod
    def validate_data_access(cls, agent_id: str, data_type: str) -> bool:
        """Validate agent has explicit permission to access data."""
        identity = cls.get(agent_id)
        if not identity:
            return False
        return identity.can_access_data(data_type)


# Default agent identity configuration (loads from YAML in production)
DEFAULT_AGENT_CONFIG = {
    "agents": [
        {
            "agent_id": "strategy_agent",
            "agent_type": "StrategyAgent",
            "display_name": "Strategy Agent",
            "domains": ["product_code", "simulation"],
            "tool_allowlist": ["call_llm", "read_memory", "write_memory", "search_vector"],
            "data_allowlist": ["strategy", "market_data", "business_model"],
        },
        {
            "agent_id": "outreach_agent",
            "agent_type": "OutreachAgent",
            "display_name": "Outreach Agent",
            "domains": ["external_comms"],
            "tool_allowlist": ["call_llm", "send_email", "read_memory", "write_memory"],
            "data_allowlist": ["leads", "outreach_templates", "campaign_data"],
        },
        {
            "agent_id": "builder_agent",
            "agent_type": "BuilderAgent",
            "display_name": "Builder Agent",
            "domains": ["product_code"],
            "tool_allowlist": [
                "call_llm",
                "write_files",
                "read_files",
                "execute_code",
                "read_memory",
                "write_memory",
            ],
            "data_allowlist": ["code", "specifications", "api_docs"],
        },
        {
            "agent_id": "repair_agent",
            "agent_type": "RepairAgent",
            "display_name": "Repair Agent",
            "domains": ["product_code"],
            "tool_allowlist": [
                "call_llm",
                "write_files",
                "read_files",
                "run_tests",
                "read_memory",
                "write_memory",
            ],
            "data_allowlist": ["code", "test_results", "error_logs"],
        },
        {
            "agent_id": "review_agent",
            "agent_type": "ReviewAgent",
            "display_name": "Review Agent",
            "domains": ["product_code"],
            "tool_allowlist": ["call_llm", "read_files", "read_memory"],
            "data_allowlist": ["code", "pull_requests", "standards"],
        },
        {
            "agent_id": "voice_agent",
            "agent_type": "VoiceAgent",
            "display_name": "Voice Agent",
            "domains": ["external_comms", "simulation"],
            "tool_allowlist": [
                "call_llm",
                "elevenlabs_stt",
                "elevenlabs_tts",
                "read_memory",
                "write_memory",
            ],
            "data_allowlist": ["conversations", "voice_sessions", "customer_data"],
        },
        {
            "agent_id": "governance_agent",
            "agent_type": "GovernanceAgent",
            "display_name": "Governance Agent",
            "domains": ["*"],
            "tool_allowlist": [
                "call_llm",
                "read_all",
                "audit",
                "enforce",
                "read_memory",
                "write_memory",
            ],
            "data_allowlist": ["*"],
        },
        {
            "agent_id": "audit_agent",
            "agent_type": "AuditAgent",
            "display_name": "Audit Agent",
            "domains": ["*"],
            "tool_allowlist": ["call_llm", "read_all", "audit_log", "read_memory"],
            "data_allowlist": ["*"],
        },
        {
            "agent_id": "monitoring_agent",
            "agent_type": "MonitoringAgent",
            "display_name": "Monitoring Agent",
            "domains": ["*"],
            "tool_allowlist": ["call_llm", "read_metrics", "trigger_alert", "read_memory"],
            "data_allowlist": ["metrics", "logs", "health"],
        },
        {
            "agent_id": "payment_agent",
            "agent_type": "PaymentAgent",
            "display_name": "Payment Agent",
            "domains": ["financial"],
            "tool_allowlist": ["call_llm", "stripe_api", "read_memory", "write_memory"],
            "data_allowlist": ["payments", "subscriptions", "billing"],
        },
        {
            "agent_id": "landing_agent",
            "agent_type": "LandingAgent",
            "display_name": "Landing Page Agent",
            "domains": ["external_comms", "simulation"],
            "tool_allowlist": ["call_llm", "elevenlabs_tts", "read_memory", "write_memory"],
            "data_allowlist": ["visitor_data", "landing_flows", "conversions"],
        },
        {
            "agent_id": "onboarding_agent",
            "agent_type": "OnboardingAgent",
            "display_name": "Onboarding Agent",
            "domains": ["simulation", "product_code"],
            "tool_allowlist": [
                "call_llm",
                "elevenlabs_tts",
                "create_tenant",
                "read_memory",
                "write_memory",
            ],
            "data_allowlist": ["onboarding_flows", "business_profiles", "tenant_data"],
        },
        {
            "agent_id": "seo_agent",
            "agent_type": "SEOAgent",
            "display_name": "SEO Agent",
            "domains": ["simulation", "product_code"],
            "tool_allowlist": ["call_llm", "analyze_seo", "read_memory", "write_memory"],
            "data_allowlist": ["keywords", "content", "analytics"],
        },
        {
            "agent_id": "content_agent",
            "agent_type": "ContentAgent",
            "display_name": "Content Agent",
            "domains": ["product_code", "simulation"],
            "tool_allowlist": ["call_llm", "generate_content", "read_memory", "write_memory"],
            "data_allowlist": ["content", "templates", "brand_guidelines"],
        },
        {
            "agent_id": "growth_agent",
            "agent_type": "GrowthAgent",
            "display_name": "Growth Agent",
            "domains": ["simulation", "product_code"],
            "tool_allowlist": [
                "call_llm",
                "analyze_growth",
                "generate_referral",
                "read_memory",
                "write_memory",
            ],
            "data_allowlist": ["growth_metrics", "referrals", "expansion_data"],
        },
        {
            "agent_id": "sdr_agent",
            "agent_type": "SDRAgent",
            "display_name": "SDR Agent",
            "domains": ["external_comms", "simulation"],
            "tool_allowlist": [
                "call_llm",
                "draft_followup",
                "read_memory",
                "write_memory",
            ],
            "data_allowlist": ["leads", "deals", "pipeline", "prospecting_data"],
        },
        {
            "agent_id": "closer_agent",
            "agent_type": "CloserAgent",
            "display_name": "Closer Agent",
            "domains": ["external_comms", "financial"],
            "tool_allowlist": [
                "call_llm",
                "compose_offer",
                "handle_objection",
                "read_memory",
                "write_memory",
            ],
            "data_allowlist": ["deals", "pipeline", "quotes", "pricing"],
        },
    ]
}


def get_agent_identity(agent_id: str) -> Optional[AgentIdentity]:
    """Get agent identity by IDENTITY: Get agent identity from registry."""
    return AgentIdentityRegistry.get(agent_id)


def validate_agent_tool_access(agent_id: str, tool_name: str) -> bool:
    """Validate agent has explicit permission to use tool."""
    return AgentIdentityRegistry.validate_tool_access(agent_id, tool_name)


def validate_agent_data_access(agent_id: str, data_type: str) -> bool:
    """Validate agent has explicit permission to access data."""
    return AgentIdentityRegistry.validate_data_access(agent_id, data_type)
