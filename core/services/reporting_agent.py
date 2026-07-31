"""
Reporting agent — daily outreach metric aggregation.

Reads aggregated metrics from the OutreachDailyMetrics table and returns
per-day snapshots in the shape expected by the frontend analytics dashboard:
[{date, sent, delivered, opened, replied}].
"""

from __future__ import annotations

import logging
from datetime import date

from sqlalchemy.orm import Session

from core.models.outreach import OutreachDailyMetrics

logger = logging.getLogger("ReportingAgent")

# metric_name values stored in outreach_daily_metrics
VALID_METRICS = ("sent", "delivered", "opened", "replied")


class ReportingAgent:
    """Aggregate daily outreach metrics from persisted snapshots."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_metrics_range(self, start: date, end: date) -> list[dict]:
        """
        Return a list of per-day metric snapshots for [start, end].

        Days with no data are included with zeroed metrics so the frontend
        chart can render a continuous series.
        """
        rows = (
            self.db.query(OutreachDailyMetrics)
            .filter(
                OutreachDailyMetrics.date >= start,
                OutreachDailyMetrics.date <= end,
                OutreachDailyMetrics.metric_name.in_(VALID_METRICS),
            )
            .all()
        )

        by_day: dict[date, dict[str, float]] = {}
        for row in rows:
            day = row.date
            if day not in by_day:
                by_day[day] = {m: 0.0 for m in VALID_METRICS}
            by_day[day][row.metric_name] = row.metric_value or 0.0

        result: list[dict] = []
        current = start
        while current <= end:
            metrics = by_day.get(current, {m: 0.0 for m in VALID_METRICS})
            result.append(
                {
                    "date": current.isoformat(),
                    "sent": metrics.get("sent", 0.0),
                    "delivered": metrics.get("delivered", 0.0),
                    "opened": metrics.get("opened", 0.0),
                    "replied": metrics.get("replied", 0.0),
                }
            )
            # advance one calendar day
            current = current.fromordinal(current.toordinal() + 1)

        return result
