"""
Integration Test

Verify the ReportingAgent aggregates daily outreach metrics correctly
and that the reporting router no longer depends on a missing module.
"""

from datetime import date

from core.persistence.session import SessionLocal, init_db
from core.services.reporting_agent import ReportingAgent
from core.models.outreach import OutreachDailyMetrics


def test_metrics_range_returns_continuous_series():
    init_db()
    db = SessionLocal()
    try:
        agent = ReportingAgent(db_session=db)
        start = date(2026, 1, 1)
        end = date(2026, 1, 5)
        result = agent.get_metrics_range(start, end)
        assert len(result) == 5
        assert result[0]["date"] == "2026-01-01"
        assert result[-1]["date"] == "2026-01-05"
        for day in result:
            assert set(day.keys()) == {"date", "sent", "delivered", "opened", "replied"}
            assert day["sent"] == 0.0
    finally:
        db.close()


def test_metrics_range_reflects_persisted_rows():
    init_db()
    db = SessionLocal()
    try:
        # Clean any existing rows for this date to avoid interference
        db.query(OutreachDailyMetrics).filter(OutreachDailyMetrics.date == date(2026, 2, 10)).delete()
        db.commit()

        db.add_all(
            [
                OutreachDailyMetrics(date=date(2026, 2, 10), metric_name="sent", metric_value=10),
                OutreachDailyMetrics(date=date(2026, 2, 10), metric_name="opened", metric_value=6),
                OutreachDailyMetrics(date=date(2026, 2, 10), metric_name="replied", metric_value=2),
            ]
        )
        db.commit()

        agent = ReportingAgent(db_session=db)
        result = agent.get_metrics_range(date(2026, 2, 10), date(2026, 2, 10))
        assert len(result) == 1
        day = result[0]
        assert day["sent"] == 10
        assert day["opened"] == 6
        assert day["replied"] == 2
        assert day["delivered"] == 0.0
    finally:
        db.rollback()
        db.close()


def test_reporting_router_imports_service():
    """The router must import from core.services, not the missing agents package."""
    from interfaces.api.routers.reporting import get_daily_reports

    assert callable(get_daily_reports)
