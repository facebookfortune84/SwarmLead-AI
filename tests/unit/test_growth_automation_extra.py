"""Extra coverage for the autonomous growth loop.

Targets the branches not exercised by test_growth_automation.py: phase
failure isolation, discovery persistence, DB-backed lead qualification,
LLM content paths, voice learning, monetize quoting, approval dispatch
outcomes, purge's DB marking, state persistence errors, and the background
loop lifecycle. Everything is mocked — no network, Ollama, or real DB.
"""

import asyncio

import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import core.models  # noqa: F401  (register models on Base.metadata)
import core.services.growth_automation as _mod
from core.models import Lead
from core.persistence.base import Base
from core.services.deliverability import deliverability
from core.services.growth_automation import GrowthAutomation


def _make_instance(tmp_path, monkeypatch, discovery="0", use_llm="0", **env):
    monkeypatch.setenv("GROWTH_DISCOVERY", discovery)
    monkeypatch.setenv("GROWTH_USE_LLM", use_llm)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(deliverability, "suppression_path", tmp_path / "suppression.json")
    monkeypatch.setattr(deliverability, "_suppressed", {})
    instance = GrowthAutomation(state_path=tmp_path / "growth_state.json")
    instance.enabled = True
    return instance


@pytest.fixture
def ga(tmp_path, monkeypatch):
    return _make_instance(tmp_path, monkeypatch)


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "growth.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)
    return test_session


# ------------------------------------------------------------------ state
def test_load_state_recovers_from_corrupt_file(tmp_path):
    state_path = tmp_path / "growth_state.json"
    state_path.write_text("{not valid json", encoding="utf-8")
    instance = GrowthAutomation(state_path=state_path)
    assert instance.state["cycle_count"] == 0
    assert instance.state["artifacts"] == {"seo_pages": [], "content_drafts": []}


def test_load_state_handles_oserror(tmp_path):
    state_path = tmp_path / "statedir"
    state_path.mkdir()
    instance = GrowthAutomation(state_path=state_path)
    assert instance.state["cycle_count"] == 0


def test_save_state_handles_oserror(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    bad_state = blocker / "sub" / "state.json"
    instance = GrowthAutomation(state_path=bad_state)
    instance.state["cycle_count"] = 3
    instance._save_state()
    assert instance.state["cycle_count"] == 3


# ----------------------------------------------------------------- run
@pytest.mark.asyncio
async def test_run_cycle_already_running(ga):
    lock = ga._cycle_lock()
    await lock.acquire()
    try:
        result = await ga.run_cycle(reason="busy")
        assert result == {"status": "already_running", "reason": "busy"}
    finally:
        lock.release()


@pytest.mark.asyncio
async def test_failing_phase_does_not_kill_cycle(ga, monkeypatch):
    async def boom():
        raise RuntimeError("seo boom")

    monkeypatch.setattr(ga, "_phase_seo", boom)
    monkeypatch.setattr(ga, "_qualified_leads", lambda limit: [])

    cycle = await ga.run_cycle(reason="test")
    assert cycle["phases"]["seo"]["status"] == "error"
    assert cycle["phases"]["seo"]["error"] == "seo boom"
    assert cycle["phases"]["discovery"]["status"] == "ok"
    assert cycle["phases"]["outreach"]["status"] == "ok"
    assert ga.state["last_errors"][-1] == "seo: seo boom"
    assert ga.state["cycle_count"] >= 1


# ------------------------------------------------------------------- seo
@pytest.mark.asyncio
async def test_seo_phase_merges_existing_pages(ga):
    ga.state["artifacts"]["seo_pages"] = [
        {"url": "/industries/e-commerce", "title": "old", "status": "draft"}
    ]
    result = await ga._phase_seo()
    assert result["status"] == "ok"
    urls = [p["url"] for p in ga.state["artifacts"]["seo_pages"]]
    assert "/industries/e-commerce" in urls
    assert result["cumulative_pages"] >= 1


# --------------------------------------------------------------- content
async def _content_phase_with(instance, monkeypatch, generate):
    from core.agents.content.content_agent import ContentAgent

    monkeypatch.setattr(ContentAgent, "generate_content", generate)
    return await instance._phase_content()


@pytest.mark.asyncio
async def test_content_phase_uses_llm_success(tmp_path, monkeypatch):
    calls = []

    async def fake_generate(self, template_name, context, seo_keywords=None):
        calls.append(template_name)
        return {"content": f"# {context['topic']} body", "seo_score": 91.0}

    instance = _make_instance(tmp_path, monkeypatch, use_llm="1")
    result = await _content_phase_with(instance, monkeypatch, fake_generate)
    assert result["status"] == "ok"
    assert result["drafts_ready"] == len(_mod.GTM_TASKS)
    assert len(calls) == len(_mod.GTM_TASKS)
    drafts = instance.state["artifacts"]["content_drafts"]
    assert all(d["seo_score"] == 91.0 for d in drafts)


@pytest.mark.asyncio
async def test_content_phase_llm_timeout(tmp_path, monkeypatch):
    async def slow_generate(self, template_name, context, seo_keywords=None):
        raise asyncio.TimeoutError()

    instance = _make_instance(tmp_path, monkeypatch, use_llm="1")
    result = await _content_phase_with(instance, monkeypatch, slow_generate)
    assert result["status"] == "ok"
    drafts = instance.state["artifacts"]["content_drafts"]
    assert drafts
    assert all("timed out" in d["content"] for d in drafts)


@pytest.mark.asyncio
async def test_content_phase_llm_error(tmp_path, monkeypatch):
    async def err_generate(self, template_name, context, seo_keywords=None):
        return {"error": "llm unavailable"}

    instance = _make_instance(tmp_path, monkeypatch, use_llm="1")
    with pytest.raises(RuntimeError, match="llm unavailable"):
        await _content_phase_with(instance, monkeypatch, err_generate)


@pytest.mark.asyncio
async def test_content_phase_merges_existing_drafts(ga):
    ga.state["artifacts"]["content_drafts"] = [
        {"task": "Draft_BargeIn_Feature_Post", "phase": "old", "content": "old"}
    ]
    result = await ga._phase_content()
    assert result["status"] == "ok"
    tasks = [d["task"] for d in ga.state["artifacts"]["content_drafts"]]
    assert "Draft_BargeIn_Feature_Post" in tasks
    assert result["cumulative_drafts"] >= 1


# -------------------------------------------------------------- discovery
@pytest.mark.asyncio
async def test_discovery_phase_writes_leads(tmp_path, monkeypatch, test_db):
    from core.services import lead_discovery as ld_mod
    from core.services.lead_discovery import DiscoveredLead

    db = test_db()
    try:
        db.add(Lead(email="existing@acmeplumbing.com", name="Existing", status="NEW", intent_score=70))
        db.commit()
    finally:
        db.close()

    class FakeDiscovery:
        async def discover(self, max_targets=6):
            return [
                DiscoveredLead(
                    email="existing@acmeplumbing.com",
                    name="Existing",
                    company="Acme Plumbing",
                    website="https://acmeplumbing.com",
                    vertical="Plumbing",
                    intent_score=70,
                ),
                DiscoveredLead(
                    email="owner@smithplumbing.com",
                    name="Sam Smith",
                    company="Smith Plumbing",
                    website="https://smithplumbing.com",
                    vertical="Plumbing",
                    intent_score=82,
                    confidence="high",
                    details={"mx": "mx.smithplumbing.com"},
                ),
            ]

    monkeypatch.setattr(ld_mod, "lead_discovery", FakeDiscovery())
    instance = _make_instance(tmp_path, monkeypatch, discovery="1")
    result = await instance._phase_discovery()
    assert result["status"] == "ok"
    assert result["discovered"] == 2
    assert result["written"] == 1
    assert result["verticals"] == ["Plumbing"]

    db = test_db()
    try:
        rows = db.query(Lead).filter(Lead.email == "owner@smithplumbing.com").all()
        assert len(rows) == 1
        assert rows[0].status == "NEW"
        assert rows[0].intent_score == 82
        assert rows[0].company == "Smith Plumbing"
        assert '"source": "search_website"' in (rows[0].metadata_json or "")
    finally:
        db.close()


# ------------------------------------------------------ qualified leads
def test_qualified_leads_db_filtering(tmp_path, monkeypatch, test_db):
    instance = _make_instance(tmp_path, monkeypatch)
    db = test_db()
    try:
        db.add_all(
            [
                Lead(email="bad@example.com", name="Bad", status="NEW", intent_score=99),
                Lead(email="owner2@smithplumbing.com", name="Owner2", status="NEW", intent_score=95),
                Lead(email="bob@mailinator.com", name="Bob", status="NEW", intent_score=90),
                Lead(email="suppressed@acmeplumbing.com", name="S", status="NEW", intent_score=85),
                Lead(email="owner@smithplumbing.com", name="Owner", status="NEW", intent_score=80),
                Lead(email="nosuppress@acmeplumbing.com", name="N", status="NEW", intent_score=70),
                Lead(email="notanemail", name="X", status="NEW", intent_score=98),
                Lead(email="purged@acmeplumbing.com", name="P", status="PURGED", intent_score=88),
                Lead(email="invalid@acmeplumbing.com", name="I", status="NEW", email_invalid=True, intent_score=60),
            ]
        )
        db.commit()
    finally:
        db.close()
    deliverability.suppress("suppressed@acmeplumbing.com", "test")

    out = instance._qualified_leads(limit=2)
    assert [r["email"] for r in out] == [
        "owner2@smithplumbing.com",
        "owner@smithplumbing.com",
    ]
    assert all(r["intent_score"] > 0 for r in out)


def test_qualified_leads_falls_back_on_db_error(tmp_path, monkeypatch):
    def raise_session():
        raise RuntimeError("db down")

    monkeypatch.setattr("core.persistence.session.SessionLocal", raise_session)
    instance = _make_instance(tmp_path, monkeypatch)
    out = instance._qualified_leads(limit=5)
    assert out == [
        {
            "email": "owner@smithplumbing.com",
            "name": "Example Lead",
            "company": "Smith Plumbing",
            "intent_score": 80,
        }
    ]


# --------------------------------------------------------------- outreach
@pytest.mark.asyncio
async def test_outreach_phase_skips_suppressed_duplicate_domains_and_limits(ga, monkeypatch):
    deliverability.suppress("supp@x.com", "test")
    leads = [
        {"email": "a@one.com", "name": "A", "company": "One", "intent_score": 80},
        {"email": "b@one.com", "name": "B", "company": "One", "intent_score": 80},
        {"email": "c2@one.com", "name": "C2", "company": "One", "intent_score": 80},
        {"email": "supp@x.com", "name": "Supp", "company": "Supp", "intent_score": 80},
        {"email": "d1@d1.com", "name": "D1", "company": "D1 Co", "intent_score": 80},
        {"email": "d2@d2.com", "name": "D2", "company": "D2 Co", "intent_score": 80},
        {"email": "d3@d3.com", "name": "D3", "company": "D3 Co", "intent_score": 80},
        {"email": "d4@d4.com", "name": "D4", "company": "D4 Co", "intent_score": 80},
        {"email": "d5@d5.com", "name": "D5", "company": "D5 Co", "intent_score": 80},
        {"email": "d6@d6.com", "name": "D6", "company": "D6 Co", "intent_score": 80},
        {"email": "d7@d7.com", "name": "D7", "company": "D7 Co", "intent_score": 80},
    ]

    monkeypatch.setattr(ga, "_qualified_leads", lambda limit: leads)
    result = await ga._phase_outreach()
    assert result["status"] == "ok"
    assert result["leads_qualified"] == len(leads)
    assert result["drafted"] == 8
    assert ga._pending_count("outreach_send") == 8
    sent = [a["payload"]["to_email"] for a in ga.state["approval_queue"] if a["kind"] == "outreach_send"]
    assert "a@one.com" in sent
    assert "b@one.com" in sent
    assert "c2@one.com" not in sent
    assert "supp@x.com" not in sent
    assert len(sent) == 8


@pytest.mark.asyncio
async def test_outreach_skips_already_contacted(ga, monkeypatch):
    ga._enqueue(
        "outreach_send",
        {"to_email": "a@one.com", "lead_name": "A", "subject": "s", "body": "b"},
    )
    leads = [
        {"email": "a@one.com", "name": "A", "company": "One", "intent_score": 80},
        {"email": "b@two.com", "name": "B", "company": "Two", "intent_score": 80},
    ]
    monkeypatch.setattr(ga, "_qualified_leads", lambda limit: leads)
    result = await ga._phase_outreach()
    assert result["drafted"] == 1
    sent = [a["payload"]["to_email"] for a in ga.state["approval_queue"] if a["kind"] == "outreach_send"]
    assert sent.count("a@one.com") == 1
    assert "b@two.com" in sent


# ------------------------------------------------------------------ voice
@pytest.mark.asyncio
async def test_voice_phase_learns_boosts(tmp_path, monkeypatch):
    from core.services.product_knowledge import product_knowledge

    learned = []

    def fake_snapshot():
        return {
            "monetization": {"count": 3, "terms": ["price", "cost", "trial", "warp"]},
            "support": {"count": 5, "terms": ["ticket", "support", "issue", "bug"]},
            "chunk:Pricing": 4,
        }

    def fake_learn(boosts):
        learned.append(boosts)

    monkeypatch.setattr(product_knowledge, "analytics_snapshot", fake_snapshot)
    monkeypatch.setattr(product_knowledge, "learn", fake_learn)
    instance = _make_instance(tmp_path, monkeypatch)

    result = await instance._phase_voice()
    assert result["status"] == "ok"
    assert result["boosts_applied"] == {
        "price": 0.4,
        "cost": 0.4,
        "trial": 0.4,
        "ticket": 0.3,
        "support": 0.3,
        "issue": 0.3,
    }
    assert learned, "learn must be called when boosts are computed"
    assert instance.state["learned_keyword_boosts"]["price"] == 0.4
    assert instance.state["learned_keyword_boosts"]["support"] == 0.3


@pytest.mark.asyncio
async def test_voice_phase_no_boosts_when_counts_low(tmp_path, monkeypatch):
    from core.services.product_knowledge import product_knowledge

    learned = []

    def fake_snapshot():
        return {
            "monetization": {"count": 1, "terms": ["price"]},
            "support": {"count": 2, "terms": ["ticket"]},
        }

    def fake_learn(boosts):
        learned.append(boosts)

    monkeypatch.setattr(product_knowledge, "analytics_snapshot", fake_snapshot)
    monkeypatch.setattr(product_knowledge, "learn", fake_learn)
    instance = _make_instance(tmp_path, monkeypatch)

    result = await instance._phase_voice()
    assert result["boosts_applied"] == {}
    assert learned == []


# ---------------------------------------------------------------- monetize
@pytest.mark.asyncio
async def test_monetize_phase_prepares_quotes(tmp_path, monkeypatch):
    from core.services.monetization import monetization

    def fake_offer(lead, **kwargs):
        if lead["email"] == "q3@biz2.com":
            return {
                "tier": "growth",
                "billing": "monthly",
                "checkout_url": None,
                "message": "no checkout",
            }
        return {
            "tier": "growth",
            "billing": "monthly",
            "checkout_url": "https://checkout.stripe.com/c/test",
            "message": "Your workspace is ready",
        }

    monkeypatch.setattr(monetization, "offer_for", fake_offer)
    instance = _make_instance(tmp_path, monkeypatch)
    instance._enqueue(
        "quote_send",
        {
            "to_email": "q1@acme.com",
            "lead_name": "Q1",
            "subject": "already quoted",
            "body": "already quoted",
            "tier": "growth",
            "checkout_url": "https://checkout.stripe.com/c/old",
        },
    )
    monkeypatch.setattr(
        instance,
        "_funnel_snapshot",
        lambda: {
            "visitors": 100,
            "leads": 10,
            "users": 2,
            "tickets": 1,
            "activation_rate": 0.2,
            "conversion_rate": 0.05,
        },
    )
    monkeypatch.setattr(
        instance,
        "_high_intent_leads",
        lambda limit: [
            {"email": "q1@acme.com", "name": "Q1", "intent_score": 90},
            {"email": "q2@biz.com", "name": "Q2", "intent_score": 88},
            {"email": "q3@biz2.com", "name": "Q3", "intent_score": 85},
            {"email": "q4@biz3.com", "name": "Q4", "intent_score": 82},
            {"email": "q5@biz4.com", "name": "Q5", "intent_score": 80},
        ],
    )

    result = await instance._phase_monetize()
    assert result["status"] == "ok"
    assert result["quotes_prepared"] == 2
    assert instance._pending_count("quote_send") == 3
    quotes = [a for a in instance.state["approval_queue"] if a["kind"] == "quote_send"]
    quoted_emails = [a["payload"]["to_email"] for a in quotes]
    assert "q1@acme.com" in quoted_emails  # pre-seeded (skipped by already-quoted)
    assert "q2@biz.com" in quoted_emails
    assert "q3@biz2.com" not in quoted_emails  # no checkout URL
    assert "q4@biz3.com" in quoted_emails
    assert "q5@biz4.com" not in quoted_emails  # hit the quote limit break
    assert all(
        a["payload"]["checkout_url"]
        for a in quotes
        if a["payload"]["to_email"] not in {"q1@acme.com", "q3@biz2.com"}
    )


def test_funnel_snapshot_falls_back_on_db_error(tmp_path, monkeypatch):
    def raise_session():
        raise RuntimeError("db gone")

    monkeypatch.setattr("core.persistence.session.SessionLocal", raise_session)
    instance = _make_instance(tmp_path, monkeypatch)
    snap = instance._funnel_snapshot()
    assert snap["visitors"] == 0
    assert snap["leads"] == 0
    assert snap["activation_rate"] == 0.0


# ----------------------------------------------------------- approval gate
def _fake_sender(monkeypatch, result):
    from core.services.email_sender import email_sender

    async def fake_send(to_email, subject, body, reply_to=None):
        return dict(result)

    monkeypatch.setattr(email_sender, "send", fake_send)


@pytest.mark.asyncio
async def test_approve_outreach_send_success(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "sent", "to_email": "owner@x.com"})
    ga._enqueue(
        "outreach_send",
        {"to_email": "owner@x.com", "lead_name": "O", "subject": "s", "body": "b"},
    )
    item = ga.pending_actions()[0]
    result = await ga.approve(item["id"])
    assert result["status"] == "approved"
    assert ga._find_action(item["id"])["status"] == "approved"


@pytest.mark.asyncio
async def test_approve_quote_send_records_revenue(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "sent", "to_email": "owner@x.com"})
    ga._enqueue(
        "quote_send",
        {
            "to_email": "owner@x.com",
            "lead_name": "O",
            "subject": "Your Growth workspace is ready",
            "body": "Hi",
            "tier": "growth",
            "checkout_url": "https://checkout.stripe.com/c/x",
        },
    )
    item = ga.pending_actions()[0]
    result = await ga.approve(item["id"])
    assert result["status"] == "approved"
    assert ga.state["revenue"]["quotes_approved"] == 1
    assert ga.state["revenue"]["projected_mrr"] == 99


@pytest.mark.asyncio
async def test_approve_quote_tiers_mrr(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "sent", "to_email": "t@x.com"})
    for tier in ("starter", "growth", "enterprise", "mystery"):
        ga._enqueue(
            "quote_send",
            {
                "to_email": f"{tier}@x.com",
                "subject": "ready",
                "body": "Hi",
                "tier": tier,
                "checkout_url": "https://checkout.stripe.com/c/x",
            },
        )
    for item in ga.pending_actions():
        assert (await ga.approve(item["id"]))["status"] == "approved"
    assert ga.state["revenue"]["quotes_approved"] == 4
    assert ga.state["revenue"]["projected_mrr"] == 29 + 99 + 299 + 99


@pytest.mark.asyncio
async def test_approve_dunning_retry_dispatches(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "sent", "to_email": "late@x.com"})
    ga._enqueue(
        "dunning_retry",
        {"to_email": "late@x.com", "subject": "s", "body": "b", "grace_days": 7},
    )
    item = ga.pending_actions()[0]
    result = await ga.approve(item["id"])
    assert result["status"] == "approved"
    assert ga._find_action(item["id"])["status"] == "approved"
    assert ga.state["revenue"].get("dunning_notices") == 1


@pytest.mark.asyncio
async def test_auto_approve_pending_dispatches_dunning(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "sent", "to_email": "late@x.com"})
    ga._enqueue(
        "dunning_retry",
        {"to_email": "late@x.com", "subject": "s", "body": "b", "grace_days": 7},
    )
    result = await ga._auto_approve_pending()
    assert result["status"] == "ok"
    assert result["approved"] == 1
    assert ga.pending_actions() == []
    assert ga.state["revenue"]["dunning_notices"] == 1


@pytest.mark.asyncio
async def test_approve_not_found(ga):
    result = await ga.approve("DOES-NOT-EXIST")
    assert result == {"status": "not_found"}


@pytest.mark.asyncio
async def test_approve_already_reviewed(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "sent", "to_email": "owner@x.com"})
    ga._enqueue("outreach_send", {"to_email": "owner@x.com", "subject": "s", "body": "b"})
    item = ga.pending_actions()[0]
    await ga.approve(item["id"])
    result = await ga.approve(item["id"])
    assert result["status"] == "already_reviewed"
    assert result["current"] == "approved"


@pytest.mark.asyncio
async def test_approve_unknown_kind(ga):
    ga._enqueue("mystery", {"to_email": "owner@x.com"})
    item = ga.pending_actions()[0]
    result = await ga.approve(item["id"])
    assert result["status"] == "failed"
    assert result["result"] == {"status": "unknown_kind"}


@pytest.mark.asyncio
async def test_approve_failed_send_records_bounce(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "failed", "error": "SMTP 550 5.1.1 recipient address rejected: bounce"})
    ga._enqueue("outreach_send", {"to_email": "bounce@x.com", "subject": "s", "body": "b"})
    item = ga.pending_actions()[0]
    result = await ga.approve(item["id"])
    assert result["status"] == "failed"
    assert deliverability.is_suppressed("bounce@x.com")
    assert deliverability._suppressed["bounce@x.com"]["reason"].startswith("bounce")


@pytest.mark.asyncio
async def test_approve_failed_send_records_complaint(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "failed", "error": "unsubscribe complaint received from recipient"})
    ga._enqueue("outreach_send", {"to_email": "spam@x.com", "subject": "s", "body": "b"})
    item = ga.pending_actions()[0]
    await ga.approve(item["id"])
    assert deliverability.is_suppressed("spam@x.com")
    assert deliverability._suppressed["spam@x.com"]["reason"] == "complaint"


@pytest.mark.asyncio
async def test_approve_failed_send_generic_suppress(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "failed", "error": "smtp connection reset by peer"})
    ga._enqueue("outreach_send", {"to_email": "flaky@x.com", "subject": "s", "body": "b"})
    item = ga.pending_actions()[0]
    await ga.approve(item["id"])
    assert deliverability.is_suppressed("flaky@x.com")
    assert deliverability._suppressed["flaky@x.com"]["reason"].startswith("failed_send:")


# ----------------------------------------------------------------- reject
def test_reject_not_found(ga):
    assert ga.reject("DOES-NOT-EXIST") == {"status": "not_found"}


def test_reject_marks_action_rejected(ga):
    ga._enqueue("outreach_send", {"to_email": "owner@x.com", "subject": "s", "body": "b"})
    item = ga.pending_actions()[0]
    result = ga.reject(item["id"], note="not now")
    assert result == {"status": "rejected"}
    assert ga._find_action(item["id"])["status"] == "rejected"
    assert all(a["id"] != item["id"] for a in ga.pending_actions())


# ------------------------------------------------------------------- purge
def test_purge_not_found(ga):
    assert ga.purge("DOES-NOT-EXIST") == {"status": "not_found"}


def test_purge_all_pending_removes_everything(ga):
    ga._enqueue("outreach_send", {"to_email": "a@x.com", "subject": "s", "body": "b"})
    ga._enqueue("outreach_send", {"to_email": "b@x.com", "subject": "s", "body": "b"})
    ga._enqueue("quote_send", {"to_email": "c@x.com", "subject": "s", "body": "b", "tier": "growth"})
    before = len(ga.pending_actions())
    assert before == 3
    result = ga.purge_all_pending()
    assert result["status"] == "purged"
    assert result["removed"] == before
    assert ga.pending_actions() == []


def test_purge_marks_lead_invalid(tmp_path, monkeypatch, test_db):
    instance = _make_instance(tmp_path, monkeypatch)
    db = test_db()
    try:
        db.add(Lead(email="owner@smithplumbing.com", name="Sam", status="NEW", intent_score=80))
        db.commit()
    finally:
        db.close()

    instance._enqueue(
        "outreach_send",
        {"to_email": "owner@smithplumbing.com", "lead_name": "Sam", "subject": "s", "body": "b"},
    )
    item = instance.pending_actions()[0]
    result = instance.purge(item["id"])
    assert result == {"status": "purged", "email": "owner@smithplumbing.com"}
    assert deliverability.is_suppressed("owner@smithplumbing.com")

    db = test_db()
    try:
        row = db.query(Lead).filter(Lead.email == "owner@smithplumbing.com").first()
        assert row is not None
        assert row.email_invalid is True
        assert row.status == "PURGED"
    finally:
        db.close()


def test_purge_action_without_email(ga):
    ga._enqueue("outreach_send", {"lead_name": "NoEmail"})
    item = ga.pending_actions()[0]
    result = ga.purge(item["id"])
    assert result["status"] == "purged"
    assert result["email"] == ""
    assert ga.pending_actions() == []


# -------------------------------------------------------------- lifecycle
@pytest.mark.asyncio
async def test_start_loop_runs_cycles(ga, monkeypatch):
    calls = []

    async def fake_run_cycle(reason="scheduled"):
        calls.append(reason)
        return {"status": "ok"}

    monkeypatch.setattr(ga, "run_cycle", fake_run_cycle)
    ga.cycle_hours = 0.000001
    await ga.start_loop()
    task = ga._loop_task
    assert task is not None
    await asyncio.sleep(0.03)
    assert calls, "background loop should run at least one cycle"
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_start_loop_survives_cycle_error(ga, monkeypatch):
    calls = []

    async def boom(reason="scheduled"):
        calls.append(reason)
        raise RuntimeError("cycle boom")

    monkeypatch.setattr(ga, "run_cycle", boom)
    ga.cycle_hours = 0.000001
    await ga.start_loop()
    task = ga._loop_task
    await asyncio.sleep(0.03)
    assert len(calls) >= 2, "loop must keep running after a failing cycle"
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_start_loop_disabled(ga):
    ga.enabled = False
    await ga.start_loop()
    assert ga._loop_task is None


@pytest.mark.asyncio
async def test_start_loop_already_running(ga):
    task = asyncio.create_task(asyncio.sleep(10))
    ga._loop_task = task
    await ga.start_loop()
    assert ga._loop_task is task
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_run_now_manual_cycle(ga, monkeypatch):
    monkeypatch.setattr(ga, "_qualified_leads", lambda limit: [])
    result = await ga.run_now()
    assert result["reason"] == "manual"
    assert ga.state["cycle_count"] >= 1


def test_set_enabled(ga):
    ga.set_enabled(False)
    assert ga.enabled is False
    assert ga.state["enabled"] is False
    ga.set_enabled(True)
    assert ga.enabled is True
    assert ga.state["enabled"] is True


def test_status_discovery_exception_paths(ga, monkeypatch):
    from core.services import lead_discovery as ld_mod

    class BoomDiscovery:
        def findings(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(ld_mod, "lead_discovery", BoomDiscovery())
    status = ga.status()
    assert status["discovery"]["findings"] == 0
    assert status["discovery"]["recent"] == []


def test_status_includes_sales_pipeline_and_dunning(ga, monkeypatch):
    ga._enqueue(
        "dunning_retry",
        {"to_email": "late@x.com", "subject": "s", "body": "b", "grace_days": 7},
    )
    status = ga.status()
    assert status["sales_pipeline"] == {
        "open_deals": 0,
        "weighted_pipeline_cents": 0,
        "closed_won_mrr_cents": 0,
    }
    assert status["approval_queue"]["pending_dunning"] == 1


def test_status_sales_pipeline_survives_missing_deals_db(ga, monkeypatch):
    import core.services.sales_pipeline as sp_mod

    class BoomPipeline:
        def pipeline_snapshot(self):
            raise RuntimeError("no deals table")

        def forecast(self):
            raise RuntimeError("no deals table")

    monkeypatch.setattr(sp_mod, "sales_pipeline", BoomPipeline())
    status = ga.status()
    assert status["sales_pipeline"] == {}


# ------------------------------------------------------------ autopilot mode
def test_auto_approve_flag_read_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GROWTH_AUTO_APPROVE", "1")
    instance = GrowthAutomation(state_path=tmp_path / "growth_state.json")
    assert instance.auto_approve is True


def test_set_auto_approve_persists_flag(ga):
    ga.set_auto_approve(True)
    assert ga.auto_approve is True
    assert ga.state["auto_approve"] is True
    ga.set_auto_approve(False)
    assert ga.auto_approve is False


@pytest.mark.asyncio
async def test_auto_approve_pending_outreach_and_quotes(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "sent", "to_email": "owner@x.com"})
    ga._enqueue("outreach_send", {"to_email": "o@x.com", "subject": "s", "body": "b"})
    ga._enqueue("quote_send", {"to_email": "q@x.com", "subject": "s", "body": "b", "tier": "growth"})
    result = await ga._auto_approve_pending()
    assert result["status"] == "ok"
    assert result["approved"] == 2
    assert result["failed"] == 0
    assert ga.pending_actions() == []
    assert ga.state["revenue"]["quotes_approved"] == 1


@pytest.mark.asyncio
async def test_auto_approve_skips_traffic_posts(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "sent", "to_email": "owner@x.com"})
    ga._enqueue("traffic_post", {"network": "x", "text": "Post it"})
    ga._enqueue("outreach_send", {"to_email": "o@x.com", "subject": "s", "body": "b"})
    result = await ga._auto_approve_pending()
    assert result["approved"] == 1
    pending = [a for a in ga.pending_actions() if a["kind"] == "traffic_post"]
    assert pending, "traffic posts must stay behind the founder"



@pytest.mark.asyncio
async def test_auto_approve_unconfigured_smtp_skips(ga, monkeypatch):
    from core.services.email_sender import email_sender

    monkeypatch.setattr(email_sender, "host", "")
    monkeypatch.setattr(email_sender, "user", "")
    monkeypatch.setattr(email_sender, "password", "")
    ga._enqueue("outreach_send", {"to_email": "o@x.com", "subject": "s", "body": "b"})
    result = await ga._auto_approve_pending()
    assert result["status"] == "skipped"
    assert result["reason"].startswith("SMTP")
    assert ga.pending_actions(), "nothing should be dispatched without SMTP"


@pytest.mark.asyncio
async def test_auto_approve_counts_rate_limited(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "rate_limited", "message": "limit hit"})
    ga._enqueue("outreach_send", {"to_email": "o@x.com", "subject": "s", "body": "b"})
    result = await ga._auto_approve_pending()
    assert result["rate_limited"] == 1
    assert ga.pending_actions(), "rate-limited action must stay pending"


@pytest.mark.asyncio
async def test_auto_approve_failed_sends_suppress(ga, monkeypatch):
    _fake_sender(monkeypatch, {"status": "failed", "error": "SMTP 550 5.1.1 bounce"})
    ga._enqueue("outreach_send", {"to_email": "bounce@x.com", "subject": "s", "body": "b"})
    result = await ga._auto_approve_pending()
    assert result["failed"] == 1
    assert deliverability.is_suppressed("bounce@x.com")


@pytest.mark.asyncio
async def test_run_cycle_invokes_auto_approve_when_enabled(tmp_path, monkeypatch):
    instance = _make_instance(tmp_path, monkeypatch)
    instance.auto_approve = True
    monkeypatch.setattr(instance, "_qualified_leads", lambda limit: [])

    async def fake_auto():
        return {"status": "ok", "approved": 0}

    monkeypatch.setattr(instance, "_auto_approve_pending", fake_auto)
    cycle = await instance.run_cycle(reason="test")
    assert cycle["auto_approve"]["status"] == "ok"


@pytest.mark.asyncio
async def test_run_cycle_skips_auto_approve_when_disabled(tmp_path, monkeypatch):
    instance = _make_instance(tmp_path, monkeypatch)
    instance.auto_approve = False
    monkeypatch.setattr(instance, "_qualified_leads", lambda limit: [])
    called = {"count": 0}

    async def _auto(**kwargs):
        called["count"] += 1
        return {"status": "ok"}

    monkeypatch.setattr(instance, "_auto_approve_pending", _auto)
    await instance.run_cycle(reason="test")
    assert called["count"] == 0


# ------------------------------------------------------------- leader lock
@pytest.mark.asyncio
async def test_run_cycle_skipped_when_another_replica_holds_lock(tmp_path, monkeypatch):
    instance = _make_instance(tmp_path, monkeypatch)
    instance.auto_approve = False

    async def hold():
        return "skipped"

    monkeypatch.setattr(instance, "_acquire_leader_lock", hold)
    result = await instance.run_cycle(reason="test")
    assert result["status"] == "skipped"
    assert "another replica" in result["reason"]


@pytest.mark.asyncio
async def test_run_cycle_disabled_returns_early(tmp_path, monkeypatch):
    instance = _make_instance(tmp_path, monkeypatch)
    instance.enabled = False
    result = await instance.run_cycle(reason="test")
    assert result == {"status": "disabled"}


@pytest.mark.asyncio
async def test_leader_lock_acquired_sets_redis_key(monkeypatch):
    monkeypatch.setenv("TEST_MODE", "0")
    import redis.asyncio as redis_module

    class FakeRedis:
        def __init__(self):
            self.value = None
            self.closed = False

        async def set(self, key, value, nx=False, px=None):
            self.value = value
            return True

        async def get(self, key):
            return self.value.encode() if self.value else None

        async def delete(self, key):
            self.value = None

        async def aclose(self):
            self.closed = True

    monkeypatch.setattr(redis_module, "from_url", lambda url, **kw: FakeRedis())
    from core.services.growth_automation import GrowthAutomation

    instance = GrowthAutomation(state_path=None)
    result = await instance._acquire_leader_lock()
    assert result == "acquired"
    assert instance._leader_client is not None


@pytest.mark.asyncio
async def test_leader_lock_skipped_when_key_held(monkeypatch):
    monkeypatch.setenv("TEST_MODE", "0")
    import redis.asyncio as redis_module

    class HeldRedis:
        async def set(self, key, value, nx=False, px=None):
            return False  # someone else owns the lock

        async def get(self, key):
            return b"other-replica"

        async def delete(self, key):
            pass

        async def aclose(self):
            pass

    monkeypatch.setattr(redis_module, "from_url", lambda url, **kw: HeldRedis())
    from core.services.growth_automation import GrowthAutomation

    instance = GrowthAutomation(state_path=None)
    assert await instance._acquire_leader_lock() == "skipped"


@pytest.mark.asyncio
async def test_leader_lock_unavailable_redis_down(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_MODE", "0")
    import redis.asyncio as redis_module

    def boom(url, **kwargs):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(redis_module, "from_url", boom)
    from core.services.growth_automation import GrowthAutomation

    instance = GrowthAutomation(state_path=tmp_path / "growth_state.json")
    assert await instance._acquire_leader_lock() == "unavailable"


@pytest.mark.asyncio
async def test_release_leader_lock_only_when_owner(tmp_path, monkeypatch):
    from core.services.growth_automation import GrowthAutomation

    class FakeRedis:
        def __init__(self):
            self.deleted = False
            self.value = None

        async def set(self, key, value, nx=False, px=None):
            self.value = value
            return True

        async def get(self, key):
            return self.value.encode() if self.value else None

        async def delete(self, key):
            self.deleted = True
            self.value = None

        async def aclose(self):
            pass

    client = FakeRedis()
    instance = GrowthAutomation(state_path=tmp_path / "growth_state.json")
    instance._leader_client = client
    client.value = instance.instance_id
    await instance._release_leader_lock()
    assert client.deleted is True


@pytest.mark.asyncio
async def test_release_leader_lock_not_owner(tmp_path, monkeypatch):
    from core.services.growth_automation import GrowthAutomation

    class FakeRedis:
        def __init__(self):
            self.deleted = False

        async def get(self, key):
            return b"another-replica"

        async def delete(self, key):
            self.deleted = True

        async def aclose(self):
            pass

    client = FakeRedis()
    instance = GrowthAutomation(state_path=tmp_path / "growth_state.json")
    instance._leader_client = client
    await instance._release_leader_lock()
    assert client.deleted is False


def test_instance_id_is_unique():
    from core.services.growth_automation import GrowthAutomation

    a = GrowthAutomation(state_path=None)
    b = GrowthAutomation(state_path=None)
    assert a.instance_id != b.instance_id


# --------------------------------------------------------------- nurture
def _patch_leads(ga, monkeypatch):
    monkeypatch.setattr(
        ga,
        "_qualified_leads",
        lambda limit: [
            {
                "email": "owner@smithplumbing.com",
                "name": "Dave",
                "company": "Smith Plumbing",
                "intent_score": 80,
            }
        ],
    )


@pytest.mark.asyncio
async def test_nurture_phase_scores_leads_and_records(ga, monkeypatch):
    _patch_leads(ga, monkeypatch)
    ga._enqueue(
        "outreach_send",
        {"to_email": "owner@smithplumbing.com", "subject": "s", "body": "b"},
    )
    result = await ga._phase_nurture()
    assert result["status"] == "ok"
    assert result["leads_scored"] >= 1
    records = ga.state["nurture_records"]
    assert any("score" in rec for rec in records.values())
    assert any(rec.get("plan") for rec in records.values())


@pytest.mark.asyncio
async def test_nurture_phase_queues_value_touch_on_day(ga, monkeypatch):
    _patch_leads(ga, monkeypatch)
    ga._enqueue(
        "outreach_send",
        {"to_email": "owner@smithplumbing.com", "subject": "s", "body": "b"},
    )
    await ga._phase_nurture()
    # day-0 intro is the outreach itself -> nothing due yet
    assert ga._pending_count("nurture_touch") == 0
    # age the plan back past the day-2 value touch
    for rec in ga.state["nurture_records"].values():
        if rec.get("plan"):
            rec["plan_started"] = "2024-01-01T00:00:00+00:00"
    result = await ga._phase_nurture()
    assert result["touches_queued"] >= 1
    pending = [
        a
        for a in ga.state["approval_queue"]
        if a["kind"] == "nurture_touch"
        and a["payload"]["to_email"] == "owner@smithplumbing.com"
    ]
    assert pending
    assert pending[0]["payload"]["touch_label"] == "value"
    assert "cadence_note" in pending[0]["payload"]


@pytest.mark.asyncio
async def test_nurture_phase_draft_does_not_repeat_touch(ga, monkeypatch):
    _patch_leads(ga, monkeypatch)
    ga._enqueue(
        "outreach_send",
        {"to_email": "owner@smithplumbing.com", "subject": "s", "body": "b"},
    )
    await ga._phase_nurture()
    for rec in ga.state["nurture_records"].values():
        if rec.get("plan"):
            rec["plan_started"] = "2024-01-01T00:00:00+00:00"
    for _ in range(8):
        await ga._phase_nurture()
    queued = [
        a["payload"]["touch_label"]
        for a in ga.state["approval_queue"]
        if a["kind"] == "nurture_touch"
        and a["payload"]["to_email"] == "owner@smithplumbing.com"
    ]
    # each 5-touch plan drafts each touch label exactly once
    assert queued == ["value", "social_proof", "risk_reversal", "breakup"]
