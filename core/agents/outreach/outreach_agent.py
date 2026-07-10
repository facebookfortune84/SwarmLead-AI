from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent


class OutreachAgent(BaseAgent):
    """
    Generates outreach messages based on strategy output.
    """

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:

        angles = input_data.get("angles", [])
        audience = context.get("audience", "")
        product = context.get("product", "")

        prompt = f"""
You are an outreach specialist.

Product: {product}
Audience: {audience}

Angles:
{angles}

Create:
1. 3 outreach messages (short, compelling)

Return JSON:
{{
  "messages": [...]
}}
"""

        response = await self.call_llm(prompt, trace_id=trace_id)

        return self._parse_response(response)

    def _parse_response(self, text: str) -> Dict[str, Any]:
        import json

        try:
            parsed = json.loads(text)
            return {
                "messages": parsed.get("messages", []),
            }
        except Exception:
            return {
                "messages": [text.strip()],
            }
