"""Tests for the voice model registry (pluggable custom voice models)."""

import os

import pytest

from core.services.voice_model import (
    DEFAULT_VOICE_MODEL_ENV,
    VoiceModelRegistry,
    _parse_overrides,
)


def test_resolve_default_uses_config_model(monkeypatch):
    monkeypatch.delenv(DEFAULT_VOICE_MODEL_ENV, raising=False)
    monkeypatch.delenv("VOICE_MODEL_BASE_URL", raising=False)
    cfg = VoiceModelRegistry().resolve()
    assert cfg.source == "default"
    assert cfg.model  # config default (e.g. llama3.2:3b)
    assert cfg.provider == "ollama"
    assert cfg.base_url.endswith("/api/generate")


def test_resolve_uses_voice_model_env(monkeypatch):
    monkeypatch.setenv(DEFAULT_VOICE_MODEL_ENV, "genesis-voice:latest")
    monkeypatch.setenv("OLLAMA_API_BASE", "http://model-host:11434")
    cfg = VoiceModelRegistry().resolve()
    assert cfg.source == "voice_model_env"
    assert cfg.model == "genesis-voice:latest"
    assert cfg.base_url == "http://model-host:11434/api/generate"


def test_resolve_voice_model_base_url_wins(monkeypatch):
    monkeypatch.setenv(DEFAULT_VOICE_MODEL_ENV, "custom:latest")
    monkeypatch.setenv("VOICE_MODEL_BASE_URL", "http://voice-svc:9999/")
    cfg = VoiceModelRegistry().resolve()
    assert cfg.base_url == "http://voice-svc:9999/api/generate"


def test_status_reports_custom_model(monkeypatch):
    monkeypatch.setenv(DEFAULT_VOICE_MODEL_ENV, "genesis-voice:latest")
    status = VoiceModelRegistry().status()
    assert status["active_model"] == "genesis-voice:latest"
    assert status["custom_model_configured"] is True
    assert status["source"] == "voice_model_env"


def test_status_hint_when_default(monkeypatch):
    monkeypatch.delenv(DEFAULT_VOICE_MODEL_ENV, raising=False)
    status = VoiceModelRegistry().status()
    assert status["custom_model_configured"] is False
    assert "VOICE_MODEL" in status["hint"]


def test_parse_overrides_empty():
    os.environ["VOICE_MODEL_OVERRIDES"] = ""
    assert _parse_overrides() == {}
    os.environ["VOICE_MODEL_OVERRIDES"] = "   "
    assert _parse_overrides() == {}


def test_parse_overrides_single():
    os.environ["VOICE_MODEL_OVERRIDES"] = "genesis-voice:latest=0.2,0.8,160"
    parsed = _parse_overrides()
    assert parsed["genesis-voice:latest"] == {
        "temperature": 0.2,
        "top_p": 0.8,
        "max_tokens": 160,
    }


def test_parse_overrides_multiple_and_partial():
    os.environ["VOICE_MODEL_OVERRIDES"] = (
        "a=0.1,0.7,100;b=0.4;c=0.5,0.99,512"
    )
    parsed = _parse_overrides()
    assert parsed["a"] == {"temperature": 0.1, "top_p": 0.7, "max_tokens": 100}
    assert parsed["b"] == {"temperature": 0.4, "top_p": 0.9, "max_tokens": 512}
    assert parsed["c"] == {"temperature": 0.5, "top_p": 0.99, "max_tokens": 512}


def test_parse_overrides_ignores_malformed():
    os.environ["VOICE_MODEL_OVERRIDES"] = "bad=notnumbers;good=0.3"
    parsed = _parse_overrides()
    assert "bad" not in parsed
    assert parsed["good"]["temperature"] == 0.3


def test_override_applied_to_resolve(monkeypatch):
    monkeypatch.setenv(DEFAULT_VOICE_MODEL_ENV, "tuned:latest")
    monkeypatch.setenv("VOICE_MODEL_OVERRIDES", "tuned:latest=0.15,0.75,140")
    cfg = VoiceModelRegistry().resolve()
    assert cfg.temperature == 0.15
    assert cfg.top_p == 0.75
    assert cfg.max_tokens == 140
