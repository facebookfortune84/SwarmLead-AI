from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent
from core.memory.vector_store import VectorStore
from core.prompts.archetype_selector import ArchetypeSelector
from core.prompts.asset_loader import AssetLoader


class StrategyAgent(BaseAgent):
    def __init__(self, name, config):
        super().__init__(name, config)

        self.asset_loader = AssetLoader()
        self.selector = ArchetypeSelector(config)

        # memory retrieval
        self.vector_store = VectorStore()

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:

        product = input_data.get("product", "")
        audience = input_data.get("audience", "")
        goal = input_data.get("goal", "")

        # --------------------------------------------------
        # Archetype Selection
        # --------------------------------------------------

        archetypes = self.selector.select(
            goal,
            "strategy_agent",
        )

        asset_context = self.asset_loader.build_context(archetypes)

        # --------------------------------------------------
        # Memory Retrieval
        # --------------------------------------------------

        related_memories = self.vector_store.search(
            f"{product} {audience} {goal}",
            top_k=3,
        )

        memory_context = "\n".join(memory["text"] for memory in related_memories)

        # --------------------------------------------------
        # Prompt
        # --------------------------------------------------

        prompt = f"""
You are an elite marketing strategist.

Historical learnings:
{memory_context}

Proven archetype intelligence:
{asset_context}

Product:
{product}

Audience:
{audience}

Goal:
{goal}

Generate:

1. 5 marketing angles
2. 5 hooks
3. A summary

Return JSON:

{{
  "angles": [...],
  "hooks": [...],
  "summary": "..."
}}
"""

        response = await self.call_llm(
            prompt,
            trace_id=trace_id,
        )

        return self._parse_response(response)

    def _parse_response(self, text: str):
        import json

        try:
            parsed = json.loads(text)

            return {
                "angles": parsed.get("angles", []),
                "hooks": parsed.get("hooks", []),
                "summary": parsed.get("summary", ""),
            }

        except Exception:
            return {
                "angles": [],
                "hooks": [],
                "summary": text.strip(),
            }
