import asyncio
import time
import uuid
from typing import Dict, Any, Callable, Optional

from utils.logging import get_logger

logger = get_logger(__name__)


class AgentExecutionError(Exception):
    """Custom exception for agent failures."""
    pass


class AgentManager:
    """
    Swarm Control Plane

    Responsibilities:
    - Register agents
    - Route execution
    - Track performance
    - Handle failures
    - Enable observability hooks
    """

    def __init__(self):
        self.agents: Dict[str, Callable] = {}
        self.agent_metadata: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Agent Registration
    # ------------------------------------------------------------------

    def register_agent(
        self,
        name: str,
        handler: Callable,
        description: str = "",
        version: str = "1.0",
        async_supported: bool = True,
    ):
        """
        Register an agent into the swarm.
        """
        if name in self.agents:
            logger.warning(f"Agent '{name}' already registered. Overwriting.")

        self.agents[name] = handler
        self.agent_metadata[name] = {
            "description": description,
            "version": version,
            "async_supported": async_supported,
            "registered_at": time.time(),
        }

        logger.info(f"Registered agent: {name}")

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an agent with full observability.
        """

        if agent_name not in self.agents:
            raise AgentExecutionError(f"Agent '{agent_name}' not found.")

        handler = self.agents[agent_name]
        trace_id = trace_id or str(uuid.uuid4())

        start_time = time.time()

        logger.info(
            f"[TRACE {trace_id}] Starting execution: {agent_name}",
            extra={"input": input_data}
        )

        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(input_data, context or {})
            else:
                result = handler(input_data, context or {})

            latency = time.time() - start_time

            logger.info(
                f"[TRACE {trace_id}] Completed execution: {agent_name} in {latency:.3f}s"
            )

            return {
                "success": True,
                "agent": agent_name,
                "trace_id": trace_id,
                "latency": latency,
                "result": result,
            }

        except Exception as e:
            latency = time.time() - start_time

            logger.error(
                f"[TRACE {trace_id}] Agent failed: {agent_name}",
                exc_info=True
            )

            return {
                "success": False,
                "agent": agent_name,
                "trace_id": trace_id,
                "latency": latency,
                "error": str(e),
            }

    # ------------------------------------------------------------------
    # Batch Execution
    # ------------------------------------------------------------------

    async def execute_batch(
        self,
        tasks: Dict[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute multiple agents concurrently.

        tasks = {
            "agent_name": {input_data}
        }
        """

        results = {}

        async def run(agent_name, input_data):
            results[agent_name] = await self.execute(
                agent_name,
                input_data,
                context=context,
            )

        await asyncio.gather(
            *(run(name, data) for name, data in tasks.items())
        )

        return results

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata of all registered agents.
        """
        return self.agent_metadata

    def get_agent(self, name: str) -> Optional[Callable]:
        """
        Retrieve a registered agent.
        """
        return self.agents.get(name)