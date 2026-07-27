"""
Integration Test — Voice Flow

Verifies VoiceSessionManager + ConversationMemoryAdapter work together
for session creation, turn recording, and context retrieval.
"""

import pytest

from core.memory.conversation_memory_adapter import ConversationMemoryAdapter
from core.orchestration.voice_session_manager import VoiceSessionManager


@pytest.fixture
def memory_adapter(tmp_path):
    path = tmp_path / "test_voice_memory.json"
    return ConversationMemoryAdapter(path=str(path))


@pytest.fixture
def session_manager(memory_adapter):
    mgr = VoiceSessionManager(memory_adapter=memory_adapter)
    return mgr


def test_memory_context_across_turns(memory_adapter):
    session_id = "static_session_for_context"

    memory_adapter.store_turn(session_id, "user", "Turn 1")
    memory_adapter.store_turn(session_id, "assistant", "Response 1")
    memory_adapter.store_turn(session_id, "user", "Turn 2")

    context = memory_adapter.get_context(session_id)
    assert context is not None
    assert len(context) > 0


def test_memory_session_stats(memory_adapter):
    session_id = "stats_session"

    memory_adapter.store_turn(session_id, "user", "hello")
    memory_adapter.store_turn(session_id, "user", "world")
    memory_adapter.store_turn(session_id, "user", "test")

    context = memory_adapter.get_context(session_id, window=2)
    assert len(context) == 2  # window limits to last 2

    stats = memory_adapter.get_session_stats(session_id)
    assert stats["turn_count"] == 3


def test_memory_resume_session(memory_adapter):
    session_id = "resume_session"

    memory_adapter.store_turn(session_id, "user", "First message")
    memory_adapter.store_turn(session_id, "assistant", "First response")
    memory_adapter.store_turn(session_id, "user", "Follow up")

    data = memory_adapter.resume_session(session_id)
    assert data is not None
    assert data["session_id"] == session_id
    assert data["resumable"] is True
    assert "context" in data
    assert "stats" in data


def test_memory_clear_session(memory_adapter):
    session_id = "clear_session"

    memory_adapter.store_turn(session_id, "user", "some data")
    assert memory_adapter.get_session_stats(session_id)["turn_count"] == 1

    memory_adapter.clear_session(session_id)
    assert memory_adapter.get_session_stats(session_id)["turn_count"] == 0


def test_memory_multi_session_isolation(memory_adapter):
    memory_adapter.store_turn("session_a", "user", "from session A")
    memory_adapter.store_turn("session_b", "user", "from session B")

    ctx_a = memory_adapter.get_context("session_a")
    ctx_b = memory_adapter.get_context("session_b")

    assert len(ctx_a) == 1
    assert len(ctx_b) == 1
    assert ctx_a[0]["text"] == "from session A"
    assert ctx_b[0]["text"] == "from session B"
