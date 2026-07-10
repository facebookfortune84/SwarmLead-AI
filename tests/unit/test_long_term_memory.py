import pytest

try:
    from core.memory import LongTermMemory
except (ImportError, AttributeError) as e:
    pytest.skip(f"core.memory.LongTermMemory is not available: {e}", allow_module_level=True)


def test_add_record(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    memory.add({"campaign": "Launch A"})

    assert memory.count() == 1


def test_persistence(tmp_path):
    path = tmp_path / "memory.json"

    memory = LongTermMemory(path=str(path))

    memory.add({"campaign": "Persisted Campaign"})

    reloaded = LongTermMemory(path=str(path))

    assert reloaded.count() == 1

    assert reloaded.all()[0]["campaign"] == "Persisted Campaign"


def test_clear(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    memory.add({"x": 1})

    memory.clear()

    assert memory.count() == 0


def test_find(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    memory.add({"type": "strategy"})
    memory.add({"type": "outreach"})
    memory.add({"type": "strategy"})

    results = memory.find(
        "type",
        "strategy",
    )

    assert len(results) == 2


def test_find_by_type(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    memory.add({"type": "feedback", "content": "A"})

    memory.add({"type": "strategy", "content": "B"})

    results = memory.find_by_type("feedback")

    assert len(results) == 1
    assert results[0]["content"] == "A"


def test_latest(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    for i in range(5):
        memory.add({"content": f"item-{i}"})

    latest = memory.latest(2)

    assert len(latest) == 2
    assert latest[0]["content"] == "item-3"
    assert latest[1]["content"] == "item-4"


def test_search_text(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    memory.add({"content": "High converting SaaS strategy"})

    memory.add({"content": "Cold outreach sequence"})

    results = memory.search_text("saas")

    assert len(results) == 1


def test_add_learning(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    record = memory.add_learning(
        content="Founder audiences respond best to ROI messaging",
        memory_type="feedback",
        score=0.92,
        metadata={"campaign": "Q1 Launch"},
    )

    assert memory.count() == 1

    assert record["type"] == "feedback"
    assert record["score"] == 0.92

    assert record["metadata"]["campaign"] == "Q1 Launch"


def test_missing_file(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "missing.json"))

    assert memory.count() == 0


def test_invalid_json(tmp_path):
    path = tmp_path / "bad.json"

    path.write_text("invalid json")

    memory = LongTermMemory(path=str(path))

    assert memory.count() == 0


def test_add_enriches_metadata(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    record = memory.add({"content": "test"})

    assert "created_at" in record
    assert record["type"] == "general"
