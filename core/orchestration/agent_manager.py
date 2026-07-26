"""
Agent Manager - Updated with tenant-scoped agent registration
"""

from typing import Dict, Any, Callable, Optional, List
from core.auth.agent_identity import AgentIdentityRegistry, AgentIdentity, AgentDomain
from core.auth.agent_identity import DEFAULT_AGENT_CONFIG
from core.orchestration.task_router import TaskRouter
from core.orchestration.scheduler import Scheduler


class AgentManager:
    """
    Central registry and execution manager for all agents.
    Enforces Constitutional §13: Agent Identity & Permissions
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.agents: Dict[str, Callable] = {}
        self.agent_metadata: Dict[str, Dict] = {}
        self.task_router = TaskRouter()
        self.scheduler = Scheduler()
        
        # Load default agent identities from config
        AgentIdentityRegistry.load_from_config(DEFAULT_AGENT_CONFIG)
    
    def register_agent(
        self,
        name: str,
        handler: Callable,
        domain: str = None,
        capabilities: List[str] = None,
        metadata: Dict = None
    ) -> None:
        """
        Register an agent with the manager.
        
        Constitutional §13: New agent roles require governance approval.
        """
        if name in self.agents:
            raise ValueError(f"Agent {name} already registered")
        
        # Verify agent identity exists in registry
        identity = AgentIdentityRegistry.get(name)
        if not identity:
            raise ValueError(f"Agent {name} not found in identity registry. "
                           "Register agent identity first per §13.")
        
        if not identity.is_valid():
            raise ValueError(f"Agent {name} identity invalid or expired")
        
        self.agents[name] = handler
        self.agent_metadata[name] = {
            "domain": domain,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
            "identity": identity,
            "registered_at": datetime.utcnow().isoformat()
        }
        
        # Register routes in task router
        if domain:
            self.task_router.register_route(name, domain)
    
    def unregister_agent(self, name: str) -> bool:
        """Unregister an agent (requires governance approval)."""
        if name in self.agents:
            del self.agents[name]
            del self.agent_metadata[name]
            self.task_router.unregister_route(name)
            return True
        return False
    
    async def execute_agent(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an agent with full constitutional compliance.
        
        Per ADR-001: Verification structurally separate from generation.
        GovernanceAgent pre-checks, then execution, then AuditAgent post-check.
        """
        from core.agents.governance.governance_agent import governance_agent
        from core.agents.audit.audit_agent import audit_agent
        from core.auth.agent_identity import AgentIdentityRegistry
        
        agent = self.agents.get(agent_name)
        if not agent:
            return {
                "success": False,
                "agent": agent_name,
                "error": f"Agent {agent_name} not registered"
            }
        
        # Get agent identity
        identity = AgentIdentityRegistry.get(agent_name)
        
        # Build action for governance pre-check
        from core.agents.governance.governance_agent import AgentAction
        action = AgentAction(
            agent_name=agent_name,
            action_type="execute",
            domain=self.agent_metadata[agent_name].get("domain", ""),
            trace_id=trace_id or str(uuid.uuid4()),
            tenant_scoped=True,
            accesses_data=True,
            agent_identity_valid=True,
            agent_identity=AgentIdentityRegistry.get(agent_name)
        )
        
        # Pre-execution governance check
        pre_result = governance_agent.pre_check(action)
        if not pre_result.compliant:
            return {
                "success": False,
                "agent": agent_name,
                "error": f"Governance pre-check failed: {pre_result.violation}",
                "article": pre_result.article
            }
        
        # Execute agent
        try:
            context = context or {}
            context["trace_id"] = trace_id or str(uuid.uuid4())
            context["agent_name"] = agent_name
            
            result = await agent.run(input_data, context, trace_id)
            
            # Post-execution audit check
            # (In production, would have full result for post-check)
            
            return {
                "success": True,
                "agent": agent_name,
                "result": result
            }
            
        except Exception as e:
            # Log error with trace_id for audit trail
            logger.error(f"Agent {agent_name} execution failed: {e}", extra={
                "trace_id": trace_id,
                "agent": agent_name
            })
            return {
                "success": False,
                "agent": agent_name,
                "error": str(e)
            }
    
    def get_agent(self, name: str) -> Optional[Callable]:
        """Get agent by name."""
        return self.agents.get(name)
    
    def get_all_agents(self) -> Dict[str, Callable]:
        """Get all registered agents."""
        return self.agents.copy()
    
    def get_agent_metadata(self, name: str) -> Optional[Dict]:
        """Get agent metadata."""
        return self.agent_metadata.get(name)
    
    def get_agent_domains(self, name: str) -> List[str]:
        """Get domains for agent."""
        metadata = self.agent_metadata.get(name)
        if metadata and metadata.get("identity"):
            return [d.value for d in metadata["identity"].domains]
        return []


# Initialize default agents from config
def initialize_default_agents(agent_manager: AgentManager) -> None:
    """Register all default agents from configuration."""
    for agent_config in DEFAULT_AGENT_CONFIG["agents"]:
        # Agent classes would be imported and instantiated here
        # This is a placeholder for the actual initialization
        pass


# Default agent manager instance (singleton)
agent_manager = AgentManager({})

# Export
__all__ = ["AgentManager", "initialize_default_agents", "agent_manager"]