from core.analytics.event_tracker import EventTracker
from core.prompts.adaptive_weights import AdaptiveWeightEngine
from core.workflows.feedback_loop import FeedbackLoop


# Provide a lightweight test stub for LongTermMemory in case the real
# implementation is not available or has a different name.
class LongTermMemory:
    def __init__(self, path=None):
        self._data = []

    def add(self, record):
        self._data.append(record)

    def count(self):
        return len(self._data)

    def all(self):
        return list(self._data)


def test_feedback_loop_updates_weights(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()

    loop = FeedbackLoop(
        memory=memory,
        event_tracker=tracker,
    )

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    result = loop.record_result(
        {"builder": 1.0},
        1.0,
    )

    assert result["updated"] is True
    assert "builder" in result["weights"]


def test_feedback_loop_negative_score(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()

    loop = FeedbackLoop(
        memory=memory,
        event_tracker=tracker,
    )

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    loop.record_result(
        {"builder": 1.0},
        0.0,
    )

    assert loop.get_weights()["builder"] < 0


def test_feedback_loop_get_weights(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()

    loop = FeedbackLoop(
        memory=memory,
        event_tracker=tracker,
    )

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    loop.record_result(
        {"planner": 1.0},
        1.0,
    )

    weights = loop.get_weights()

    assert "planner" in weights


def test_feedback_creates_memory_record(
    tmp_path,
):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()

    loop = FeedbackLoop(
        memory=memory,
        event_tracker=tracker,
    )

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    loop.record_result(
        {"planner": 1.0},
        0.8,
        lesson="ROI messaging outperformed feature messaging",
    )

    assert memory.count() == 1

    record = memory.all()[0]

    assert record["type"] == "feedback"

    assert record["score"] == 0.8


def test_feedback_tracks_event(
    tmp_path,
):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()

    loop = FeedbackLoop(
        memory=memory,
        event_tracker=tracker,
    )

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    loop.record_result(
        {"planner": 1.0},
        1.0,
        trace_id="trace-123",
    )

    events = tracker.filter("feedback_recorded")

    assert len(events) == 1

    assert events[0]["trace_id"] == "trace-123"


def test_get_learnings(
    tmp_path,
):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()

    loop = FeedbackLoop(
        memory=memory,
        event_tracker=tracker,
    )

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    loop.record_result(
        {"architect": 1.0},
        0.9,
        lesson="Executive audiences responded best",
    )

    learnings = loop.get_learnings()

    assert len(learnings) == 1

    assert learnings[0]["content"] == "Executive audiences responded best"


def test_record_result_returns_memory_flag(
    tmp_path,
):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()

    loop = FeedbackLoop(
        memory=memory,
        event_tracker=tracker,
    )

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    result = loop.record_result(
        {"builder": 1.0},
        1.0,
    )

    assert result["memory_recorded"] is True


def test_get_learnings_find_by_type_exception():
    class Memory:
        def find_by_type(self, _):
            raise RuntimeError()

    loop = FeedbackLoop()
    loop.memory = Memory()

    assert loop.get_learnings() == []


def test_get_learnings_legacy_find():
    class Memory:
        def find(self, key, value):
            return [{"type": "feedback", "content": "legacy"}]

    loop = FeedbackLoop()
    loop.memory = Memory()
    learnings = loop.get_learnings()

    assert len(learnings) == 1


def test_get_learnings_find_exception():
    class Memory:
        def find(self, key, value):
            raise RuntimeError()

    loop = FeedbackLoop()
    loop.memory = Memory()

    assert loop.get_learnings() == []


def test_get_learnings_all_fallback():
    class Memory:
        def all(self):
            return [
                {"type": "feedback", "content": "fallback"},
                {"type": "strategy"},
            ]

    loop = FeedbackLoop()
    loop.memory = Memory()
    learnings = loop.get_learnings()

    assert len(learnings) == 1


def test_get_learnings_all_exception():
    class Memory:
        def all(self):
            raise RuntimeError()

    loop = FeedbackLoop()
    loop.memory = Memory()

    assert loop.get_learnings() == []


def test_get_learnings_empty_memory():
    class EmptyMemory:
        pass

    loop = FeedbackLoop()
    loop.memory = EmptyMemory()

    assert loop.get_learnings() == []
