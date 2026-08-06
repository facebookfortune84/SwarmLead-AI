"""Sales team <-> growth loop integration tests."""

import pytest
import pytest_asyncio

from core.services.growth_automation import GrowthAutomation


def _deal(lead_id="L1", email="owner@smithplumbing.com", intent="high"):
    return {
        "id": lead_id,
        "email": email,
        "name": "Sam Smith",
        "company": "Smith Plumbing",
        "intent_score": 80 if intent == "high" else 5,
        "metadata": {"source": "search_website"},
    }


@pytest_asyncio.fixture
async def growth(tmp_path, monkeypatch):
    from core.services import growth_automation as _mod

    async def fast_generate(self, prompt, template):
        return f"# {template.name}\n\n[test scaffold]"

    from core.agents.content.content_agent import ContentAgent

    monkeypatch.setattr(ContentAgent, "_generate", fast_generate)
    monkeypatch.setenv("GROWTH_DISCOVERY", "0")

    def realistic_leads(self, limit):
        return [_deal()]

    monkeypatch.setattr(_mod.GrowthAutomation, "_qualified_leads", realistic_leads)

    from core.services.deliverability import deliverability

    deliverability.suppression_path = tmp_path / "suppression.json"
    deliverability._suppressed = {}

    old = _mod.STATE_PATH
    _mod.STATE_PATH = tmp_path / "growth_state.json"
    instance = GrowthAutomation(state_path=tmp_path / "growth_state.json")
    instance.enabled = True
    yield instance
    _mod.STATE_PATH = old
    from core.services.deliverability import SUPPRESSION_PATH as _def_supp

    deliverability.suppression_path = _def_supp
    deliverability._suppressed = {}


@pytest.mark.asyncio
async def test_discovery_runs_sdr_qualification(tmp_path, monkeypatch, growth):
    from core.services.lead_discovery import DiscoveredLead

    async def fake_discover(self, max_targets=6):
        return [
            DiscoveredLead(
                email="a@bcorp.com",
                name="Ada",
                company="B Corp",
                vertical="Legal",
                intent_score=95,
            ),
            DiscoveredLead(
                email="cold@x.com",
                company="Cold Co",
                vertical="Legal",
                intent_score=5,
            ),
        ]

    monkeypatch.setenv("GROWTH_DISCOVERY", "1")
    monkeypatch.setattr(
        "core.services.lead_discovery.LeadDiscoveryEngine.discover", fake_discover
    )

    import sqlalchemy
    import sqlalchemy.orm as orm

    import core.models  # noqa: F401
    from core.persistence.base import Base

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'sales.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = orm.sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)

    result = await growth._phase_discovery()

    assert result["discovered"] == 2
    assert result["written"] == 2
    assert result["deals_created"] == 1  # only the 95-intent lead qualifies


@pytest.mark.asyncio
async def test_mark_deal_quoted_advances_engaged(tmp_path, monkeypatch, growth):
    import sqlalchemy
    import sqlalchemy.orm as orm

    import core.models  # noqa: F401
    from core.persistence.base import Base

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'sales2.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = orm.sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)

    from core.services.sales_pipeline import sales_pipeline

    deal = sales_pipeline.create_deal(_deal(lead_id="LD", email="owner@smithplumbing.com"))
    sales_pipeline.advance(deal["id"], "engaged", triggered_by="closer_agent")

    growth._mark_deal_quoted("owner@smithplumbing.com", tier="growth")

    refreshed = sales_pipeline.get_deal(deal["id"])
    assert refreshed["stage"] == "quoted"
    assert "closer_agent" in refreshed["notes"]


@pytest.mark.asyncio
async def test_mark_deal_quoted_missing_email_noop(tmp_path, monkeypatch, growth):
    import sqlalchemy
    import sqlalchemy.orm as orm

    import core.models  # noqa: F401
    from core.persistence.base import Base

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'sales3.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = orm.sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)

    growth._mark_deal_quoted("nobody@nowhere.com", tier="starter")
    assert growth.state is not None  # no exception, no-op