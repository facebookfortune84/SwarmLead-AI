import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.agents.voice.voice_agent import VoiceAgent
from core.integrations.elevenlabs.elevenlabs_client import STTResult


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
    return client


@pytest.fixture
def mock_memory():
    mem = MagicMock()
    mem.get_context = MagicMock(return_value=[{"role": "user", "text": "hi"}])
    mem.store_turn = AsyncMock(return_value={"turn_id": 1})
    mem.resume_session = MagicMock(return_value={"summary": "test", "turns": []})
    mem.get_session_stats = MagicMock(return_value={"turn_count": 1, "session_id": "s1"})
    mem.clear_session = MagicMock(return_value=True)
    return mem


@pytest.fixture
def mock_config():
    return MagicMock()


@pytest.fixture
def voice_agent(mock_elevenlabs, mock_memory, mock_config):
    with patch("core.agents.base_agent.OllamaClient") as mock_ollama:
        mock_ollama.return_value.generate = AsyncMock(return_value="test response")
        agent = VoiceAgent(
            name="test_voice_agent",
            config=mock_config,
            elevenlabs_client=mock_elevenlabs,
            memory_adapter=mock_memory
        )
        agent.execute = AsyncMock(return_value={
            "success": True,
            "result": {"response": "I can help with that"}
        })
        return agent


@pytest.mark.asyncio
async def test_process_voice_input_returns_audio(voice_agent, mock_elevenlabs, mock_memory):
    chunks = []
    async for chunk in voice_agent.process_voice_input(
        audio_stream=b"audio_input",
        session_id="session_1"
    ):
        chunks.append(chunk)

    assert len(chunks) == 2
    mock_elevenlabs.speech_to_text.assert_awaited_once_with(b"audio_input")
    assert mock_memory.store_turn.call_count == 2


@pytest.mark.asyncio
async def test_process_voice_input_stores_turns(voice_agent, mock_memory):
    async for _ in voice_agent.process_voice_input(
        audio_stream=b"audio", session_id="s1"
    ):
        pass

    calls = mock_memory.store_turn.call_args_list
    assert len(calls) == 2
    assert calls[0][1]["role"] == "user"
    assert calls[1][1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_process_voice_input_empty_audio(voice_agent, mock_elevenlabs):
    mock_elevenlabs.speech_to_text.return_value = STTResult(
        text="", confidence=0.0, language="en", duration_ms=0
    )

    async for _ in voice_agent.process_voice_input(
        audio_stream=b"", session_id="s1"
    ):
        pass

    voice_agent.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_interruption(voice_agent, mock_elevenlabs):
    mock_elevenlabs.speech_to_text.return_value = STTResult(
        text="stop, I have a question", confidence=0.9, language="en", duration_ms=300
    )

    chunks = []
    async for chunk in voice_agent.handle_interruption(
        session_id="s1",
        interruption_audio=b"interrupt"
    ):
        chunks.append(chunk)

    assert len(chunks) == 2
    voice_agent.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_interruption_empty_audio(voice_agent, mock_elevenlabs):
    mock_elevenlabs.speech_to_text.return_value = STTResult(
        text="", confidence=0.0, language="en", duration_ms=0
    )

    async for _ in voice_agent.handle_interruption(
        session_id="s1",
        interruption_audio=b""
    ):
        pass

    voice_agent.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_maintain_session_context(voice_agent, mock_memory):
    result = await voice_agent.maintain_session_context("s1")
    mock_memory.resume_session.assert_called_once_with("s1")
    assert "summary" in result


@pytest.mark.asyncio
async def test_handle_session_resume(voice_agent, mock_elevenlabs):
    chunks = []
    async for chunk in voice_agent.handle_session_resume("s1"):
        chunks.append(chunk)

    assert len(chunks) == 2


@pytest.mark.asyncio
async def test_get_session_stats(voice_agent, mock_memory):
    stats = voice_agent.get_session_stats("s1")
    mock_memory.get_session_stats.assert_called_once_with("s1")
    assert stats["turn_count"] == 1


@pytest.mark.asyncio
async def test_clear_session(voice_agent, mock_memory):
    result = voice_agent.clear_session("s1")
    assert result is True
    mock_memory.clear_session.assert_called_once_with("s1")


@pytest.mark.asyncio
async def test_process_voice_input_with_context(voice_agent, mock_elevenlabs, mock_memory):
    async for _ in voice_agent.process_voice_input(
        audio_stream=b"audio",
        session_id="s1",
        context={"custom_field": "value"}
    ):
        pass

    mock_elevenlabs.speech_to_text.assert_awaited_once_with(b"audio")


@pytest.mark.asyncio
async def test_process_voice_input_failed_execution(voice_agent):
    voice_agent.execute = AsyncMock(return_value={
        "success": False,
        "error": "LLM error"
    })

    async for _ in voice_agent.process_voice_input(
        audio_stream=b"audio", session_id="s1"
    ):
        pass

    voice_agent.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_interruption_failed_stt_degradation(voice_agent, mock_elevenlabs):
    mock_elevenlabs.speech_to_text.side_effect = RuntimeError("STT failed")

    chunks = []
    async for chunk in voice_agent.handle_interruption(
        session_id="s1",
        interruption_audio=b"data"
    ):
        chunks.append(chunk)

    assert len(chunks) == 2
    voice_agent.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_text_to_speech_success(voice_agent, mock_elevenlabs):
    mock_elevenlabs.text_to_speech_bytes = AsyncMock(return_value=b"audio_data")

    result = await voice_agent.text_to_speech("Hello, world!")
    assert result == b"audio_data"
    mock_elevenlabs.text_to_speech_bytes.assert_awaited_once_with("Hello, world!")


@pytest.mark.asyncio
async def test_text_to_speech_failure_degradation(voice_agent, mock_elevenlabs):
    mock_elevenlabs.text_to_speech_bytes = AsyncMock(side_effect=RuntimeError("TTS failed"))

    result = await voice_agent.text_to_speech("Hello, world!")
    assert result is None


@pytest.mark.asyncio
async def test_process_voice_input_stt_failure_degradation(voice_agent, mock_elevenlabs, mock_memory):
    mock_elevenlabs.speech_to_text.side_effect = RuntimeError("STT failed")

    chunks = []
    async for chunk in voice_agent.process_voice_input(
        audio_stream=b"audio_input",
        session_id="session_1"
    ):
        chunks.append(chunk)

    assert len(chunks) == 2
    mock_memory.store_turn.assert_called()
    # First turn should have empty text (degradation)
    user_turn = mock_memory.store_turn.call_args_list[0]
    assert user_turn[1]["text"] == ""


@pytest.mark.asyncio
async def test_process_voice_input_tts_failure_degradation(voice_agent, mock_elevenlabs):
    mock_elevenlabs.text_to_speech_stream.side_effect = RuntimeError("TTS streaming failed")

    chunks = []
    async for chunk in voice_agent.process_voice_input(
        audio_stream=b"audio",
        session_id="s1"
    ):
        chunks.append(chunk)

    assert len(chunks) == 1
    assert isinstance(chunks[0], bytes)


@pytest.mark.asyncio
async def test_no_memory_adapter_creates_default(mock_elevenlabs, mock_config):
    with patch("core.agents.base_agent.OllamaClient"), \
         patch("core.agents.voice.voice_agent.ConversationMemoryAdapter") as mock_adapter_cls:
        mock_adapter_cls.return_value = MagicMock()
        agent = VoiceAgent(
            name="test",
            config=mock_config,
            elevenlabs_client=mock_elevenlabs
        )
        mock_adapter_cls.assert_called_once()
        assert agent.memory_adapter is not None
