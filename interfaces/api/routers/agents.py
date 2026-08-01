"""
Agent Center API.

Exposes the production agent registry:
- GET  /api/agents               -> list all agents with identity + runtime info
- POST /api/agents/{id}/test     -> run a sample task through the agent (verifiable proof)
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.auth.agent_identity import AgentIdentityRegistry
from core.orchestration.agent_manager import agent_manager
from core.orchestration.register_default_agents import register_default_agents

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["Agents"])


class AgentTestRequest(BaseModel):
    prompt: Optional[str] = None


def _agent_summary(agent_id: str) -> dict:
    identity = AgentIdentityRegistry.get(agent_id)
    meta = agent_manager.agent_metadata.get(agent_id)

    return {
        "id": agent_id,
        "type": identity.agent_type if identity else None,
        "name": identity.display_name if identity else agent_id,
        "registered": agent_id in agent_manager.agents,
        "implemented": bool(meta and meta.get("metadata", {}).get("implemented")),
        "capabilities": (meta or {}).get("capabilities", []),
        "domains": sorted(d.value for d in identity.domains) if identity else [],
        "tools": sorted(identity.tool_allowlist) if identity else [],
        "data_access": sorted(identity.data_allowlist) if identity else [],
        "active": identity.is_active if identity else False,
        "status": "active" if (identity and identity.is_active and agent_id in agent_manager.agents) else "inactive",
    }


@router.get("")
async def list_agents():
    """List all agents in the registry with identity and runtime status."""
    register_default_agents()
    identities = AgentIdentityRegistry.get_all()
    return {"agents": [_agent_summary(i.agent_id) for i in identities]}


@router.post("/{agent_id}/test")
async def test_agent(agent_id: str, payload: AgentTestRequest):
    """Run a sample task through the agent and return its output."""
    register_default_agents()
    if agent_id not in agent_manager.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not registered")

    prompt = payload.prompt or "Give a brief one-sentence introduction of what you do."

    input_data = {
        "text": prompt,
        "audience": "small business founders",
        "product": "Genesis autonomous business launch platform",
        "goal": "Generate a concise response",
    }

    try:
        result = await agent_manager.execute_agent(agent_id, input_data, context={"domain": "simulation"})
        identity = AgentIdentityRegistry.get(agent_id)
        if identity:
            identity.record_use()
        return {"agent_id": agent_id, "success": bool(result.get("success")), "result": result}
    except Exception as exc:
        logger.warning("Agent %s test failed: %s", agent_id, exc)
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}")
