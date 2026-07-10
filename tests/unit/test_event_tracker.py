from core.analytics.event_tracker import EventTracker


def test_track_event():
    tracker = EventTracker()

    tracker.track(
        "strategy_completed",
        {"campaign": "A"},
    )

    events = tracker.all()

    assert len(events) == 1
    assert events[0]["event_type"] == "strategy_completed"


def test_count():
    tracker = EventTracker()

    tracker.track("a")
    tracker.track("b")

    assert tracker.count() == 2


def test_clear():
    tracker = EventTracker()

    tracker.track("a")

    tracker.clear()

    assert tracker.count() == 0


def test_filter():
    tracker = EventTracker()

    tracker.track("strategy")
    tracker.track("outreach")
    tracker.track("strategy")

    results = tracker.filter("strategy")

    assert len(results) == 2


def test_payload_defaults_to_empty_dict():
    tracker = EventTracker()

    tracker.track("event")

    event = tracker.all()[0]

    assert event["payload"] == {}


def test_all_returns_events():
    tracker = EventTracker()

    tracker.track("one")
    tracker.track("two")

    events = tracker.all()

    assert len(events) == 2


def test_track_trace_id():
    tracker = EventTracker()

    tracker.track(
        "strategy_started",
        trace_id="trace-123",
    )

    event = tracker.all()[0]

    assert event["trace_id"] == "trace-123"


def test_track_agent():
    tracker = EventTracker()

    tracker.track(
        "completed",
        agent="StrategyAgent",
    )

    event = tracker.all()[0]

    assert event["agent"] == "StrategyAgent"


def test_filter_by_agent():
    tracker = EventTracker()

    tracker.track(
        "event1",
        agent="A",
    )

    tracker.track(
        "event2",
        agent="B",
    )

    tracker.track(
        "event3",
        agent="A",
    )

    results = tracker.filter_by_agent("A")

    assert len(results) == 2


def test_filter_by_trace():
    tracker = EventTracker()

    tracker.track(
        "event1",
        trace_id="trace-a",
    )

    tracker.track(
        "event2",
        trace_id="trace-b",
    )

    tracker.track(
        "event3",
        trace_id="trace-a",
    )

    results = tracker.filter_by_trace("trace-a")

    assert len(results) == 2


def test_latest():
    tracker = EventTracker()

    tracker.track("1")
    tracker.track("2")
    tracker.track("3")

    latest = tracker.latest(2)

    assert len(latest) == 2
    assert latest[0]["event_type"] == "2"
    assert latest[1]["event_type"] == "3"


def test_track_error():
    tracker = EventTracker()

    try:
        raise ValueError("test failure")
    except ValueError as exc:
        tracker.track_error(exc)

    event = tracker.all()[0]

    assert event["event_type"] == "error"

    assert event["payload"]["error_type"] == "ValueError"


def test_summary():
    tracker = EventTracker()

    tracker.track("strategy")
    tracker.track("strategy")
    tracker.track("outreach")

    summary = tracker.summary()

    assert summary["total_events"] == 3

    assert summary["event_types"]["strategy"] == 2

    assert summary["event_types"]["outreach"] == 1
