from configs.config_loader import ConfigLoader
from core.prompts.archetype_selector import ArchetypeSelector


def test_selector_dynamic_enabled():
    config = ConfigLoader.load()

    selector = ArchetypeSelector(config)

    result = selector.select("growth", "strategy_agent")

    assert isinstance(result, dict)
    assert "planner" in result


def test_selector_default_path():
    config = ConfigLoader.load()
    config.archetypes.enable_dynamic_selection = False

    selector = ArchetypeSelector(config)

    result = selector.select("anything", "strategy_agent")

    assert result == config.archetypes.default_strategy_archetypes


def test_selector_outreach():
    config = ConfigLoader.load()
    selector = ArchetypeSelector(config)

    result = selector.select("convert", "outreach_agent")

    assert "builder" in result


def test_selector_unknown_agent():
    from configs.config_loader import ConfigLoader
    from core.prompts.archetype_selector import ArchetypeSelector

    config = ConfigLoader.load()
    selector = ArchetypeSelector(config)

    result = selector.select("test", "unknown_agent")

    assert result == {}


def test_selector_conversion_branch():
    from configs.config_loader import ConfigLoader
    from core.prompts.archetype_selector import ArchetypeSelector

    config = ConfigLoader.load()
    selector = ArchetypeSelector(config)

    result = selector.select("conversion goal", "strategy_agent")

    assert "architect" in result


def test_selector_no_adaptive_weights(monkeypatch):
    from configs.config_loader import ConfigLoader
    from core.prompts.archetype_selector import ArchetypeSelector

    config = ConfigLoader.load()
    config.archetypes.enable_adaptive_weights = False

    selector = ArchetypeSelector(config)

    result = selector.select("growth", "strategy_agent")

    assert isinstance(result, dict)


def test_selector_default_unknown_agent():
    from configs.config_loader import ConfigLoader
    from core.prompts.archetype_selector import ArchetypeSelector

    config = ConfigLoader.load()
    config.archetypes.enable_dynamic_selection = False

    selector = ArchetypeSelector(config)

    result = selector.select("anything", "unknown")

    assert result == {}


def test_selector_empty_goal():
    from configs.config_loader import ConfigLoader
    from core.prompts.archetype_selector import ArchetypeSelector

    config = ConfigLoader.load()
    selector = ArchetypeSelector(config)

    result = selector.select("", "strategy_agent")

    assert isinstance(result, dict)


def test_selector_outreach_with_adaptive_disabled():
    from configs.config_loader import ConfigLoader
    from core.prompts.archetype_selector import ArchetypeSelector

    config = ConfigLoader.load()
    config.archetypes.enable_adaptive_weights = False

    selector = ArchetypeSelector(config)

    result = selector.select("anything", "outreach_agent")

    assert "builder" in result


def test_selector_goal_case_handling():
    from configs.config_loader import ConfigLoader
    from core.prompts.archetype_selector import ArchetypeSelector

    config = ConfigLoader.load()
    selector = ArchetypeSelector(config)

    # ✅ mixed case input
    result = selector.select("GROWTH", "strategy_agent")

    assert "planner" in result
