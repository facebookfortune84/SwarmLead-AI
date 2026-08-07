"""
Launch Concierge Agent - orchestrates voice-driven company creation.

Runs the CompanyConcierge in an agent-shaped wrapper so the Agent Center can
discover it and drive the full launch flow. Deterministic: the concierge it
wraps never depends on the LLM to advance a step, so this agent is always
responsive and testable without a model.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConciergeAgent:
    """Agent wrapper around the deterministic company-creation concierge."""

    def __init__(self, name: str = "concierge_agent", config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self._concierge = None

    def _svc(self):
        if self._concierge is None:
            from core.services.company_concierge import company_concierge

            self._concierge = company_concierge
        return self._concierge

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run one turn: start or advance a company-creation conversation."""
        context = context or {}
        try:
            svc = self._svc()
            action = input_data.get("action", "start")
            if action == "start":
                result = svc.start(
                    founder_name=input_data.get("founder_name", ""),
                    opening_line=input_data.get("opening_line", ""),
                )
            else:
                session_id = input_data.get("session_id")
                if not session_id:
                    return {"success": False, "agent": self.name, "error": "session_id required"}
                result = svc.advance(session_id, input_data.get("text", ""))
            return {"success": True, "agent": self.name, "result": result}
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Concierge agent failed")
            return {"success": False, "agent": self.name, "error": str(exc)}


concierge_agent = ConciergeAgent()
__all__ = ["ConciergeAgent", "concierge_agent"]