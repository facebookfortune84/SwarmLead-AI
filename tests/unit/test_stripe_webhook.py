"""
Tests for Stripe webhook route registration and handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    _app = FastAPI()
    from interfaces.api.routers.payments import router

    _app.include_router(router)
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestStripeWebhookRoute:
    """Verify the webhook route exists and validates requests."""

    WEBHOOK_PATH = "/api/stripe/webhook"

    def test_webhook_route_registered(self, client):
        """Webhook endpoint exists in OpenAPI schema."""
        schema = client.get("/openapi.json").json()
        paths = schema.get("paths", {})
        assert self.WEBHOOK_PATH in paths, (
            f"Webhook route {self.WEBHOOK_PATH} not found in OpenAPI schema"
        )

    def test_webhook_missing_signature_returns_400(self, client):
        """Missing stripe-signature header returns 400."""
        response = client.post(
            self.WEBHOOK_PATH,
            json={"type": "invoice.payment_succeeded"},
        )
        assert response.status_code == 400
        assert "signature" in response.text.lower()

    def test_webhook_empty_body_returns_400(self, client):
        """Empty body with valid header returns 400."""
        response = client.post(
            self.WEBHOOK_PATH,
            content=b"",
            headers={"stripe-signature": "t=123,v1=test"},
        )
        assert response.status_code == 400

    @patch("core.services.payment_service.payment_service")
    def test_webhook_successful_processing(self, mock_payment_service, client):
        """Valid webhook returns 200."""
        mock_payment_service.handle_webhook.return_value = {"status": "success"}

        response = client.post(
            self.WEBHOOK_PATH,
            content=b'{"type": "invoice.payment_succeeded"}',
            headers={"stripe-signature": "t=123,v1=test"},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        mock_payment_service.handle_webhook.assert_called_once()

    @patch("core.services.payment_service.payment_service")
    def test_webhook_processing_error_returns_400(self, mock_payment_service, client):
        """Webhook processing failure returns 400."""
        mock_payment_service.handle_webhook.return_value = {
            "status": "error",
            "message": "Invalid signature",
        }

        response = client.post(
            self.WEBHOOK_PATH,
            content=b'{"type": "invoice.payment_succeeded"}',
            headers={"stripe-signature": "t=123,v1=invalid"},
        )
        assert response.status_code == 400

    @patch("core.services.payment_service.payment_service")
    def test_webhook_unexpected_exception_returns_500(self, mock_payment_service, client):
        """Unexpected error returns 500."""
        mock_payment_service.handle_webhook.side_effect = RuntimeError("Unexpected error")

        response = client.post(
            self.WEBHOOK_PATH,
            content=b'{"type": "invoice.payment_succeeded"}',
            headers={"stripe-signature": "t=123,v1=test"},
        )
        assert response.status_code == 500
