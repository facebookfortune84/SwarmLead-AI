import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from core.orchestration.voice_session_manager import VoiceSessionManager, VoiceSession, VoiceSessionStatus
from core.memory.conversation_memory_adapter import ConversationMemoryAdapter


@pytest.fixture
def memory_adapter():
    adapter = MagicMock(spec=ConversationMemoryAdapter)
    adapter.store_turn = AsyncMock(return_value={"status": "stored"})
    return adapter


@pytest.fixture
def manager(memory_adapter):
    return VoiceSessionManager(memory_adapter=memory_adapter, default_timeout_minutes=30)


@pytest.mark.asyncio
async def test_create_session_returns_session(manager, memory_adapter):
    session = await manager.create_session(visitor_id="visitor_1")
    assert isinstance(session, VoiceSession)
    assert session.visitor_id == "visitor_1"
    assert session.status == VoiceSessionStatus.CREATED
    assert session.session_id.startswith("voice_")
    memory_adapter.store_turn.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_session_with_tenant(manager):
    session = await manager.create_session(
        visitor_id="visitor_1",
        tenant_id="tenant_abc",
        greeting_type="welcome"
    )
    assert session.tenant_id == "tenant_abc"
    assert session.greeting_type == "welcome"
    assert session.context["greeting_type"] == "welcome"


@pytest.mark.asyncio
async def test_create_session_sets_expiry(manager):
    session = await manager.create_session(visitor_id="visitor_1", timeout_minutes=10)
    assert session.expires_at is not None
    diff = session.expires_at - datetime.utcnow()
    assert 590 <= diff.total_seconds() <= 610


@pytest.mark.asyncio
async def test_get_session_returns_session(manager):
    created = await manager.create_session(visitor_id="visitor_1")
    retrieved = await manager.get_session(created.session_id)
    assert retrieved is not None
    assert retrieved.session_id == created.session_id


@pytest.mark.asyncio
async def test_get_session_nonexistent(manager):
    retrieved = await manager.get_session("nonexistent")
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_session_expired_ends(manager):
    created = await manager.create_session(visitor_id="visitor_1", timeout_minutes=-1)
    retrieved = await manager.get_session(created.session_id)
    assert retrieved is None
    assert created.status == VoiceSessionStatus.ENDED


@pytest.mark.asyncio
async def test_get_sessions_by_visitor(manager):
    await manager.create_session(visitor_id="v1")
    await manager.create_session(visitor_id="v1")
    sessions = await manager.get_sessions_by_visitor("v1")
    assert len(sessions) == 2


@pytest.mark.asyncio
async def test_get_session_by_visitor_active(manager):
    await manager.create_session(visitor_id="v1")
    s2 = await manager.create_session(visitor_id="v1")
    s2.status = VoiceSessionStatus.ACTIVE
    active = await manager.get_session_by_visitor("v1")
    assert active is not None
    assert active.session_id == s2.session_id


@pytest.mark.asyncio
async def test_update_session(manager):
    created = await manager.create_session(visitor_id="v1")
    result = await manager.update_session(created.session_id, status=VoiceSessionStatus.ACTIVE, turn_count=5)
    assert result is True
    updated = await manager.get_session(created.session_id)
    assert updated.status == VoiceSessionStatus.ACTIVE
    assert updated.turn_count == 5


@pytest.mark.asyncio
async def test_update_session_nonexistent(manager):
    result = await manager.update_session("nonexistent", status=VoiceSessionStatus.ACTIVE)
    assert result is False


@pytest.mark.asyncio
async def test_add_turn(manager, memory_adapter):
    created = await manager.create_session(visitor_id="v1")
    result = await manager.add_turn(created.session_id, role="user", text="hello")
    assert result is True
    session = await manager.get_session(created.session_id)
    assert session.turn_count == 1
    memory_adapter.store_turn.assert_called()


@pytest.mark.asyncio
async def test_add_turn_nonexistent(manager):
    result = await manager.add_turn("nonexistent", role="user", text="hello")
    assert result is False


@pytest.mark.asyncio
async def test_record_barge_in(manager):
    created = await manager.create_session(visitor_id="v1")
    result = await manager.record_barge_in(created.session_id)
    assert result is True
    session = await manager.get_session(created.session_id)
    assert session.barge_in_count == 1


@pytest.mark.asyncio
async def test_record_barge_in_nonexistent(manager):
    result = await manager.record_barge_in("nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_end_session(manager, memory_adapter):
    created = await manager.create_session(visitor_id="v1")
    result = await manager.end_session(created.session_id, reason="completed")
    assert result is True
    assert created.status == VoiceSessionStatus.ENDED
    assert created.context["end_reason"] == "completed"


@pytest.mark.asyncio
async def test_end_session_nonexistent(manager):
    result = await manager.end_session("nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_start_stop(manager):
    await manager.start(interval_seconds=10)
    assert manager._running is True
    assert manager._cleanup_task is not None
    await manager.stop()
    assert manager._running is False


@pytest.mark.asyncio
async def test_cleanup_expired(manager):
    created = await manager.create_session(visitor_id="v1", timeout_minutes=-1)
    assert created.status == VoiceSessionStatus.CREATED

    count = await manager._cleanup_expired()
    assert count >= 1
    assert created.status == VoiceSessionStatus.EXPIRED


@pytest.mark.asyncio
async def test_visitor_session_indexing(manager):
    await manager.create_session(visitor_id="v1")
    await manager.create_session(visitor_id="v2")
    await manager.create_session(visitor_id="v1")
    assert len(manager._visitor_sessions["v1"]) == 2
    assert len(manager._visitor_sessions["v2"]) == 1
