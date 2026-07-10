import json
from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent
from core.analytics.event_tracker import EventTracker
from core.memory import long_term_memory as long_term_memory_module
from core.memory.vector_store import VectorStore
from core.prompts.archetype_selector import ArchetypeSelector
from core.prompts.asset_loader import AssetLoader

LongTermMemory = getattr(long_term_memory_module, "LongTermMemory", None)


class _NullLongTermMemory:
    def find_by_type(self, _type):
        return []


class StrategyAgent(BaseAgent):
    """
    Strategy generation agent.

    Responsibilities:
    - Select archetypes
    - Load archetype assets
    - Retrieve historical memory
    - Generate strategic recommendations
    - Emit telemetry events
    """

    def __init__(
        self,
        name,
        config,
        vector_store=None,
        long_term_memory=None,
        event_tracker=None,
    ):
        super().__init__(name, config)

        self.asset_loader = AssetLoader()
        self.selector = ArchetypeSelector(config)

        self.vector_store = vector_store or VectorStore()

        self.long_term_memory = (
            long_term_memory
            if long_term_memory is not None
            else (LongTermMemory() if callable(LongTermMemory) else _NullLongTermMemory())
        )

        self.event_tracker = event_tracker if event_tracker is not None else EventTracker()

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        product = input_data.get(
            "product",
            "",
        )

        audience = input_data.get(
            "audience",
            "",
        )

        goal = input_data.get(
            "goal",
            "",
        )

        self.event_tracker.track(
            event_type="strategy_started",
            trace_id=trace_id,
            agent="StrategyAgent",
            payload={
                "product": product,
                "audience": audience,
                "goal": goal,
            },
        )

        try:
            # -----------------------------------------------------------
            # Archetype Selection
            # -----------------------------------------------------------

            archetypes = self.selector.select(
                goal,
                "strategy_agent",
            )

            asset_context = self.asset_loader.build_context(archetypes)

            # -----------------------------------------------------------

            # Vector Memory Retrieval
            # -----------------------------------------------------------

            query = f"{product} {audience} {goal}"

            related_memories = self.vector_store.search(
                query,
                top_k=5,
            )

            vector_memory_context = "\n".join(
                str(memory.get("text", "")) for memory in related_memories
            )

            # -------------------------------------------------------------------------------------------------------------------------

            # Long-Term Memory Retrieval
            # -------------------------------------------------------------------------------------------------------------------------

            feedback_memories = []

            try:
                feedback_memories = self.long_term_memory.find_by_type("feedback")
            except Exception:
                feedback_memories = []

            feedback_context = "\n".join(
                memory.get("content", "") for memory in feedback_memories[-3:]
            )

            memory_context = "\n".join(
                [
                    vector_memory_context,
                    feedback_context,
                ]
            ).strip()

            # -------------------------------------------------------------------------------------------------------------------------

            # Prompt Construction
            # -------------------------------------------------------------------------------------------------------------------------

            prompt = f""" You are an elite marketing strategist.  Historical learnings: {memory_context} Proven archetype intelligence: {asset_context} Product: {product} Audience: {audience} Goal: {goal} Generate: 1. 5 marketing angles 2. 5 hooks 3. A summary Return JSON: {{"angles": [...], "hooks": [...], "summary": "..."}}"""

            response = await self.call_llm(
                prompt,
                trace_id=trace_id,
            )

            parsed = self._parse_response(response)

            self.event_tracker.track(
                event_type="strategy_completed",
                trace_id=trace_id,
                agent="StrategyAgent",
                payload={
                    "angles": len(parsed["angles"]),
                    "hooks": len(parsed["hooks"]),
                },
            )

            return parsed

        except Exception as exc:
            self.event_tracker.track_error(
                exc,
                trace_id=trace_id,
                agent="StrategyAgent",
            )

            raise

    def _parse_response(self, text: str) -> Dict[str, Any]:
        try:
            parsed = json.loads(text)
            return {
                "angles": parsed.get("angles", []),
                "hooks": parsed.get("hooks", []),
                "summary": parsed.get("summary", text.strip()),
            }
        except Exception:
            return {
                "angles": [],
                "hooks": [],
                "summary": text.strip(),
            }
