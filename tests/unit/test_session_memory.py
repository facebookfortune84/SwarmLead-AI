from core.memory.session_memory.session_memory import SessionMemory


def test_set_and_get():
    memory = SessionMemory()

    memory.set("user", "alice")

    assert memory.get("user") == "alice"


def test_default_value():
    memory = SessionMemory()

    assert memory.get("missing", "default") == "default"


def test_append():
    memory = SessionMemory()

    memory.append("messages", "hello")
    memory.append("messages", "world")

    assert memory.get("messages") == [
        "hello",
        "world",
    ]


def test_delete():
    memory = SessionMemory()

    memory.set("x", 1)

    memory.delete("x")

    assert memory.get("x") is None


def test_clear():
    memory = SessionMemory()

    memory.set("a", 1)
    memory.set("b", 2)

    memory.clear()

    assert memory.all() == {}


def test_all_returns_copy():
    memory = SessionMemory()

    memory.set("key", "value")

    snapshot = memory.all()

    snapshot["key"] = "changed"

    assert memory.get("key") == "value"
