"""Unit tests for the launch-ext router (interfaces.api.routers.launch_ext):
company concierge, outreach maximization, and nurture engine endpoints."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from interfaces.api.routers.launch_ext import router


def _client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_concierge_start_returns_prompt():
    client = _client()
    response = client.post("/api/launch/concierge/start", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"]
    assert body["step"] == "company"
    assert body["done"] is False
    assert body["prompt"]


def test_concierge_message_advances_through_flow():
    client = _client()
    started = client.post(
        "/api/launch/concierge/start", json={"founder_name": "Sandra"}
    ).json()
    sid = started["session_id"]

    turns = [
        "A mobile dog-grooming business for city residents",
        ".io",
        "busy pet owners in the city",
        "sdr, outreach, content, seo",
        "premium flat-rate, $499/mo",
        "launch",
    ]
    step_before = "company"
    final = None
    for text in turns:
        response = client.post(
            "/api/launch/concierge/message", json={"session_id": sid, "text": text}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["session_id"] == sid
        assert body["step"] != step_before or body["done"]
        step_before = body["step"]
        final = body
    assert final["done"] is True
    assert final["launch_signal"] is True
    assert final["brief"]
    assert "dog" in final["brief"].lower()


def test_concierge_get_brief():
    client = _client()
    session = client.post("/api/launch/concierge/start", json={}).json()
    sid = session["session_id"]
    client.post(
        "/api/launch/concierge/message",
        json={"session_id": sid, "text": "AI tax advisory for freelancers"},
    )
    response = client.get(f"/api/launch/concierge/{sid}")
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["brief"]["company"]


def test_concierge_status_endpoint_not_masked_by_session_id():
    client = _client()
    response = client.get("/api/launch/concierge/status")
    assert response.status_code == 200
    body = response.json()
    assert "sessions" in body
    assert "steps" in body


def test_concierge_end_session():
    client = _client()
    session = client.post("/api/launch/concierge/start", json={}).json()
    sid = session["session_id"]
    response = client.post(f"/api/launch/concierge/{sid}/end")
    assert response.status_code == 200
    assert response.json()["ended"] is True


def test_maximize_scores_lead_and_returns_levers():
    client = _client()
    response = client.post(
        "/api/launch/maximize",
        json={"email": "owner@smithplumbing.com", "name": "Dave", "company": "Smith Plumbing"},
    )
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["score"] <= 100
    assert body["band"] in {"ideal", "solid", "warm", "cool"}
    assert "suggested_subject" in body
    assert "suggested_hook" in body
    assert "ready" in body


def test_maximize_levers_catalog():
    client = _client()
    response = client.get("/api/launch/maximize/levers")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 10
    assert len(body["levers"]) == body["total"]


def test_nurture_plan_returns_five_touches():
    client = _client()
    response = client.post(
        "/api/launch/nurture/plan", json={"email": "owner@smithplumbing.com"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert len(body["touches"]) == 5
    assert body["touches"][0]["label"] == "intro"


def test_nurture_classify_escalates_hot_reply():
    client = _client()
    response = client.post(
        "/api/launch/nurture/classify", json={"reply": "Yes, schedule a demo"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "escalate_to_closer"


def test_nurture_status():
    client = _client()
    response = client.get("/api/launch/nurture/status")
    assert response.status_code == 200
    body = response.json()
    assert body["touches"] == 5