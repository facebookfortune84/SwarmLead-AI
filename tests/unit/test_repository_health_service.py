from core.orchestration.repository_health_service import (
    HealthServiceResult,
    RepositoryHealthService,
)


def test_collect_health():

    service = RepositoryHealthService()

    result = service.collect_health(90)

    assert isinstance(
        result,
        HealthServiceResult,
    )


def test_health_marked_healthy():

    service = RepositoryHealthService()

    result = service.collect_health(95)

    assert result.healthy is True


def test_health_marked_unhealthy():

    service = RepositoryHealthService()

    result = service.collect_health(40)

    assert result.healthy is False


def test_latest_health():

    service = RepositoryHealthService()

    service.collect_health(90)

    assert service.latest_health() is not None


def test_average_health():

    service = RepositoryHealthService()

    service.collect_health(80)
    service.collect_health(100)

    assert service.average_health() == 90


def test_history_recorded():

    service = RepositoryHealthService()

    service.collect_health(90)

    assert service.history.count() == 1


def test_events_recorded():

    service = RepositoryHealthService()

    service.collect_health(90)

    assert service.tracker.count() == 1


def test_summary():

    service = RepositoryHealthService()

    service.collect_health(90)

    summary = service.summary()

    assert "monitor" in summary
    assert "history" in summary
    assert "events" in summary


def test_reset():

    service = RepositoryHealthService()

    service.collect_health(90)

    service.reset()

    assert service.history.count() == 0
    assert service.tracker.count() == 0


def test_result_dataclass():

    result = HealthServiceResult(
        score=100,
        healthy=True,
    )

    assert result.score == 100
    assert result.healthy is True


def test_latest_health_none():

    service = RepositoryHealthService()

    assert service.latest_health() is None


def test_average_health_no_report():

    service = RepositoryHealthService()

    assert service.average_health() == 0.0


def test_health_trending_up_no_report():

    service = RepositoryHealthService()

    assert service.health_trending_up() is False


def test_health_trending_down_no_report():

    service = RepositoryHealthService()

    assert service.health_trending_down() is False


def test_summary_without_report():

    service = RepositoryHealthService()

    summary = service.summary()

    assert "monitor" in summary
    assert "history" in summary
    assert "events" in summary


def test_reset_clears_state():

    service = RepositoryHealthService()

    service.collect_health(90)

    service.reset()

    assert service.history.count() == 0
    assert service.tracker.count() == 0


def test_summary_after_reset():

    service = RepositoryHealthService()

    service.collect_health(90)

    service.reset()

    summary = service.summary()

    assert "monitor" in summary
