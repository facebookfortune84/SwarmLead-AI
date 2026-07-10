def test_default_config_load():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    assert config.environment == "development"
    assert config.scheduler.max_concurrent_tasks == 5
    assert config.llm.model == "mistral"


def test_env_override(monkeypatch):
    from configs.config_loader import ConfigLoader

    monkeypatch.setenv("ENV", "production")

    config = ConfigLoader.load()

    assert config.environment == "production"


def test_feature_flags():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    assert config.features.enable_analytics is True
    assert config.features.enable_voice is False


def test_schema_validation():
    from configs.schema import SchedulerConfig
    import pytest

    with pytest.raises(Exception):
        SchedulerConfig(max_concurrent_tasks=0)  # invalid


def test_generation_defaults():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    assert config.generation.max_tokens == 512
    assert config.generation.temperature == 0.3


def test_runtime_defaults():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    assert config.runtime.stream is False
    assert config.runtime.max_concurrent_requests == 1


def test_generation_validation_limits():
    from configs.schema import GenerationConfig
    import pytest

    with pytest.raises(Exception):
        GenerationConfig(max_tokens=0)

    with pytest.raises(Exception):
        GenerationConfig(temperature=1.5)

    with pytest.raises(Exception):
        GenerationConfig(top_p=-0.1)


def test_runtime_validation_limits():
    from configs.schema import RuntimeConfig
    import pytest

    with pytest.raises(Exception):
        RuntimeConfig(timeout=0)

    with pytest.raises(Exception):
        RuntimeConfig(max_concurrent_requests=0)


def test_llm_config_validation():
    from configs.schema import LLMConfig
    import pytest

    config = LLMConfig()
    assert config.max_retries == 3

    with pytest.raises(Exception):
        LLMConfig(max_retries=-1)


def test_optional_fields():
    from configs.schema import LLMConfig, LoggingConfig

    llm_config = LLMConfig()
    assert llm_config.fallback_model is None

    logging_config = LoggingConfig()
    assert logging_config.error_file_path == "logs/error.log"


def test_full_config_integrity():
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    assert config.environment in ["development", "production"]

    # LLM safety guarantees
    assert config.runtime.stream is False
    assert config.runtime.max_concurrent_requests >= 1

    # Generation sanity
    assert 0 <= config.generation.temperature <= 1
    assert 0 <= config.generation.top_p <= 1

    # Scheduler safety
    assert config.scheduler.max_concurrent_tasks >= 1
