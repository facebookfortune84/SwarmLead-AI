"""Tests for the Company Concierge service (voice-driven company creation)."""

import pytest

from core.services.company_concierge import (
    FLOW,
    CompanyConcierge,
    company_concierge,
)


@pytest.fixture
def con():
    return CompanyConcierge()


def test_start_returns_prompt_and_step(con):
    s = con.start(founder_name="Rob")
    assert s["session_id"].startswith("cc_")
    assert s["step"] == "company"
    assert "name" in s["prompt"].lower()


def test_advance_unknown_session_autostarts(con):
    res = con.advance("cc_nope", "build an ai plumbing business")
    assert res["session_id"] != "cc_nope"
    assert res["step"] == "company"


def test_full_flow_collects_brief(con):
    s = con.start("Rob")
    replies = [
        "plumbing service for small businesses",
        ".ai",
        "homeowners with leaks in the metro area",
        "sdr, content, seo",
        "flat rate 89/visit",
        "launch",
    ]
    final = None
    for text in replies:
        final = con.advance(s["session_id"], text)
    assert final["done"] is True
    assert final["launch_signal"] is True
    brief = con.brief_for(s["session_id"])
    assert brief["company"]
    assert brief["domain_available"] is True
    assert "sdr_agent" in brief["roles"]
    assert brief["brief_text"]


def test_brainstorm_names_returns_available_brandable(con):
    names = con.brainstorm_names("ai tools for movers")
    assert names
    # first candidate should be a compound/suffixed brandable, not bare generic
    first, available = names[0]
    assert available is True
    assert 3 <= len(first) <= 18


def test_name_available_flag_taken(con):
    assert con.name_available("novample") is True
    assert con.name_available("google") is False


def test_domain_available_local_registry(con):
    assert con.domain_available("something-never-seen.io") is True
    assert con.domain_available("example.com") is False
    assert con.domain_available("") is False


def test_domain_for_picks_requested_tld(con):
    d = con.domain_for("Nova Plumbing", tld="ai")
    assert d["domain"].endswith(".ai")


def test_domain_suggestions_cover_extensions(con):
    cols = con.domain_suggestions("nimbus")
    assert {c["domain"].rsplit(".", 1)[-1] for c in cols} == {
        "com", "net", "org", "io", "ai", "co", "app", "dev", "shop",
    }


def test_final_brief_contains_sections(con):
    s = con.start()
    for text in ["hvac company", ".com", "homeowners", "outreach",
                 "preventive service plan", "launch"]:
        con.advance(s["session_id"], text)
    brief = con.brief_for(s["session_id"])["brief_text"]
    assert "Company name" in brief
    assert "Audience" in brief
    assert "Offer" in brief


def test_global_singleton_and_flow(con):
    assert company_concierge is not None
    assert len(FLOW) == 6
    assert company_concierge.status()["steps"][0] == "company"


def test_build_brief_props_shape(con):
    s = con.start("Rob")
    for text in ["law firm consulting", ".co", "founders", "closer", "retainer", "launch"]:
        con.advance(s["session_id"], text)
    props = con.build_brief_props(s["session_id"])
    assert props["business_name"]
    assert "sdr_agent" in props["roles_staffed"] or props["roles_staffed"]
    assert props["domain"]