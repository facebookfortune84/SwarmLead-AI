import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.orchestration.voice_orchestrator import VoiceOrchestrator
from core.integrations.elevenlabs.elevenlabs_client import STTResult
from core.orchestration.voice_session_manager import VoiceSessionManager
from core.memory.conversation_memory_adapter import ConversationMemoryAdapter


class AsyncGenMock:
    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        return self._async_gen()

    async def _async_gen(self):
        for item in self.items:
            yield item


@pytest.fixture
def mock_elevenlabs():
    client = MagicMock()
    client.speech_to_text = AsyncMock(return_value=STTResult(
        text="hello", confidence=0.95, language="en", duration_ms=500
    ))
    client.text_to_speech_stream = MagicMock(return_value=AsyncGenMock([b"audio1", b"audio2"]))
    client.cancel_stream = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_memory():
    return MagicMock(spec=ConversationMemoryAdapter)


@pytest.fixture
def mock_session_manager():
    return MagicMock(spec=VoiceSessionManager)


@pytest.fixture
def mock_agent_manager():
    mgr = MagicMock()
    mgr.get_agent = MagicMock(return_value=MagicMock())
    mgr.execute_agent = AsyncMock(return_value={
        "success": True,
        "result": {"response": "I can help with that"}
    })
    return mgr


@pytest.fixture
def orchestrator(mock_elevenlabs, mock_memory, mock_session_manager, mock_agent_manager):
    orch = VoiceOrchestrator(
        agent_manager=mock_agent_manager,
        elevenlabs_client=mock_elevenlabs,
        memory_adapter=mock_memory,
        voice_session_manager=mock_session_manager
    )
    return orch


@pytest.mark.asyncio
async def test_route_voice_task_success(orchestrator, mock_elevenlabs, mock_agent_manager):
    chunks = []
    async for chunk in orchestrator.route_voice_task(
        session_id="session_1",
        intent="qualification",
        audio_data=b"audio_data"
    ):
        chunks.append(chunk)

    assert len(chunks) == 2
    mock_elevenlabs.speech_to_text.assert_awaited_once_with(b"audio_data")
    mock_agent_manager.execute_agent.assert_awaited_once()


@pytest.mark.asyncio
async def test_route_voice_task_uses_intent_for_routing(orchestrator, mock_agent_manager):
    async for _ in orchestrator.route_voice_task(
        session_id="session_1", intent="onboarding", audio_data=b"data"
    ):
        pass

    agent_name = mock_agent_manager.execute_agent.call_args[1]["agent_name"]
    assert agent_name == "onboarding_agent"


@pytest.mark.asyncio
async def test_route_voice_task_fallback_to_voice_agent(orchestrator, mock_agent_manager):
    async for _ in orchestrator.route_voice_task(
        session_id="session_1", intent="unknown_thing", audio_data=b"data"
    ):
        pass

    agent_name = mock_agent_manager.execute_agent.call_args[1]["agent_name"]
    assert agent_name == "voice_agent"


@pytest.mark.asyncio
async def test_route_voice_task_no_agent(orchestrator, mock_agent_manager):
    mock_agent_manager.get_agent.return_value = None

    with pytest.raises(ValueError, match="No agent found"):
        async for _ in orchestrator.route_voice_task(
            session_id="session_1", intent="qualification", audio_data=b"data"
        ):
            pass


@pytest.mark.asyncio
async def test_route_voice_task_failed_execution(orchestrator, mock_agent_manager):
    mock_agent_manager.execute_agent.return_value = {
        "success": False,
        "error": "Agent failed"
    }

    chunks = []
    async for chunk in orchestrator.route_voice_task(
        session_id="session_1", intent="qualification", audio_data=b"data"
    ):
        chunks.append(chunk)

    assert len(chunks) == 0


@pytest.mark.asyncio
async def test_handle_barge_in(orchestrator, mock_elevenlabs):
    mock_elevenlabs.speech_to_text.return_value = STTResult(
        text="wait actually", confidence=0.9, language="en", duration_ms=300
    )

    chunks = []
    async for chunk in orchestrator.handle_barge_in(
        session_id="session_1",
        interruption_audio=b"interrupt_audio"
    ):
        chunks.append(chunk)

    assert len(chunks) == 2
    mock_elevenlabs.cancel_stream.assert_awaited_once_with("session_1")


@pytest.mark.asyncio
async def test_classify_voice_intent_qualification(orchestrator):
    assert orchestrator._classify_voice_intent("I am interested in your service", {}) == "qualification"
    assert orchestrator._classify_voice_intent("Can you qualify these leads", {}) == "qualification"


@pytest.mark.asyncio
async def test_classify_voice_intent_founder_discovery(orchestrator):
    assert orchestrator._classify_voice_intent("I am a founder with a startup idea", {}) == "founder_discovery"


@pytest.mark.asyncio
async def test_classify_voice_intent_business_launch(orchestrator):
    assert orchestrator._classify_voice_intent("I want to incorporate my company", {}) == "business_launch"
    assert orchestrator._classify_voice_intent("Help me register my business", {}) == "business_launch"


@pytest.mark.asyncio
async def test_classify_voice_intent_product_recommendation(orchestrator):
    assert orchestrator._classify_voice_intent("Can you recommend a tool", {}) == "product_recommendation"


@pytest.mark.asyncio
async def test_classify_voice_intent_onboarding(orchestrator):
    assert orchestrator._classify_voice_intent("I want to get started", {}) == "onboarding"


@pytest.mark.asyncio
async def test_classify_voice_intent_default(orchestrator):
    assert orchestrator._classify_voice_intent("something random", {}) == "qualification"


@pytest.mark.asyncio
async def test_route_voice_task_provides_audio_context(orchestrator, mock_elevenlabs):
    mock_elevenlabs.speech_to_text.return_value = STTResult(
        text="test query", confidence=0.88, language="en", duration_ms=400
    )

    async for _ in orchestrator.route_voice_task(
        session_id="session_1", intent="qualification", audio_data=b"data"
    ):
        pass

    call_kwargs = mock_elevenlabs.text_to_speech_stream.call_args
    assert call_kwargs is not None


@pytest.mark.asyncio
async def test_stream_registration(orchestrator):
    q = asyncio.Queue()
    orchestrator.register_stream("stream_1", q)
    assert "stream_1" in orchestrator._active_streams
    assert orchestrator._active_streams["stream_1"] is q

    orchestrator.unregister_stream("stream_1")
    assert "stream_1" not in orchestrator._active_streams


@pytest.mark.asyncio
async def test_cancel_stream(orchestrator):
    q = asyncio.Queue()
    orchestrator.register_stream("stream_1", q)
    result = await orchestrator.cancel_stream("stream_1")
    assert result is True
    assert "stream_1" not in orchestrator._active_streams


@pytest.mark.asyncio
async def test_cancel_stream_nonexistent(orchestrator):
    result = await orchestrator.cancel_stream("nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_route_voice_task_empty_stt(orchestrator, mock_elevenlabs, mock_agent_manager):
    mock_elevenlabs.speech_to_text.return_value = STTResult(
        text="", confidence=0.0, language="en", duration_ms=0
    )

    async for _ in orchestrator.route_voice_task(
        session_id="session_1", intent="qualification", audio_data=b"silence"
    ):
        pass

    mock_agent_manager.execute_agent.assert_awaited_once()


@pytest.mark.asyncio
async def test_classify_voice_intent_case_insensitive(orchestrator):
    assert orchestrator._classify_voice_intent("INTERESTED IN PARTNERSHIP", {}) == "qualification"
    assert orchestrator._classify_voice_intent("INCORPORATE MY COMPANY", {}) == "business_launch"
