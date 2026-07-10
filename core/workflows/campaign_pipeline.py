from typing import Any, Dict, Optional

from configs.config_loader import ConfigLoader
from core.agents.outreach.outreach_agent import OutreachAgent
from core.agents.strategy.strategy_agent import StrategyAgent
from utils.logging import get_logger, log_with_context

logger = get_logger(__name__)


class CampaignPipeline:
    def __init__(self):
        self.config = ConfigLoader.load()

        self.strategy_agent = StrategyAgent("strategy_agent", self.config)
        self.outreach_agent = OutreachAgent("outreach_agent", self.config)

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
            # ✅ STEP 1: Strategy
            strategy_result = await self.strategy_agent.run(
                input_data,
                context={},
                trace_id=trace_id,
            )

            strategy_data = strategy_result.get("result", {})

            # ✅ STEP 2: Outreach (uses strategy output)
            outreach_result = await self.outreach_agent.run(
                {"angles": strategy_data.get("angles", [])},
                context=input_data,
                trace_id=trace_id,
            )

            result = {
                "success": True,
                "strategy": strategy_data,
                "outreach": outreach_result.get("result", {}),
            }

            log_with_context(
                logger,
                "info",
                "Campaign pipeline completed",
                extra={"steps": ["strategy", "outreach"]},
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
