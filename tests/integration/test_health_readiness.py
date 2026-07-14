"""
Integration Test
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient


def build_app():

    app = FastAPI()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready():
        return {"status": "ready"}

    return app


def test_health():

    client = TestClient(build_app())

    assert client.get("/health").status_code == 200


def test_ready():

    client = TestClient(build_app())

    assert client.get("/ready").status_code == 200
