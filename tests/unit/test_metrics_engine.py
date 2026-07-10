from core.analytics.metrics_engine import MetricsEngine


def test_perfect_score():
    engine = MetricsEngine()

    score = engine.calculate_score(
        reply_rate=1.0,
        conversion_rate=1.0,
        engagement_score=1.0,
    )

    assert score == 1.0


def test_zero_score():
    engine = MetricsEngine()

    score = engine.calculate_score(
        reply_rate=0.0,
        conversion_rate=0.0,
        engagement_score=0.0,
    )

    assert score == 0.0


def test_weighted_score():
    engine = MetricsEngine()

    score = engine.calculate_score(
        reply_rate=0.5,
        conversion_rate=1.0,
        engagement_score=0.5,
    )

    expected = (0.5 * 0.4) + (1.0 * 0.4) + (0.5 * 0.2)

    assert score == expected


def test_clamps_high_values():
    engine = MetricsEngine()

    score = engine.calculate_score(
        reply_rate=10,
        conversion_rate=10,
        engagement_score=10,
    )

    assert score == 1.0


def test_clamps_low_values():
    engine = MetricsEngine()

    score = engine.calculate_score(
        reply_rate=-5,
        conversion_rate=-5,
        engagement_score=-5,
    )

    assert score == 0.0


def test_score_campaign():
    engine = MetricsEngine()

    score = engine.score_campaign(
        {
            "reply_rate": 0.5,
            "conversion_rate": 0.5,
            "engagement_score": 0.5,
        }
    )

    assert score == 0.5
