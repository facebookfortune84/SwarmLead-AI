"""
Nurture Agent - deterministic lead-nurture orchestrator.

Wraps the NurtureEngine in an agent-shaped interface so the Agent Center can
discover it: plan a multi-touch nurture cadence, advance it, and classify
inbound replies into next actions (escalate / suppress / continue).
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class NurtureAgent:
    """Agent wrapper around the deterministic lead-nurture engine."""

    def __init__(self, name: str = "nurture_agent", config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self._engine = None

    def _svc(self):
        if self._engine is None:
            from core.services.nurture_engine import nurture_engine

            self._engine = nurture_engine
        return self._engine

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        try:
            svc = self._svc()
            action = input_data.get("action", "plan")
            if action == "classify":
                result = svc.apply(input_data.get("reply", ""))
            elif action == "advance":
                result = svc.advance(input_data.get("seq", 0))
            else:
                result = svc.plan(input_data.get("email", ""))
            return {"success": True, "agent": self.name, "result": result}
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Nurture agent failed")
            return {"success": False, "agent": self.name, "error": str(exc)}


nurture_agent = NurtureAgent()
__all__ = ["NurtureAgent", "nurture_agent"]