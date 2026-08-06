"""Unit tests for the new CLI commands (cli.py sales / revenue / seo)."""

import pytest

import cli


@pytest.fixture(autouse=True)
def isolate_sales_pipeline(tmp_path, monkeypatch):
    """Route the sales-pipeline DB into a temp file for deterministic CLI runs."""
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    import core.models  # noqa: F401
    from core.persistence.base import Base

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'cli.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)
    return tmp_path


def test_cmd_sales_prints_board(tmp_path, capsys):
    assert cli.cmd_sales(type("A", (), {"deals": None})()) == 0
    out = capsys.readouterr().out
    assert "AI Sales Pipeline" in out
    assert "Weighted pipeline" in out
    assert "Closed-won MRR" in out


def test_cmd_sales_lists_deals(tmp_path, capsys):
    from core.services.sales_pipeline import sales_pipeline

    sales_pipeline.create_deal(
        {"id": "L1", "email": "a@b.com", "intent_score": 92}
    )
    assert cli.cmd_sales(type("S", (), {"deals": "qualified"})()) == 0
    out = capsys.readouterr().out
    assert "a@b.com" in out


def test_cmd_revenue_prints_dashboard(tmp_path, capsys):
    assert cli.cmd_revenue(type("S", (), {})()) == 0
    out = capsys.readouterr().out
    assert "Revenue Dashboard" in out
    assert "Monthly recurring" in out
    assert "Tier mix" in out


def test_cmd_seo_prints_assets(tmp_path, capsys):
    assert cli.cmd_seo(type("S", (), {})()) == 0
    out = capsys.readouterr().out
    assert "SEO Assets" in out
    assert "URL inventory" in out
    assert "robots.txt" in out

def test_main_help():
    assert cli.make_arg_parser().prog == "genesis"