from core.memory.long_term_memory.long_term_memory import LongTermMemory


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


def test_missing_file(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "missing.json"))

    assert memory.count() == 0


def test_invalid_json(tmp_path):
    path = tmp_path / "bad.json"

    path.write_text("invalid json")

    memory = LongTermMemory(path=str(path))

    assert memory.count() == 0
