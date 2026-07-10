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
