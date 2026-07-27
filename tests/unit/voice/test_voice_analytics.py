import pytest

from core.agents.voice.voice_analytics import VoiceAnalytics, VoiceSessionMetrics


@pytest.fixture
def analytics():
    return VoiceAnalytics()


def test_start_session(analytics):
    metrics = analytics.start_session(session_id="s1", visitor_id="v1")
    assert isinstance(metrics, VoiceSessionMetrics)
    assert metrics.session_id == "s1"
    assert metrics.visitor_id == "v1"
    assert metrics.started_at is not None


def test_end_session(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    metrics = analytics.end_session(session_id="s1")
    assert metrics is not None
    assert metrics.ended_at is not None


def test_end_session_with_conversion(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    metrics = analytics.end_session(session_id="s1", conversion=True, conversion_value=100.0)
    assert metrics.conversion is True
    assert metrics.conversion_value == 100.0


def test_end_session_nonexistent(analytics):
    metrics = analytics.end_session(session_id="nonexistent")
    assert metrics is None


def test_record_turn(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.record_turn(session_id="s1", latency_ms=150, stt_ms=50, tts_ms=80)
    metrics = analytics.get_session("s1")
    assert metrics.turn_count == 1
    assert metrics.avg_latency_ms == 150


def test_record_turn_multiple(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.record_turn(session_id="s1", latency_ms=100)
    analytics.record_turn(session_id="s1", latency_ms=200)
    metrics = analytics.get_session("s1")
    assert metrics.turn_count == 2
    assert metrics.avg_latency_ms == 150


def test_record_barge_in(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.record_barge_in(session_id="s1", latency_ms=75)
    metrics = analytics.get_session("s1")
    assert metrics.barge_in_count == 1
    assert metrics.interruptions == 1


def test_record_error(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.record_error(session_id="s1", error="STT failed")
    metrics = analytics.get_session("s1")
    assert len(metrics.errors) == 1
    assert metrics.errors[0].endswith("STT failed")


def test_record_stt_latency(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.record_stt_latency(session_id="s1", latency_ms=60)
    metrics = analytics.get_session("s1")
    assert metrics.stt_latency_ms == 60


def test_record_tts_latency(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.record_tts_latency(session_id="s1", latency_ms=120)
    metrics = analytics.get_session("s1")
    assert metrics.tts_latency_ms == 120


def test_record_llm_latency(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.record_llm_latency(session_id="s1", latency_ms=300)
    metrics = analytics.get_session("s1")
    assert metrics.llm_latency_ms == 300


def test_record_conversion(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.record_conversion(session_id="s1", value=250.0)
    metrics = analytics.get_session("s1")
    assert metrics.conversion is True
    assert metrics.conversion_value == 250.0


def test_get_session_nonexistent(analytics):
    metrics = analytics.get_session("nonexistent")
    assert metrics is None


def test_get_visitor_sessions(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.start_session(session_id="s2", visitor_id="v1")
    analytics.start_session(session_id="s3", visitor_id="v2")
    sessions = analytics.get_visitor_sessions("v1")
    assert len(sessions) == 2
    assert "s1" in sessions
    assert "s2" in sessions


def test_get_aggregate_stats(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.start_session(session_id="s2", visitor_id="v2")
    analytics.record_turn("s1")
    analytics.record_turn("s1")
    analytics.record_turn("s2")
    analytics.record_barge_in("s1")

    stats = analytics.get_aggregate_stats()
    assert stats["total_sessions"] == 2
    assert stats["total_barge_ins"] == 1
    assert stats["avg_turns_per_session"] == 1.5


def test_aggregate_stats_empty(analytics):
    stats = analytics.get_aggregate_stats()
    assert stats["total_sessions"] == 0
    assert stats["avg_turns_per_session"] == 0


def test_multiple_errors(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    analytics.record_error("s1", "err1")
    analytics.record_error("s1", "err2")
    metrics = analytics.get_session("s1")
    assert len(metrics.errors) == 2


def test_session_duration(analytics):
    analytics.start_session(session_id="s1", visitor_id="v1")
    metrics_end = analytics.end_session(session_id="s1")
    assert metrics_end.duration_seconds >= 0


def test_global_instance():
    from core.agents.voice.voice_analytics import voice_analytics

    assert isinstance(voice_analytics, VoiceAnalytics)


@pytest.mark.asyncio
async def test_record_turn_nonexistent_session(analytics):
    analytics.record_turn(session_id="nonexistent")
    assert analytics.get_session("nonexistent") is None


@pytest.mark.asyncio
async def test_record_barge_in_nonexistent(analytics):
    analytics.record_barge_in(session_id="nonexistent")
    assert analytics.get_session("nonexistent") is None
