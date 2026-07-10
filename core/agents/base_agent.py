from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from core.models.local_llm.ollama_client import OllamaClient
from utils.logging import get_logger, log_with_context

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Base class for all swarm agents.

    Responsibilities:
    - Structured execution
    - Input validation
    - Context handling
    - LLM integration (via OllamaClient)
    - Structured logging
    """

    def __init__(self, name: str, config):
        self.name = name
        self.config = config
        self.llm_client = OllamaClient()  # ✅ CENTRALIZED LLM ACCESS

    # ------------------------------------------------------------------
    # Public Execution Interface
    # ------------------------------------------------------------------

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        context = context if context is not None else {}

        log_with_context(
            logger,
            "info",
            f"Agent started: {self.name}",
            extra={
                "agent": self.name,
                "input": input_data,
                "context_present": bool(context),
            },
            trace_id=trace_id,
        )

        try:
            self.validate(input_data)

            result = await self._execute_internal(input_data, context, trace_id)

            log_with_context(
                logger,
                "info",
                f"Agent completed: {self.name}",
                extra={"agent": self.name},
                trace_id=trace_id,
            )

            return {
                "success": True,
                "agent": self.name,
                "result": result,
            }

        except Exception as e:
            log_with_context(
                logger,
                "error",
                "Agent execution failed",
                extra={
                    "agent": self.name,
                    "error": str(e),
                },
                trace_id=trace_id,
            )

            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
            }

    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        return await self.execute(input_data, context, trace_id)  # pragma: no cover

    # ------------------------------------------------------------------
    # ✅ NEW: LLM HELPER METHOD
    # ------------------------------------------------------------------

    async def call_llm(
        self,
        prompt: str,
        trace_id: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """Centralized LLM call for all agents. Returns response text only."""
        log_with_context(
            logger,
            "info",
            "Agent calling LLM",
            extra={
                "agent": self.name,
                "prompt_preview": prompt[:100],
                "model_override": model,
            },
            trace_id=trace_id,
        )

        try:
            result = await self.llm_client.generate(
                prompt=prompt,
                model=model,
                trace_id=trace_id,
            )

            # normalize dict responses
            if isinstance(result, dict):
                return result.get("response", "")

            return str(result)

        except Exception as e:
            log_with_context(
                logger,
                "error",
                "LLM call failed",
                extra={
                    "agent": self.name,
                    "error": str(e),
                },
                trace_id=trace_id,
            )
            # consistent string fallback
            return ""

    # ------------------------------------------------------------------
    # Validation Hook
    # ------------------------------------------------------------------

    def validate(self, input_data: Dict[str, Any]) -> None:
        if not isinstance(input_data, dict):
            raise ValueError("input_data must be a dictionary")

    # ------------------------------------------------------------------
    # Core Logic (must be implemented)
    # ------------------------------------------------------------------

    @abstractmethod
    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        pass
