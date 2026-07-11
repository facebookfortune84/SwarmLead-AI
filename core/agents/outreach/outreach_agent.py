import json
from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent
from core.analytics.event_tracker import EventTracker
from core.memory.long_term_memory.long_term_memory import LongTermMemory
from core.memory.vector_store import VectorStore


class OutreachAgent(BaseAgent):
    """
    Generates outreach messages using:
    - strategy angles
    - historical vector memories
    - learned campaign feedback
    - based on strategy output
    - and historical outreach learnings.
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

        self.vector_store = vector_store or VectorStore()

        self.long_term_memory = (
            long_term_memory if long_term_memory is not None else LongTermMemory()
        )

        self.event_tracker = event_tracker if event_tracker is not None else EventTracker()

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:

        angles = input_data.get("angles", [])

        audience = context.get(
            "audience",
            "",
        )

        product = context.get(
            "product",
            "",
        )

        self.event_tracker.track(
            event_type="outreach_started",
            trace_id=trace_id,
            agent="OutreachAgent",
        )

        try:
            # -------------------------------------------------------

            # Vector Memory Retrieval
            # -------------------------------------------------------

            query = f"{product} {audience} {' '.join(str(a) for a in angles)}"

            related_memories = self.vector_store.search(
                query,
                top_k=3,
            )

            vector_context = "\n".join(memory.get("text", "") for memory in related_memories)

            # -------------------------------------------------------------------------
            # Long-Term Learnings
            # -------------------------------------------------------------------------

            feedback_context = ""

            try:
                feedback_memories = self.long_term_memory.find_by_type("feedback")
                feedback_context = "\n".join(memory.get("text", "") for memory in feedback_memories)

            except Exception:
                feedback_context = ""

            # -------------------------------------------------------------------------
            # Prompt Construction
            # -------------------------------------------------------------------------

            prompt = f"""
You are an outreach specialist.
            
Historical outreach learnings:
{vector_context}

Campaign learnings:
{feedback_context}

Product:
{product}

Audience:
{audience}

Angles:
{angles}

Create:

1. Three outreach messages
2. Short
3. Personalized
4. High response rate

Return JSON:

{{
    "messages": [...]
}}
"""

            response = await self.call_llm(
                prompt,
                trace_id=trace_id,
            )

            parsed = self._parse_response(response)

            self.event_tracker.track(
                event_type="outreach_completed",
                trace_id=trace_id,
                agent="OutreachAgent",
                payload={
                    "message_count": len(
                        parsed.get(
                            "messages",
                            [],
                        )
                    )
                },
            )

            return parsed

        except Exception as exc:
            self.event_tracker.track_error(
                exc,
                trace_id=trace_id,
                agent="outreachAgent",
            )

            raise

    def _parse_response(
        self,
        text: str,
    ) -> Dict[str, Any]:

        try:
            parsed = json.loads(text)

            return {
                "messages": parsed.get(
                    "messages",
                    [],
                ),
            }

        except Exception:
            return {
                "messages": [text.strip()],
            }
