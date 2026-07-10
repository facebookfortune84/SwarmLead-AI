import io
import json
import logging

import pytest

from core.agents.base_agent import BaseAgent
from utils.logging import JSONFormatter, get_logger

# ------------------------------------------------------------------
# Helper to capture logs
# ------------------------------------------------------------------


def capture_log(logger):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    return stream, handler


# ------------------------------------------------------------------
# Test Agent Implementations
# ------------------------------------------------------------------


class DummyAgent(BaseAgent):
    async def execute(self, input_data, context, trace_id):
        return {"echo": input_data}


class DummyFailingAgent(BaseAgent):
    async def execute(self, input_data, context, trace_id):
        raise ValueError("failure")


class ContextAgent(BaseAgent):
    async def execute(self, input_data, context, trace_id):
        return {"context": context}


# ✅ NEW — covers delegation wrapper explicitly
class InternalCallAgent(BaseAgent):
    async def execute(self, input_data, context, trace_id):
        return {"internal": True}


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_agent_success():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()
    agent = DummyAgent("test_agent", config)

    result = await agent.run({"x": 1})

    assert result["success"] is True
    assert result["result"]["echo"]["x"] == 1


@pytest.mark.asyncio
async def test_agent_failure():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()
    agent = DummyFailingAgent("fail_agent", config)

    result = await agent.run({})

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_validation_failure():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()
    agent = DummyAgent("test_agent", config)

    result = await agent.run("invalid")

    assert result["success"] is False


def test_validate_rejects_invalid_input():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()
    agent = DummyAgent("test", config)

    with pytest.raises(ValueError):
        agent.validate("invalid")


@pytest.mark.asyncio
async def test_structured_logging():
    from configs.config_loader import ConfigLoader

    logger = get_logger("core.agents.base_agent")
    stream, handler = capture_log(logger)

    try:
        config = ConfigLoader.load()
        agent = DummyAgent("log_agent", config)

        await agent.run({"test": True})

        handler.flush()
        logs = stream.getvalue().strip().split("\n")

        parsed = [json.loads(log) for log in logs if log.strip()]
        info_logs = [log for log in parsed if log["level"] == "INFO"]

        assert len(info_logs) >= 2
    finally:
        logger.removeHandler(handler)


@pytest.mark.asyncio
async def test_context_defaults_to_empty_dict():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()
    agent = ContextAgent("context_test", config)

    result = await agent.run({"x": 1}, context=None)

    assert result["result"]["context"] == {}


@pytest.mark.asyncio
async def test_trace_id_in_logging():
    from configs.config_loader import ConfigLoader

    logger = get_logger("core.agents.base_agent")
    stream, handler = capture_log(logger)

    try:
        config = ConfigLoader.load()
        agent = DummyAgent("trace_agent", config)

        trace_id = "trace-123"
        await agent.run({"x": 1}, trace_id=trace_id)

        handler.flush()
        logs = stream.getvalue().strip().split("\n")
        parsed = [json.loads(log) for log in logs if log.strip()]

        trace_logs = [log for log in parsed if log.get("trace_id") == trace_id]

        assert len(trace_logs) > 0
    finally:
        logger.removeHandler(handler)


@pytest.mark.asyncio
async def test_execute_returns_custom_structure():
    from configs.config_loader import ConfigLoader

    class CustomAgent(BaseAgent):
        async def execute(self, input_data, context, trace_id):
            return {
                "combined": {
                    "input": input_data,
                    "context": context,
                    "trace": trace_id,
                }
            }

    config = ConfigLoader.load()
    agent = CustomAgent("custom_agent", config)

    result = await agent.run({"key": "value"}, context={"ctx": True}, trace_id="trace-xyz")

    assert result["result"]["combined"]["trace"] == "trace-xyz"


# ✅ NEW — explicitly hits internal delegation wrapper
@pytest.mark.asyncio
async def test_internal_execute_wrapper():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()
    agent = InternalCallAgent("internal_agent", config)

    result = await agent._execute_internal({"a": 1}, {}, None)

    assert result["internal"] is True


@pytest.mark.asyncio
async def test_call_llm(monkeypatch):
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    class LLMTestAgent(BaseAgent):
        async def execute(self, input_data, context, trace_id):
            return {}

    agent = LLMTestAgent("llm_test", config)

    async def mock_generate(*args, **kwargs):
        return {"response": "mocked response"}

    agent.llm_client.generate = mock_generate

    result = await agent.call_llm("test prompt")

    assert result == "mocked response"


@pytest.mark.asyncio
async def test_call_llm_missing_response_field():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    class TestAgent(BaseAgent):
        async def execute(self, input_data, context, trace_id):
            return {}

    agent = TestAgent("test_agent", config)

    async def mock_generate(*args, **kwargs):
        return {}  # no "response"

    agent.llm_client.generate = mock_generate

    result = await agent.call_llm("test")

    assert result == ""


@pytest.mark.asyncio
async def test_call_llm_with_model_override():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    class TestAgent(BaseAgent):
        async def execute(self, input_data, context, trace_id):
            return {}

    agent = TestAgent("test_agent", config)

    captured = {}

    async def mock_generate(prompt, model, trace_id):
        captured["model"] = model
        return {"response": "ok"}

    agent.llm_client.generate = mock_generate

    result = await agent.call_llm("prompt", model="custom-model")

    assert result == "ok"
    assert captured["model"] == "custom-model"


@pytest.mark.asyncio
async def test_call_llm_trace_id_propagation(monkeypatch):
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    class TestAgent(BaseAgent):
        async def execute(self, input_data, context, trace_id):
            return {}

    agent = TestAgent("trace_agent", config)

    logger = get_logger("core.agents.base_agent")
    stream, handler = capture_log(logger)

    try:

        async def mock_generate(*args, **kwargs):
            return {"response": "ok"}

        agent.llm_client.generate = mock_generate

        trace_id = "llm-trace"

        await agent.call_llm("prompt", trace_id=trace_id)

        handler.flush()
        logs = stream.getvalue().strip().split("\n")

        parsed = [json.loads(log_line) for log_line in logs if log_line.strip()]

        trace_logs = [log_entry for log_entry in parsed if log_entry.get("trace_id") == trace_id]

        assert len(trace_logs) > 0

    finally:
        logger.removeHandler(handler)
