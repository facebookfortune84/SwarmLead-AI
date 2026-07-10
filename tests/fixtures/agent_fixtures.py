import pytest


@pytest.fixture
def simple_agent():
    async def agent(input_data, context):
        return {"echo": input_data}
    return agent


@pytest.fixture
def failing_agent():
    async def agent(input_data, context):
        raise RuntimeError("Intentional failure")
    return agent


@pytest.fixture
def slow_agent():
    import asyncio

    async def agent(input_data, context):
        await asyncio.sleep(0.05)
        return {"slow": True}
    return agent