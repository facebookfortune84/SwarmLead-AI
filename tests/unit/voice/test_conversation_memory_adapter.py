from unittest.mock import MagicMock

import pytest

from core.memory.conversation_memory_adapter import ConversationMemoryAdapter
from core.memory.long_term_memory import LongTermMemory


@pytest.fixture
def mock_ltm():
    ltm = MagicMock(spec=LongTermMemory)
    ltm.add.side_effect = lambda record: dict(record)
    ltm.query.return_value = []
    return ltm


@pytest.fixture
def adapter(mock_ltm):
    return ConversationMemoryAdapter(ltm=mock_ltm)


@pytest.fixture
def file_adapter(tmp_path):
    path = tmp_path / "test_memory.json"
    return ConversationMemoryAdapter(path=str(path))


def test_store_turn_returns_dict(adapter):
    result = adapter.store_turn(
        session_id="session_1",
        role="user",
        text="hello",
    )
    assert isinstance(result, dict)
    assert result["session_id"] == "session_1"
    import json

    content = json.loads(result["content"])
    assert content["role"] == "user"
    assert content["text"] == "hello"


def test_store_turn_with_audio_meta(adapter):
    result = adapter.store_turn(
        session_id="session_1",
        role="assistant",
        text="hi there",
        audio_meta={"duration": 1.5, "format": "mp3"},
    )
    import json

    content = json.loads(result["content"])
    assert content["audio_meta"] == {"duration": 1.5, "format": "mp3"}


def test_store_turn_calls_ltm_add(adapter, mock_ltm):
    adapter.store_turn(session_id="session_1", role="user", text="hello")
    mock_ltm.add.assert_called_once()


def test_get_context_returns_list(adapter):
    adapter.store_turn(session_id="session_1", role="user", text="turn1")
    adapter.store_turn(session_id="session_1", role="assistant", text="response1")
    context = adapter.get_context(session_id="session_1")
    assert isinstance(context, list)
    assert len(context) == 2


def test_get_context_with_window(adapter):
    for i in range(5):
        adapter.store_turn(session_id="session_1", role="user", text=f"turn{i}")
    context = adapter.get_context(session_id="session_1", window=2)
    assert len(context) == 2
    assert context[-1]["text"] == "turn4"


def test_get_context_empty_session(adapter):
    context = adapter.get_context(session_id="nonexistent")
    assert context == []


def test_get_session_stats(adapter):
    adapter.store_turn(session_id="session_1", role="user", text="hello")
    adapter.store_turn(session_id="session_1", role="assistant", text="world")
    stats = adapter.get_session_stats(session_id="session_1")
    assert stats["turn_count"] == 2
    assert stats["session_id"] == "session_1"


def test_get_session_stats_empty(adapter):
    stats = adapter.get_session_stats(session_id="nonexistent")
    assert stats["session_id"] == "nonexistent"
    assert stats["turn_count"] == 0


def test_resume_session_returns_context(adapter):
    adapter.store_turn(session_id="session_1", role="user", text="hello")
    result = adapter.resume_session(session_id="session_1")
    assert "context" in result
    assert "stats" in result


def test_clear_session(adapter):
    adapter.store_turn(session_id="session_1", role="user", text="hello")
    result = adapter.clear_session(session_id="session_1")
    assert result is True
    context = adapter.get_context(session_id="session_1")
    assert context == []


def test_clear_session_empty(adapter):
    result = adapter.clear_session(session_id="nonexistent")
    assert result is True


def test_file_based_storage(file_adapter):
    file_adapter.store_turn(session_id="s1", role="user", text="hello")
    context = file_adapter.get_context(session_id="s1")
    assert len(context) == 1
    assert context[0]["text"] == "hello"
    assert context[0]["role"] == "user"


def test_file_persists_to_disk(tmp_path):
    path = tmp_path / "test_memory.json"
    a1 = ConversationMemoryAdapter(path=str(path))
    a1.store_turn(session_id="s1", role="user", text="persist me")
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "persist me" in content


def test_file_based_stats(file_adapter):
    file_adapter.store_turn(session_id="s1", role="user", text="a")
    file_adapter.store_turn(session_id="s1", role="assistant", text="b")
    stats = file_adapter.get_session_stats(session_id="s1")
    assert stats["turn_count"] == 2


def test_resume_session_with_file(file_adapter):
    file_adapter.store_turn(session_id="s1", role="user", text="hello")
    result = file_adapter.resume_session(session_id="s1")
    assert len(result["context"]) == 1
    assert result["stats"]["turn_count"] == 1


def test_multiple_sessions(adapter):
    adapter.store_turn(session_id="s1", role="user", text="session1 turn")
    adapter.store_turn(session_id="s2", role="user", text="session2 turn")
    assert len(adapter.get_context(session_id="s1")) == 1
    assert len(adapter.get_context(session_id="s2")) == 1


def test_store_turn_increments_cache(adapter):
    adapter.store_turn(session_id="s1", role="user", text="t1")
    adapter.store_turn(session_id="s1", role="assistant", text="t2")
    context = adapter.get_context(session_id="s1")
    assert len(context) == 2


def test_get_context_orders_by_insertion(adapter):
    adapter.store_turn(session_id="s1", role="assistant", text="second")
    adapter.store_turn(session_id="s1", role="user", text="first")
    context = adapter.get_context(session_id="s1")
    texts = [t["text"] for t in context]
    assert texts == ["second", "first"]
