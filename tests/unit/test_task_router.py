import pytest

from core.orchestration.task_router import TaskRouter, DomainViolationError


@pytest.mark.asyncio
async def test_route_to_registered_agent(router, agent_manager, simple_agent):
    agent_manager.register_agent("agent1", simple_agent)
    result = await router.route("agent1", {"x": 1})
    assert result["success"] is True
    assert result["result"]["echo"] == {"x": 1}


@pytest.mark.asyncio
async def test_missing_route(router):
    with pytest.raises(ValueError, match="No agent registered for task"):
        await router.route("missing", {})


@pytest.mark.asyncio
async def test_register_and_list_routes(router, agent_manager, simple_agent):
    agent_manager.register_agent("agent1", simple_agent)
    router.register_agent_domains("agent1", ["simulation"])
    assert router.get_agent_for_domain("simulation") == "agent1"


@pytest.mark.asyncio
async def test_domain_classification(router):
    domain = router._classify_domain("generate_code", {"language": "python"})
    assert domain == "product_code"
    domain = router._classify_domain("send_email", {"to": "test@example.com"})
    assert domain == "external_comms"
    domain = router._classify_domain("unknown_task", {})
    assert domain == "simulation"


@pytest.mark.asyncio
async def test_domain_autonomy_gating():
    from core.auth.agent_identity import AgentIdentityRegistry, AgentIdentity, AgentDomain
    router = TaskRouter()
    AgentIdentityRegistry.register(
        AgentIdentity(
            agent_id="builder_agent", agent_type="BuilderAgent", display_name="Builder Agent",
            domains={AgentDomain.PRODUCT_CODE},
            tool_allowlist={"*"}, data_allowlist={"*"},
        )
    )
    router.register_agent_domains("builder_agent", ["product_code"])
    router.register_route("build", "builder_agent")
    allowed = router._domain_allowed("builder_agent", "product_code")
    assert allowed is True
    blocked = router._domain_allowed("builder_agent", "financial")
    assert blocked is False


@pytest.mark.asyncio
async def test_domain_violation_raises_error():
    from core.auth.agent_identity import AgentIdentityRegistry, AgentIdentity, AgentDomain
    router = TaskRouter()
    AgentIdentityRegistry.register(
        AgentIdentity(
            agent_id="builder_agent", agent_type="BuilderAgent", display_name="Builder Agent",
            domains={AgentDomain.PRODUCT_CODE},
            tool_allowlist={"*"}, data_allowlist={"*"},
        )
    )
    router.register_agent_domains("builder_agent", ["product_code"])
    router.register_route("build", "builder_agent")
    router.register_route("charge_customer", "builder_agent")
    with pytest.raises(DomainViolationError):
        await router.route("charge_customer", {"amount": 100})


def test_get_agent_domains(router):
    router.register_agent_domains("test_agent", ["product_code", "simulation"])
    domains = router.get_agent_domains("test_agent")
    assert "product_code" in domains
    assert "simulation" in domains


def test_unregister_route():
    router = TaskRouter()
    router.register_route("task1", "agent1")
    assert router.unregister_route("task1") is True
    assert router.unregister_route("task1") is False


def test_duplicate_route_raises_error():
    router = TaskRouter()
    router.register_route("task1", "agent1")
    with pytest.raises(ValueError, match="already registered"):
        router.register_route("task1", "agent2")
