from typing import Any, Dict, Optional

from configs.config_loader import ConfigLoader
from core.agents.outreach.outreach_agent import OutreachAgent
from core.agents.strategy.strategy_agent import StrategyAgent
from core.prompts.archetype_selector import ArchetypeSelector
from core.workflows.feedback_loop import FeedbackLoop
from utils.logging import get_logger, log_with_context

logger = get_logger(__name__)


class CampaignPipeline:
    def __init__(self):
        self.config = ConfigLoader.load()

        self.strategy_agent = StrategyAgent("strategy_agent", self.config)
        self.outreach_agent = OutreachAgent("outreach_agent", self.config)

        self.selector = ArchetypeSelector(self.config)
        self.feedback = FeedbackLoop()

    async def run(
        self,
        input_data: Dict[str, Any],
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        log_with_context(
            logger,
            "info",
            "Campaign pipeline started",
            extra={"input": input_data},
            trace_id=trace_id,
        )

        try:
            # --------------------------------------------------
            # Select archetypes for strategy phase
            # --------------------------------------------------

            selected_archetypes = self.selector.select(
                goal=input_data.get("goal", ""),
                agent="strategy_agent",
            )

            # --------------------------------------------------
            # Strategy
            # --------------------------------------------------

            strategy_result = await self.strategy_agent.run(
                input_data,
                context={},
                trace_id=trace_id,
            )

            strategy_data = strategy_result.get("result", {})

            # --------------------------------------------------
            # Outreach
            # --------------------------------------------------

            outreach_result = await self.outreach_agent.run(
                {"angles": strategy_data.get("angles", [])},
                context=input_data,
                trace_id=trace_id,
            )

            outreach_data = outreach_result.get("result", {})

            # --------------------------------------------------
            # Learning
            # --------------------------------------------------

            feedback_result = self.feedback.record_result(
                archetypes=selected_archetypes,
                score=0.8,  # placeholder metric
            )

            result = {
                "success": True,
                "strategy": strategy_data,
                "outreach": outreach_data,
                "learning": feedback_result,
            }

            log_with_context(
                logger,
                "info",
                "Campaign pipeline completed",
                extra={
                    "steps": [
                        "strategy",
                        "outreach",
                        "feedback",
                    ]
                },
                trace_id=trace_id,
            )

            return result

        except Exception as e:
            log_with_context(
                logger,
                "error",
                "Campaign pipeline failed",
                extra={"error": str(e)},
                trace_id=trace_id,
            )

            return {
                "success": False,
                "error": str(e),
            }
