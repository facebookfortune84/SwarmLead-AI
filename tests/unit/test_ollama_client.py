import asyncio

import pytest

from core.models.local_llm.ollama_client import OllamaClient


@pytest.mark.asyncio
async def test_generate_success(monkeypatch):
    client = OllamaClient()

    async def mock_call(prompt, model=None, trace_id=None):
        return {"model": "test-model", "response": "hello", "done": True}

    monkeypatch.setattr(client, "_call_ollama", mock_call)

    result = await client.generate("hi")
    assert result["response"] == "hello"


@pytest.mark.asyncio
async def test_retry_logic(monkeypatch):
    client = OllamaClient()

    calls = {"count": 0}

    async def flaky_call(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] < 2:
            raise ValueError("fail")
        return {"response": "ok"}

    monkeypatch.setattr(client, "_call_ollama", flaky_call)

    result = await client.generate("retry test")

    assert result["response"] == "ok"
    assert calls["count"] == 2


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_fallback_model(monkeypatch):
    client = OllamaClient()

    # ✅ Correct config usage
    client.config.llm.fallback_model = "fallback-model"
    client.config.features.enable_fallbacks = True

    calls = {"count": 0}

    async def mock_call(prompt, model, trace_id):
        calls["count"] += 1

        # First attempts fail (primary model)
        if model != "fallback-model":
            raise ValueError("primary failed")

        # Fallback succeeds
        return {
            "model": "fallback-model",
            "response": "fallback success",
            "done": True,
        }

    client._call_ollama = mock_call

    result = await client.generate("test prompt")

    assert result["response"] == "fallback success"
    assert calls["count"] >= 2  # at least one failure + fallback

    async def failing_primary(prompt, model=None, trace_id=None):
        if model != "fallback-model":
            raise ValueError("primary failed")
        return {"response": "fallback success"}

    monkeypatch.setattr(client, "_call_ollama", failing_primary)

    result = await client.generate("test")
    assert result["response"] == "fallback success"


@pytest.mark.asyncio
async def test_concurrency_limit():
    client = OllamaClient()

    async def slow_call(*args, **kwargs):
        await asyncio.sleep(0.05)
        return {"response": "done"}

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(client, "_call_ollama", slow_call)

    tasks = [client.generate("a") for _ in range(3)]

    results = await asyncio.gather(*tasks)

    assert len(results) == 3
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_http_error(monkeypatch):
    client = OllamaClient()

    class MockResponse:
        status_code = 500

        def json(self):
            return {}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: MockClient())

    with pytest.raises(RuntimeError):
        await client._call_ollama("prompt", "model", None)


@pytest.mark.asyncio
async def test_retry_exhaustion_no_fallback():
    client = OllamaClient()

    client.config.features.enable_fallbacks = False
    client.config.llm.fallback_model = None
    client.config.llm.max_retries = 1

    async def always_fail(*args, **kwargs):
        raise ValueError("fail")

    client._call_ollama = always_fail

    with pytest.raises(RuntimeError):
        await client.generate("fail test")


@pytest.mark.asyncio
async def test_no_fallback_when_disabled():
    client = OllamaClient()

    client.config.features.enable_fallbacks = False
    client.config.llm.fallback_model = "fallback-model"

    calls = {"count": 0}

    async def fail_all(prompt, model, trace_id):
        calls["count"] += 1
        raise ValueError("fail")

    client._call_ollama = fail_all

    with pytest.raises(RuntimeError):
        await client.generate("no fallback")

    assert calls["count"] > 0


@pytest.mark.asyncio
async def test_full_http_success(monkeypatch):
    client = OllamaClient()

    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "model": "test-model",
                "response": "hello world",
                "done": True,
            }

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: MockClient())

    result = await client._call_ollama("prompt", "test-model", None)

    assert result["response"] == "hello world"
