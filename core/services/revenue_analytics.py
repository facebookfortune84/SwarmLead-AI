"""
Revenue analytics — deterministic, LLM-free revenue reporting.

Aggregates three sources into one dashboard-shaped snapshot:
1. The sales pipeline (closed-won deals, open weighted pipeline)
2. The growth loop's quote/revenue state (approved quotes, projected MRR)
3. Monetization billing configuration (monthly vs annual pricing)

Everything here is read-only math over persisted state, so it can be
rendered by the API and CLI without any model calls or side effects.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from core.services.sales_pipeline import MONTHLY_VALUE, SalesPipeline, sales_pipeline

logger = logging.getLogger("RevenueAnalytics")

GROWTH_STATE_PATH = Path(__file__).resolve().parents[2] / "data" / "growth_state.json"

DEFAULT_CHURN_RATE = 0.03  # 3% monthly, used when no history exists
DEFAULT_MONTHS_HORIZON = 24


class RevenueAnalytics:
    """Read-only revenue reporting over pipeline + quote + billing state."""

    def __init__(
        self,
        pipeline: SalesPipeline | None = None,
        growth_state_path: Path | None = None,
    ) -> None:
        self.pipeline = pipeline if pipeline is not None else sales_pipeline
        self.growth_state_path = growth_state_path or GROWTH_STATE_PATH

    # ---------------------------------------------------------------- source
    def _growth_revenue(self) -> Dict[str, Any]:
        """Read the growth loop's revenue state (quotes approved / MRR)."""
        try:
            with open(self.growth_state_path, encoding="utf-8") as fh:
                state = json.load(fh)
            return state.get("revenue", {}) or {}
        except (OSError, ValueError):
            return {}

    # ---------------------------------------------------------------- summary
    def summary(self) -> Dict[str, Any]:
        """One dashboard-shaped snapshot of all revenue dimensions."""
        forecast = self.pipeline.forecast()
        quotes = self._growth_revenue()
        velocity = self.pipeline.velocity_stats()

        closed = self.pipeline.list_deals(stage="closed_won", limit=10000)
        tier_mix = self.tier_mix(closed)

        mrr_cents = (
            forecast.get("closed_won_mrr_cents", 0)
            + quotes.get("projected_mrr", 0) * 100
        )

        return {
            "mrr_cents": mrr_cents,
            "arr_cents": mrr_cents * 12,
            "annual_contract_cents": forecast.get("annual_contract_cents", 0),
            "open_weighted_annual_cents": forecast.get(
                "open_weighted_annual_cents", 0
            ),
            "closed_won_count": forecast.get("closed_won_count", 0),
            "quotes_approved": quotes.get("quotes_approved", 0),
            "quotes_expected_mrr_cents": quotes.get("projected_mrr", 0) * 100,
            "sales_velocity_days": forecast.get("sales_velocity_days", 0),
            "median_close_days": velocity.get("median_close_days", 0),
            "oldest_open_deal_days": velocity.get("oldest_open_deal_days", 0),
            "tier_mix": tier_mix,
            "as_of": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def tier_mix(closed: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Closed-won deals grouped by the tier their value maps to."""
        mix = {name: {"count": 0, "mrr_cents": 0} for name in MONTHLY_VALUE}
        for deal in closed:
            amount = deal.get("amount_cents") or 0
            tier = min(MONTHLY_VALUE, key=lambda k: abs(MONTHLY_VALUE[k] - amount))
            mix[tier]["count"] += 1
            mix[tier]["mrr_cents"] += amount
        return mix

    # ---------------------------------------------------------------- churn
    def retention_curve(
        self,
        months: int = DEFAULT_MONTHS_HORIZON,
        churn_rate: float | None = None,
    ) -> List[Dict[str, Any]]:
        """Deterministic cohort retention: % of customers left per month."""
        rate = churn_rate if churn_rate is not None else DEFAULT_CHURN_RATE
        retained = 1.0
        curve = []
        for month in range(1, months + 1):
            retained *= 1.0 - rate
            curve.append(
                {
                    "month": month,
                    "retention_rate": round(retained, 4),
                    "churn_rate": rate,
                }
            )
        return curve

    def ltv(
        self,
        mrr_cents: int | None = None,
        churn_rate: float | None = None,
    ) -> Dict[str, Any]:
        """Lifetime value = MRR / monthly churn (geometric lifetime)."""
        rate = churn_rate if churn_rate is not None else DEFAULT_CHURN_RATE
        value_cents = mrr_cents if mrr_cents is not None else self.summary()["mrr_cents"]
        ltv_cents = int(value_cents / max(rate, 0.001)) if rate > 0 else value_cents * 24
        return {
            "ltv_cents": ltv_cents,
            "mrr_cents": value_cents,
            "churn_rate": rate,
            "avg_customer_lifetime_months": round(1.0 / max(rate, 0.001), 1),
        }

    def churn_risk(self, max_days_inactive: int = 60) -> Dict[str, Any]:
        """Flag open deals that have gone quiet as churn risks.

        A deal is 'at risk' when it sits in a non-terminal stage with no
        stage event within the lookback window (silence = disengagement).
        """
        lookback_days = max_days_inactive
        at_risk = []
        safe_ids: List[str] = []
        for deal in self.pipeline.list_deals(limit=10000):
            if not deal.get("active"):
                continue
            history = self.pipeline.deal_history(deal["id"])
            if not history:
                continue
            last = history[-1]["occurred_at"]
            try:
                last_dt = datetime.fromisoformat(last)
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            days_since = (datetime.now(timezone.utc) - last_dt).total_seconds() / 86400
            if days_since > lookback_days:
                at_risk.append(
                    {
                        "deal_id": deal["id"],
                        "email": deal["email"],
                        "stage": deal["stage"],
                        "days_inactive": round(days_since, 1),
                    }
                )
            else:
                safe_ids.append(deal["id"])
        return {
            "at_risk_deals": at_risk,
            "safe_deals": len(safe_ids),
            "lookback_days": lookback_days,
            "risk_rate": round(
                len(at_risk) / max(len(at_risk) + len(safe_ids), 1), 3
            ),
        }


revenue_analytics = RevenueAnalytics()

__all__ = [
    "RevenueAnalytics",
    "revenue_analytics",
    "DEFAULT_CHURN_RATE",
    "DEFAULT_MONTHS_HORIZON",
]
