from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.integrations.elevenlabs.elevenlabs_client import ElevenLabsClient, STTResult


def _make_cm(response):
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=response)
    cm.__aexit__ = AsyncMock(return_value=None)
    return cm


@pytest.fixture
def client():
    c = ElevenLabsClient(api_key="test_key")
    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.post = MagicMock()
    mock_session.get = MagicMock()
    mock_session.delete = MagicMock()
    mock_session.close = AsyncMock()
    c._session = mock_session
    return c


class AsyncIterableMock:
    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        for item in self.items:
            yield item


@pytest.fixture
def mock_response():
    resp = AsyncMock()
    resp.status = 200
    resp.text = AsyncMock(return_value="ok")
    resp.json = AsyncMock(return_value={})
    resp.content = MagicMock()
    resp.content.iter_chunked.return_value = AsyncIterableMock([b"chunk1", b"chunk2"])
    return resp


@pytest.mark.asyncio
async def test_init_without_api_key_warns(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    with patch("core.integrations.elevenlabs.elevenlabs_client.logger") as mock_logger:
        ElevenLabsClient(api_key=None)
        mock_logger.warning.assert_called_once()


@pytest.mark.asyncio
async def test_tts_stream_no_api_key(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    c = ElevenLabsClient(api_key=None)
    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY not configured"):
        async for _ in c.text_to_speech_stream("hello"):
            pass


@pytest.mark.asyncio
async def test_tts_bytes_no_api_key(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    c = ElevenLabsClient(api_key=None)
    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY not configured"):
        await c.text_to_speech_bytes("hello")


@pytest.mark.asyncio
async def test_stt_no_api_key(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    c = ElevenLabsClient(api_key=None)
    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY not configured"):
        await c.speech_to_text(b"audio_data")


@pytest.mark.asyncio
async def test_tts_stream_success(client, mock_response):
    client._session.post.return_value = _make_cm(mock_response)

    results = []
    async for chunk in client.text_to_speech_stream("hello"):
        results.append(chunk)
    assert results == [b"chunk1", b"chunk2"]
    client._session.post.assert_called_once()


@pytest.mark.asyncio
async def test_tts_stream_http_error(client, mock_response):
    mock_response.status = 400
    mock_response.text = AsyncMock(return_value="bad request")
    client._session.post.return_value = _make_cm(mock_response)

    with pytest.raises(RuntimeError, match="ElevenLabs TTS error"):
        async for _ in client.text_to_speech_stream("hello"):
            pass


@pytest.mark.asyncio
async def test_tts_bytes_collects_chunks(client, mock_response):
    client._session.post.return_value = _make_cm(mock_response)

    result = await client.text_to_speech_bytes("hello")
    assert result == b"chunk1chunk2"


@pytest.mark.asyncio
async def test_speech_to_text_success(client, mock_response):
    mock_response.json = AsyncMock(
        return_value={
            "text": "hello world",
            "confidence": 0.95,
            "language": "en",
            "duration_ms": 1500,
        }
    )
    client._session.post.return_value = _make_cm(mock_response)

    result = await client.speech_to_text(b"audio_data")
    assert isinstance(result, STTResult)
    assert result.text == "hello world"
    assert result.confidence == 0.95
    assert result.language == "en"
    assert result.duration_ms == 1500


@pytest.mark.asyncio
async def test_speech_to_text_http_error(client, mock_response):
    mock_response.status = 500
    mock_response.text = AsyncMock(return_value="server error")
    client._session.post.return_value = _make_cm(mock_response)

    with pytest.raises(RuntimeError, match="ElevenLabs STT error"):
        await client.speech_to_text(b"audio_data")


@pytest.mark.asyncio
async def test_barge_in_register_unregister(client):
    stream_id = "test_stream"
    resp = MagicMock()
    client.register_stream(stream_id, resp)
    assert stream_id in client._active_streams
    assert client._active_streams[stream_id] is resp
    client.unregister_stream(stream_id)
    assert stream_id not in client._active_streams


@pytest.mark.asyncio
async def test_cancel_stream_success(client):
    stream_id = "test_stream"
    resp = AsyncMock()
    client.register_stream(stream_id, resp)
    result = await client.cancel_stream(stream_id)
    assert result is True
    resp.close.assert_awaited_once()
    assert stream_id not in client._active_streams


@pytest.mark.asyncio
async def test_cancel_stream_nonexistent(client):
    result = await client.cancel_stream("nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_create_conversation(client, mock_response):
    mock_response.json = AsyncMock(return_value={"conversation_id": "conv_123"})
    client._session.post.return_value = _make_cm(mock_response)

    conv_id = await client.create_conversation({"agent": "test"})
    assert conv_id == "conv_123"


@pytest.mark.asyncio
async def test_get_conversation(client, mock_response):
    mock_response.json = AsyncMock(return_value={"id": "conv_123", "messages": []})
    client._session.get.return_value = _make_cm(mock_response)

    result = await client.get_conversation("conv_123")
    assert result["id"] == "conv_123"


@pytest.mark.asyncio
async def test_delete_conversation(client, mock_response):
    client._session.delete.return_value = _make_cm(mock_response)
    await client.delete_conversation("conv_123")


@pytest.mark.asyncio
async def test_close_cleans_up(client):
    stream_id = "test_stream"
    resp = AsyncMock()
    client.register_stream(stream_id, resp)
    client._session.closed = False
    await client.close()
    resp.close.assert_awaited_once()
    assert len(client._active_streams) == 0
    client._session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_context_manager():
    with patch.object(ElevenLabsClient, "close", new=AsyncMock()) as mock_close:
        c = ElevenLabsClient(api_key="test_key")
        async with c as result:
            assert result is c
        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_stt_passes_language_hint(client, mock_response):
    mock_response.json = AsyncMock(
        return_value={"text": "hola", "confidence": 0.9, "language": "es", "duration_ms": 1000}
    )
    client._session.post.return_value = _make_cm(mock_response)

    result = await client.speech_to_text(b"audio", language="es")
    assert result.language == "es"


@pytest.mark.asyncio
async def test_create_conversation_no_api_key(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    c = ElevenLabsClient(api_key=None)
    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY not configured"):
        await c.create_conversation({})


@pytest.mark.asyncio
async def test_tts_stream_uses_default_voice(client, mock_response):
    client._session.post.return_value = _make_cm(mock_response)

    async for _ in client.text_to_speech_stream("hello"):
        pass

    call_url = client._session.post.call_args[0][0]
    assert client.default_voice_id in call_url


@pytest.mark.asyncio
async def test_stt_default_content_type(client, mock_response):
    mock_response.json = AsyncMock(
        return_value={"text": "", "confidence": 1.0, "language": "en", "duration_ms": 0}
    )
    client._session.post.return_value = _make_cm(mock_response)

    await client.speech_to_text(b"data")
    call_kwargs = client._session.post.call_args.kwargs
    assert "data" in call_kwargs
