"""
Voice model registry — pick which model powers the Genesis voice assistant.

The voice assistant is a text-in/text-out conversational loop (browser STT ->
Ollama LLM -> ElevenLabs TTS). The single knob that changes *what the agent
sounds like and how well it thinks* is the LLM model name. This module makes
that pluggable:

- `VOICE_MODEL` env var (e.g. ``VOICE_MODEL=genesis-voice:latest``) selects a
  custom fine-tuned model served by Ollama. If unset, the platform's default
  LLM (``configs.schema.LLMConfig.model``) is used.
- `VOICE_MODEL_OVERRIDES` lets you tune generation per model
  (temperature / top_p / max_tokens) without touching config files.
- `VOICE_MODEL_BASE_URL` overrides the Ollama endpoint for this model only
  (handy when the trained model runs on a separate host).

The intended workflow: `ollama create genesis-voice:latest -f Modelfile`, set
``VOICE_MODEL=genesis-voice:latest`` in ``.env.docker.local``, and the landing
agent immediately runs on your trained model. See ``docs/voice_model_integration.md``.
"""

import logging
import os
from dataclasses import dataclass
from typing import Dict

from configs.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

DEFAULT_VOICE_MODEL_ENV = "VOICE_MODEL"


@dataclass(frozen=True)
class VoiceModelConfig:
    """Resolved settings for the model that powers the voice assistant."""

    model: str
    base_url: str
    temperature: float
    top_p: float
    max_tokens: int
    provider: str = "ollama"
    source: str = "default"  # "default" | "voice_model_env" | "ollama_override"

    def to_dict(self) -> Dict[str, object]:
        return {
            "model": self.model,
            "provider": self.provider,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "source": self.source,
        }


def _parse_overrides() -> Dict[str, Dict[str, float]]:
    """Parse ``VOICE_MODEL_OVERRIDES`` as ``model=temp,top_p,max_tokens;...``."""
    raw = os.getenv("VOICE_MODEL_OVERRIDES", "")
    parsed: Dict[str, Dict[str, float]] = {}
    if not raw:
        return parsed
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        model, _, values = chunk.partition("=")
        parts = [p.strip() for p in values.split(",")]
        if not parts or not parts[0]:
            continue
        entry: Dict[str, float] = {"temperature": 0.3, "top_p": 0.9, "max_tokens": 512}
        try:
            entry["temperature"] = float(parts[0])
            if len(parts) > 1:
                entry["top_p"] = float(parts[1])
            if len(parts) > 2:
                entry["max_tokens"] = float(parts[2])
        except ValueError:
            logger.warning("Ignoring malformed VOICE_MODEL_OVERRIDES entry: %r", chunk)
            continue
        parsed[model.strip()] = entry
    return parsed


class VoiceModelRegistry:
    """Resolves and reports the active voice LLM configuration."""

    def __init__(self) -> None:
        self._overrides = _parse_overrides()

    def resolve(self) -> VoiceModelConfig:
        """Return the effective voice model config for this environment."""
        config = ConfigLoader.load()

        env_model = os.getenv(DEFAULT_VOICE_MODEL_ENV, "").strip()
        base_url = (
            os.getenv("VOICE_MODEL_BASE_URL", "").rstrip("/")
            or os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434").rstrip("/")
        ) + "/api/generate"

        if env_model:
            override = self._overrides.get(env_model)
            return VoiceModelConfig(
                model=env_model,
                base_url=base_url,
                temperature=(
                    override["temperature"]
                    if override
                    else config.generation.temperature
                ),
                top_p=override["top_p"] if override else config.generation.top_p,
                max_tokens=int(
                    override["max_tokens"] if override else config.generation.max_tokens
                ),
                source="voice_model_env",
            )

        return VoiceModelConfig(
            model=config.llm.model,
            base_url=base_url,
            temperature=config.generation.temperature,
            top_p=config.generation.top_p,
            max_tokens=config.generation.max_tokens,
            source="default",
        )

    def status(self) -> Dict[str, object]:
        """Human-readable report for the ops / autonomy console."""
        cfg = self.resolve()
        return {
            "active_model": cfg.model,
            "provider": cfg.provider,
            "base_url": cfg.base_url,
            "source": cfg.source,
            "custom_model_configured": cfg.source == "voice_model_env",
            "hint": (
                "Set VOICE_MODEL=<trained-model> in .env.docker.local to use your "
                "custom voice model."
                if cfg.source != "voice_model_env"
                else "Using custom voice model from VOICE_MODEL."
            ),
        }


voice_model_registry = VoiceModelRegistry()

__all__ = [
    "VoiceModelConfig",
    "VoiceModelRegistry",
    "voice_model_registry",
    "DEFAULT_VOICE_MODEL_ENV",
]
