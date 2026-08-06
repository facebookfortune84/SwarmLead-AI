"""Tests for VoiceAgentService — session lifecycle, lead capture, model wiring."""

import pytest

from core.services.voice_agent_service import (
    GREETINGS,
    VoiceAgentService,
    voice_agent_service,
)


@pytest.fixture
def service(monkeypatch):
    svc = VoiceAgentService(llm_timeout_s=0.05)

    class FakeLLM:
        async def generate(self, prompt="", num_predict=None, model=None):
            return {"response": "Here is the answer."}

    class FakeTTS:
        async def text_to_speech_bytes(self, text):
            return b"fake-mp3-bytes"

    monkeypatch.setattr(svc, "_llm", FakeLLM())
    monkeypatch.setattr(svc, "_elevenlabs", FakeTTS())
    return svc


@pytest.mark.asyncio
async def test_create_session_returns_greeting_and_audio(service):
    result = await service.create_session("proactive")
    assert result["session_id"].startswith("voice_")
    assert result["visitor_id"].startswith("visitor_")
    assert result["greeting"] == GREETINGS["proactive"]
    assert result["greeting_audio_b64"] == "ZmFrZS1tcDMtYnl0ZXM="  # base64(fake-mp3-bytes)


@pytest.mark.asyncio
async def test_create_session_unknown_greeting_falls_back(service):
    result = await service.create_session("nonsense")
    assert result["greeting"] == GREETINGS["proactive"]


@pytest.mark.asyncio
async def test_process_message_returns_reply_and_intent(service):
    created = await service.create_session("voice")
    sid = created["session_id"]
    out = await service.process_message(sid, "What are the pricing plans?")
    assert out["session_id"] == sid
    assert out["reply"] == "Here is the answer."
    assert out["reply_audio_b64"] == "ZmFrZS1tcDMtYnl0ZXM="
    assert out["intent"] == "pricing"


@pytest.mark.asyncio
async def test_process_message_creates_session_if_missing(service):
    out = await service.process_message("voice_does_not_exist", "hello")
    assert out["session_id"] != "voice_does_not_exist"


@pytest.mark.asyncio
async def test_process_message_llm_failure_uses_scripted(service, monkeypatch):
    async def boom(prompt="", num_predict=None, model=None):
        raise RuntimeError("ollama down")

    monkeypatch.setattr(service._llm, "generate", boom)
    created = await service.create_session("voice")
    out = await service.process_message(created["session_id"], "tell me about workflows")
    assert "Workflows" in out["reply"]


@pytest.mark.asyncio
async def test_end_session_removes(service):
    created = await service.create_session("voice")
    sid = created["session_id"]
    assert service.end_session(sid) is True
    assert service.end_session(sid) is False


def test_detect_intent_variants(service):
    assert service._detect_intent("how much does it cost?") == "pricing"
    assert service._detect_intent("I want to sign up") == "onboarding"
    assert service._detect_intent("qualify my leads") == "qualify"
    assert service._detect_intent("help me launch a business") == "launch"
    assert service._detect_intent("what is the weather") == "general"


def test_scripted_for_build(service):
    reply = service._scripted_for("I want to build a startup")
    assert "Company Builder" in reply


def test_scripted_for_outreach(service):
    reply = service._scripted_for("help with outreach campaigns")
    assert "Outreach" in reply


def test_scripted_for_workflows(service):
    reply = service._scripted_for("automate my follow-up")
    assert "Workflows" in reply


def test_scripted_for_tickets(service):
    reply = service._scripted_for("create a support ticket")
    assert "ticket" in reply.lower()


def test_scripted_for_pricing(service):
    reply = service._scripted_for("what's the price?")
    assert "$29" in reply or "29" in reply


def test_capture_lead_rejects_invalid(service):
    assert service.capture_lead("")["created"] is False
    assert service.capture_lead("notanemail")["created"] is False


def test_capture_lead_persists(service, tmp_path, monkeypatch):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    import core.models  # noqa: F401  (register models on Base.metadata)
    from core.persistence.base import Base

    db_path = tmp_path / "leads.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)

    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)

    result = service.capture_lead("   Visitor@Example.com  ", name="Visitor", company="ACME")
    assert result["created"] is True
    assert result["email"] == "visitor@example.com"
    assert result["lead_id"]

    db = test_session()
    try:
        from core.models import Lead

        row = db.query(Lead).filter(Lead.email == "visitor@example.com").first()
        assert row is not None
        assert row.name == "Visitor"
        assert row.company == "ACME"
        assert row.intent_score == 80
        assert row.needs_review is True
    finally:
        db.close()

    # dedup on repeat capture
    second = service.capture_lead("Visitor@Example.com")
    assert second["created"] is False
    assert second["lead_id"] == result["lead_id"]


def test_capture_lead_dedup_flags_review(service, tmp_path, monkeypatch):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    import core.models  # noqa: F401
    from core.persistence.base import Base

    db_path = tmp_path / "leads2.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)

    first = service.capture_lead("a@b.com", name="A")
    assert first["created"] is True
    db = test_session()
    try:
        from core.models import Lead

        db.query(Lead).filter(Lead.email == "a@b.com").update(
            {"needs_review": False}
        )
        db.commit()
    finally:
        db.close()

    second = service.capture_lead("a@b.com")
    assert second["created"] is False

    db = test_session()
    try:
        from core.models import Lead

        row = db.query(Lead).filter(Lead.email == "a@b.com").first()
        assert row.needs_review is True
    finally:
        db.close()


def test_model_status_reports_active_model(service):
    status = service.model_status()
    assert "active_model" in status
    assert status["provider"] == "ollama"


def test_greetings_cover_all_keys():
    for key in ("proactive", "scroll", "exit_intent", "voice"):
        assert key in GREETINGS
        assert GREETINGS[key]


def test_singleton_is_service():
    assert isinstance(voice_agent_service, VoiceAgentService)
