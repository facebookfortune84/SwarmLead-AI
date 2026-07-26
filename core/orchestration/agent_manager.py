"""
Agent Manager - Central registry and execution manager for all agents.
Constitutional §13: Agent Identity & Permissions enforcement.
"""

import asyncio
import uuid
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime

from core.auth.agent_identity import AgentIdentityRegistry, AgentIdentity, AgentDomain
from core.auth.agent_identity import DEFAULT_AGENT_CONFIG
from core.orchestration.task_router import TaskRouter
from core.orchestration.scheduler import Scheduler


class AgentManager:
    """
    Central registry and execution manager for all agents.
    Enforces Constitutional §13: Agent Identity & Permissions.
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.agents: Dict[str, Callable] = {}
        self.agent_metadata: Dict[str, Dict] = {}
        self.task_router = TaskRouter()
        self.task_router.set_agent_manager(self)
        self.scheduler = Scheduler()

        AgentIdentityRegistry.load_from_config(DEFAULT_AGENT_CONFIG)

    def register_agent(
        self,
        name: str,
        handler: Callable,
        domain: str = None,
        capabilities: List[str] = None,
        metadata: Dict = None
    ) -> None:
        if name in self.agents:
            raise ValueError(f"Agent {name} already registered")

        identity = AgentIdentityRegistry.get(name)
        if not identity:
            raise ValueError(
                f"Agent {name} not found in identity registry. "
                "Register agent identity first per §13."
            )
        if not identity.is_valid():
            raise ValueError(f"Agent {name} identity invalid or expired")

        self.agents[name] = handler
        resolved_domain = domain or (list(identity.domains)[0].value if identity.domains else "simulation")
        self.agent_metadata[name] = {
            "domain": resolved_domain,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
            "identity": identity,
            "registered_at": datetime.utcnow().isoformat()
        }
        self.task_router.register_route(name, name)

    def unregister_agent(self, name: str) -> bool:
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
        from core.agents.governance.governance_agent import governance_agent
        from core.agents.governance.governance_agent import AgentAction

        agent = self.agents.get(agent_name)
        if not agent:
            return {
                "success": False,
                "agent": agent_name,
                "error": f"Agent {agent_name} not registered"
            }

        identity = AgentIdentityRegistry.get(agent_name)
        action = AgentAction(
            agent_id=agent_name,
            action_type="execute",
            domain=self.agent_metadata[agent_name].get("domain", ""),
            trace_id=trace_id or str(uuid.uuid4()),
            tenant_scoped=True,
            accesses_data=True,
            agent_identity_valid=True,
            agent_identity=identity,
        )

        pre_result = governance_agent.pre_check(action)
        if not pre_result.compliant:
            return {
                "success": False,
                "agent": agent_name,
                "error": f"Governance pre-check failed: {pre_result.violation}",
                "article": pre_result.article,
            }

        context = context or {}
        context["trace_id"] = trace_id or str(uuid.uuid4())
        context["agent_name"] = agent_name

        try:
            if hasattr(agent, "run"):
                result = await agent.run(input_data, context, trace_id)
            elif asyncio.iscoroutinefunction(agent):
                result = await agent(input_data, context)
            else:
                result = agent(input_data, context)

            return {"success": True, "agent": agent_name, "result": result}
        except Exception as e:
            return {"success": False, "agent": agent_name, "error": str(e)}

    def get_agent(self, name: str) -> Optional[Callable]:
        return self.agents.get(name)

    def get_all_agents(self) -> Dict[str, Callable]:
        return self.agents.copy()

    def get_agent_metadata(self, name: str) -> Optional[Dict]:
        return self.agent_metadata.get(name)

    def get_agent_domains(self, name: str) -> List[str]:
        metadata = self.agent_metadata.get(name)
        if metadata and metadata.get("identity"):
            return [d.value for d in metadata["identity"].domains]
        return []


agent_manager = AgentManager({})

__all__ = ["AgentManager", "agent_manager"]