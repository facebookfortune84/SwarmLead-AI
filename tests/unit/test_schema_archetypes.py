from configs.config_loader import ConfigLoader


def test_archetype_config_exists():
    config = ConfigLoader.load()

    assert hasattr(config, "archetypes")


def test_archetype_defaults():
    config = ConfigLoader.load()

    assert isinstance(config.archetypes.default_strategy_archetypes, dict)
    assert "architect" in config.archetypes.default_strategy_archetypes


def test_toggle_dynamic_selection():
    config = ConfigLoader.load()

    config.archetypes.enable_dynamic_selection = False

    assert config.archetypes.enable_dynamic_selection is False
