from typing import Dict, Any, Callable, Optional

from utils.logging import get_logger, log_with_context

logger = get_logger(__name__)


class TaskRouter:
    """
    Intelligent routing layer for swarm execution.

    Responsibilities:
    - Route tasks to appropriate agents
    - Enable pipeline chaining
    - Support dynamic decision logic
    """

    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.routes: Dict[str, str] = {}
        self.pipelines: Dict[str, Callable] = {}

    # ------------------------------------------------------------------
    # Route Registration
    # ------------------------------------------------------------------

    def register_route(self, task_name: str, agent_name: str):
        """
        Map a task to an agent.
        """
        self.routes[task_name] = agent_name

        logger.info(f"Route registered: {task_name} -> {agent_name}")

    def register_pipeline(self, name: str, handler: Callable):
        """
        Register a multi-step pipeline.
        """
        self.pipelines[name] = handler

        logger.info(f"Pipeline registered: {name}")

    # ------------------------------------------------------------------
    # Routing Logic
    # ------------------------------------------------------------------

    async def route(
        self,
        task_name: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route execution based on task type.
        """

        log_with_context(
            logger,
            "info",
            f"Routing task: {task_name}",
            extra={"task": task_name},
            trace_id=trace_id,
        )

        # Pipeline takes priority
        if task_name in self.pipelines:
            handler = self.pipelines[task_name]

            result = await handler(input_data, context or {})

            return {
                "type": "pipeline",
                "task": task_name,
                "result": result,
            }

        # Agent route fallback
        if task_name not in self.routes:
            raise ValueError(f"No route defined for task '{task_name}'")

        agent_name = self.routes[task_name]

        result = await self.agent_manager.execute(
            agent_name=agent_name,
            input_data=input_data,
            context=context,
            trace_id=trace_id,
        )

        return {
            "type": "agent",
            "task": task_name,
            "agent": agent_name,
            "result": result,
        }

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_routes(self) -> Dict[str, str]:
        return self.routes

    def list_pipelines(self) -> Dict[str, Callable]:
        return self.pipelines