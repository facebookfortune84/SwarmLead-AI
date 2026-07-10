from typing import Dict, Optional

from pydantic import BaseModel, Field

# ------------------------------------------------------------------
# Core Sub-Configs
# ------------------------------------------------------------------


class LoggingConfig(BaseModel):
    level: str = Field(default="INFO")
    file_path: str = Field(default="logs/swarm.log")
    error_file_path: Optional[str] = Field(default="logs/error.log")


class SchedulerConfig(BaseModel):
    max_concurrent_tasks: int = Field(default=5, ge=1)


class LLMConfig(BaseModel):
    provider: str = Field(default="ollama")
    model: str = Field(default="mistral")

    timeout: int = Field(default=60)
    fallback_model: Optional[str] = None

    max_retries: int = Field(default=3, ge=0)


class FeatureFlags(BaseModel):
    enable_voice: bool = False
    enable_analytics: bool = True
    enable_ab_testing: bool = True
    enable_fallbacks: bool = True


# ------------------------------------------------------------------
# Runtime + Generation Config
# ------------------------------------------------------------------


class GenerationConfig(BaseModel):
    max_tokens: int = Field(default=512, gt=0)
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)


class RuntimeConfig(BaseModel):
    stream: bool = False
    timeout: int = Field(default=60, gt=0)
    max_concurrent_requests: int = Field(default=1, ge=1)


# ------------------------------------------------------------------
# Archetypes
# ------------------------------------------------------------------


class ArchetypeConfig(BaseModel):
    enable_dynamic_selection: bool = True
    enable_adaptive_weights: bool = True

    default_strategy_archetypes: Dict[str, float] = {"architect": 0.5, "planner": 0.5}

    default_outreach_archetypes: Dict[str, float] = {"builder": 1.0}


# ------------------------------------------------------------------
# Main Config
# ------------------------------------------------------------------


class AppConfig(BaseModel):
    environment: str = Field(default="development")

    logging: LoggingConfig = LoggingConfig()
    scheduler: SchedulerConfig = SchedulerConfig()
    llm: LLMConfig = LLMConfig()
    features: FeatureFlags = FeatureFlags()

    generation: GenerationConfig = GenerationConfig()
    runtime: RuntimeConfig = RuntimeConfig()
    archetypes: ArchetypeConfig = ArchetypeConfig()
