"""
Task Router - Routes tasks to registered agents with domain autonomy gating.
Constitutional §5: Autonomy by Domain enforcement.
"""

from typing import Dict, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum

from core.auth.agent_identity import AgentIdentityRegistry, AgentDomain
from core.auth.agent_identity import AgentIdentityRegistry


class DomainViolationError(Exception):
    """Raised when agent attempts action outside authorized domain."""
    pass


class TaskRouter:
    """
    Routes tasks to appropriate agents with domain autonomy gating.
    
    Constitutional §5: Autonomy by Domain enforcement.
    Agents can only operate within their authorized domains.
    """
    
    def __init__(self):
        self.routes: Dict[str, str] = {}  # task_name -> agent_name
        self.domain_config: Dict[str, Dict] = {}  # agent_name -> {domains: []}
        self.agent_manager = None  # Set by AgentManager
    
    def register_route(self, task_name: str, agent_name: str) -> None:
        """Register a task route to an agent."""
        if task_name in self.routes:
            raise ValueError(f"Route {task_name} already registered to {self.routes[task_name]}")
        self.routes[task_name] = agent_name
    
    def unregister_route(self, task_name: str) -> bool:
        """Unregister a task route."""
        if task_name in self.routes:
            del self.routes[task_name]
            return True
        return False
    
    def register_agent_domains(self, agent_name: str, domains: List[str]) -> None:
        """Register agent's authorized domains."""
        self.domain_config[agent_name] = {
            "domains": domains,
            "default": domains[0] if domains else None
        }
    
    def set_agent_manager(self, agent_manager):
        """Set reference to agent manager for agent lookup."""
        self.agent_manager = agent_manager
    
    def _classify_domain(self, task_name: str, input_data: Dict) -> str:
        """Classify task into constitutional domain."""
        # Domain classification logic
        domain_keywords = {
            "product_code": ["code", "build", "generate", "implement", "refactor", "api", "service"],
            "security_secrets": ["secret", "credential", "key", "token", "password", "encrypt"],
            "financial": ["payment", "billing", "subscription", "charge", "invoice", "stripe"],
            "legal_contracts": ["contract", "agreement", "legal", "nda", "terms", "compliance"],
            "external_comms": ["email", "outreach", "notification", "message", "send", "campaign"],
            "simulation": ["plan", "strategy", "analyze", "research", "simulate", "draft"],
        }
        
        task_lower = task_name.lower()
        input_str = str(input_data).lower()
        combined = f"{task_lower} {input_str}"
        
        for domain, keywords in domain_keywords.items():
            if any(kw in combined for kw in keywords):
                return domain
        
        return "simulation"  # Default to most permissive
    
    def _domain_allowed(self, agent_name: str, domain: str) -> bool:
        """Check if agent is authorized for domain per §5."""
        identity = AgentIdentityRegistry.get(agent_name)
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
        required = domain_map.get(domain)
        if not required:
            return False
        return identity.has_domain(required)
    
    async def route(
        self,
        task_name: str,
        input_data: Dict,
        context: Optional[Dict] = None,
        trace_id: Optional[str] = None
    ) -> Dict:
        """
        Route task to appropriate agent with domain autonomy check.
        
        Constitutional §5: Autonomy by Domain
        - Product/code build: Agent-autonomous within reversible boundaries
        - Security & secrets: Human-mediated, always
        - Financial: Human approval required
        - Legal/contracts: Human approval + KYC
        - External comms: AI-drafted, human-reviewed
        - Simulation: Fully autonomous
        """
        # Classify domain
        domain = self._classify_domain(task_name, input_data)
        
        # Find agent for task
        agent_name = self.routes.get(task_name)
        if not agent_name:
            # Fallback: find by domain
            for agent, config in self.domain_config.items():
                if domain in config.get("domains", []):
                    agent_name = config.get("default")
                    break
        
        if not agent_name:
            raise ValueError(f"No agent registered for task: {task_name}")
        
        # Domain autonomy check per §5
        if not self._domain_allowed(agent_name, domain):
            raise DomainViolationError(
                f"Agent {agent_name} not authorized for domain {domain}. "
                f"Allowed: {self.domain_config.get(agent_name, {}).get('domains', [])}"
            )
        
        # Route to agent via AgentManager
        if not hasattr(self, 'agent_manager') or not self.agent_manager:
            raise RuntimeError("AgentManager not set on TaskRouter")
        
        return await self.agent_manager.execute_agent(
            agent_name=agent_name,
            input_data=input_data,
            context=context,
            trace_id=trace_id
        )
    
    def get_agent_for_domain(self, domain: str) -> Optional[str]:
        """Get default agent for domain."""
        for agent, config in self.domain_config.items():
            if domain in config.get("domains", []):
                return agent
        return None
    
    def get_agent_domains(self, agent_name: str) -> List[str]:
        """Get domains authorized for agent."""
        return self.domain_config.get(agent_name, {}).get("domains", [])


# Default domain configuration per Constitution §5
DEFAULT_DOMAIN_CONFIG = {
    "strategy_agent": {"domains": ["simulation", "product_code"], "default": "strategy_agent"},
    "outreach_agent": {"domains": ["external_comms"], "default": "outreach_agent"},
    "builder_agent": {"domains": ["product_code"], "default": "builder_agent"},
    "repair_agent": {"domains": ["product_code"], "default": "repair_agent"},
    "review_agent": {"domains": ["product_code"], "default": "review_agent"},
    "governance_agent": {"domains": ["*"], "default": "governance_agent"},
    "audit_agent": {"domains": ["*"], "default": "audit_agent"},
    "monitoring_agent": {"domains": ["*"], "default": "monitoring_agent"},
    "voice_agent": {"domains": ["external_comms", "simulation"], "default": "voice_agent"},
    "landing_agent": {"domains": ["external_comms", "simulation"], "default": "landing_agent"},
    "onboarding_agent": {"domains": ["simulation", "product_code"], "default": "onboarding_agent"},
    "seo_agent": {"domains": ["simulation", "product_code"], "default": "seo_agent"},
    "content_agent": {"domains": ["product_code", "simulation"], "default": "content_agent"},
    "growth_agent": {"domains": ["simulation", "product_code"], "default": "growth_agent"},
    "payment_agent": {"domains": ["financial"], "default": "payment_agent"},
}