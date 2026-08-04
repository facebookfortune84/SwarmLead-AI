"""Extra unit tests for PaymentService.

Covers Stripe checkout session creation, hosting subscriptions, cancellations,
and webhook handling. The Stripe SDK, AgentIdentityRegistry and env vars are
mocked — no real network / Stripe / DB access.
"""

import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from core.auth.agent_identity import AgentDomain, AgentIdentity, AgentIdentityRegistry
from core.services.payment_service import PaymentService


# --------------------------------------------------------------------------- #
# helpers / fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def service():
    return PaymentService()


@pytest.fixture
def mock_stripe():
    with patch("core.services.payment_service.stripe") as m:
        yield m


def _customer(customer_id="cus_123"):
    return SimpleNamespace(id=customer_id)


def _subscription(sub_id="sub_123", items_data=True, unit_amount=1999):
    if items_data:
        item = SimpleNamespace(price=SimpleNamespace(unit_amount=unit_amount))
        items = SimpleNamespace(data=[item])
    else:
        items = SimpleNamespace(data=[])
    return SimpleNamespace(id=sub_id, items=items)


def _non_financial_identity():
    return AgentIdentity(
        agent_id="strategy_agent",
        agent_type="StrategyAgent",
        display_name="Strategy Agent",
        domains={AgentDomain.PRODUCT_CODE},
    )


# --------------------------------------------------------------------------- #
# get_price_id
# --------------------------------------------------------------------------- #
def test_get_price_id_known_plan_returns_value(service):
    service.plans = {"starter": "price_123"}
    assert service.get_price_id("starter") == "price_123"


def test_get_price_id_unknown_plan_returns_none(service):
    service.plans = {"starter": "price_123"}
    assert service.get_price_id("nonexistent") is None


def test_get_price_id_empty_price_value_returns_none(service):
    service.plans = {"starter": ""}
    assert service.get_price_id("starter") is None


# --------------------------------------------------------------------------- #
# create_hosting_subscription
# --------------------------------------------------------------------------- #
def test_create_hosting_subscription_uses_existing_customer(service, mock_stripe):
    mock_stripe.Customer.list.return_value.data = [_customer("cus_existing")]
    mock_stripe.Subscription.create.return_value = _subscription()

    result = service.create_hosting_subscription(
        customer_email="a@b.com", project_id="proj_1"
    )

    assert result == {"status": "success", "subscription_id": "sub_123"}
    mock_stripe.Customer.list.assert_called_once_with(email="a@b.com", limit=1)
    mock_stripe.Customer.create.assert_not_called()
    mock_stripe.Subscription.create.assert_called_once_with(
        customer="cus_existing",
        items=[{"price": service.hosting_price_id}],
        metadata={"project_id": "proj_1", "type": "hosting", "rail": "stripe_card"},
    )


def test_create_hosting_subscription_creates_new_customer(service, mock_stripe):
    mock_stripe.Customer.list.return_value.data = []
    mock_stripe.Customer.create.return_value = _customer("cus_new")
    mock_stripe.Subscription.create.return_value = _subscription()

    result = service.create_hosting_subscription(
        customer_email="new@b.com", project_id="proj_2"
    )

    assert result["status"] == "success"
    mock_stripe.Customer.create.assert_called_once_with(
        email="new@b.com", metadata={"project_id": "proj_2"}
    )
    mock_stripe.Subscription.create.assert_called_once()


def test_create_hosting_subscription_with_financial_agent_passes(service, mock_stripe):
    mock_stripe.Customer.list.return_value.data = [_customer()]
    mock_stripe.Subscription.create.return_value = _subscription()
    identity = Mock()
    identity.has_domain.return_value = True
    with patch.object(AgentIdentityRegistry, "get", return_value=identity):
        result = service.create_hosting_subscription(
            customer_email="a@b.com", project_id="proj_3", agent_id="payment_agent"
        )

    assert result["status"] == "success"
    identity.has_domain.assert_called_once_with("financial")
    mock_stripe.Subscription.create.assert_called_once()


def test_create_hosting_subscription_missing_identity_denied(service, mock_stripe):
    mock_stripe.Customer.list.return_value.data = [_customer()]
    with patch.object(AgentIdentityRegistry, "get", return_value=None):
        result = service.create_hosting_subscription(
            customer_email="a@b.com", project_id="proj_4", agent_id="ghost"
        )

    assert result == {"status": "error", "message": "Agent lacks financial authority"}
    mock_stripe.Subscription.create.assert_not_called()


def test_create_hosting_subscription_non_financial_agent_denied(service, mock_stripe):
    mock_stripe.Customer.list.return_value.data = [_customer()]
    with patch.object(
        AgentIdentityRegistry, "get", return_value=_non_financial_identity()
    ):
        result = service.create_hosting_subscription(
            customer_email="a@b.com", project_id="proj_5", agent_id="strategy_agent"
        )

    assert result == {"status": "error", "message": "Agent lacks financial authority"}
    mock_stripe.Subscription.create.assert_not_called()


def test_create_hosting_subscription_audits_amount_from_price(service, mock_stripe):
    mock_stripe.Customer.list.return_value.data = [_customer()]
    mock_stripe.Subscription.create.return_value = _subscription(unit_amount=2000)

    with patch.object(service, "_audit_log") as audit:
        service.create_hosting_subscription("a@b.com", "proj_6")

    audit.assert_called_once()
    details = audit.call_args[0][2]
    assert details["amount_usd"] == 20.0
    assert details["subscription_id"] == "sub_123"
    assert details["rail"] == "stripe_card"


def test_create_hosting_subscription_no_items_amount_zero(service, mock_stripe):
    mock_stripe.Customer.list.return_value.data = [_customer()]
    mock_stripe.Subscription.create.return_value = _subscription(items_data=False)

    with patch.object(service, "_audit_log") as audit:
        result = service.create_hosting_subscription("a@b.com", "proj_7")

    assert result["status"] == "success"
    details = audit.call_args[0][2]
    assert details["amount_usd"] == 0


def test_create_hosting_subscription_stripe_error(service, mock_stripe):
    mock_stripe.Customer.list.return_value.data = [_customer()]
    mock_stripe.Subscription.create.side_effect = Exception("card declined")

    result = service.create_hosting_subscription("a@b.com", "proj_8")

    assert result["status"] == "error"
    assert "card declined" in result["message"]


# --------------------------------------------------------------------------- #
# cancel_hosting
# --------------------------------------------------------------------------- #
def test_cancel_hosting_finds_and_deletes_subscription(service, mock_stripe):
    sub = SimpleNamespace(id="sub_a", metadata={"project_id": "proj_x"})
    other = SimpleNamespace(id="sub_b", metadata={"project_id": "proj_y"})
    mock_stripe.Subscription.list.return_value.data = [sub, other]
    mock_stripe.Subscription.delete.return_value = SimpleNamespace(canceled_at=1700000000)

    result = service.cancel_hosting("proj_x")

    assert result == {
        "status": "success",
        "subscription_id": "sub_a",
        "canceled_at": 1700000000,
    }
    mock_stripe.Subscription.delete.assert_called_once_with("sub_a")
    mock_stripe.Subscription.list.assert_called_once_with(limit=100)


def test_cancel_hosting_no_matching_subscription(service, mock_stripe):
    sub = SimpleNamespace(id="sub_a", metadata={"project_id": "proj_other"})
    mock_stripe.Subscription.list.return_value.data = [sub]

    result = service.cancel_hosting("proj_missing")

    assert result == {"status": "not_found", "message": "No subscription found"}
    mock_stripe.Subscription.delete.assert_not_called()


def test_cancel_hosting_empty_list(service, mock_stripe):
    mock_stripe.Subscription.list.return_value.data = []

    result = service.cancel_hosting("proj_x")

    assert result == {"status": "not_found", "message": "No subscription found"}


def test_cancel_hosting_stripe_error(service, mock_stripe):
    mock_stripe.Subscription.list.side_effect = Exception("api down")

    result = service.cancel_hosting("proj_x")

    assert result["status"] == "error"
    assert "api down" in result["message"]


# --------------------------------------------------------------------------- #
# create_checkout_session
# --------------------------------------------------------------------------- #
def test_create_checkout_session_success_default_urls(service, mock_stripe, monkeypatch):
    monkeypatch.setenv("FRONTEND_URL", "https://app.example.test")
    session = SimpleNamespace(id="cs_123", url="https://checkout.stripe.com/c/pay/123")
    mock_stripe.checkout.Session.create.return_value = session

    result = service.create_checkout_session(
        customer_email="a@b.com",
        project_id="proj_1",
        price_id="price_123",
    )

    assert result == {"status": "success", "session_id": "cs_123", "url": session.url}
    kwargs = mock_stripe.checkout.Session.create.call_args.kwargs
    assert kwargs["success_url"] == (
        "https://app.example.test/success?session_id={CHECKOUT_SESSION_ID}"
    )
    assert kwargs["cancel_url"] == "https://app.example.test/cancel"
    assert kwargs["mode"] == "subscription"
    assert kwargs["metadata"] == {"project_id": "proj_1", "rail": "stripe_card"}


def test_create_checkout_session_custom_urls_and_mode(service, mock_stripe):
    session = SimpleNamespace(id="cs_456", url="https://checkout/pay/456")
    mock_stripe.checkout.Session.create.return_value = session

    result = service.create_checkout_session(
        customer_email="a@b.com",
        project_id="proj_2",
        price_id="price_456",
        success_url="https://custom/success",
        cancel_url="https://custom/cancel",
        mode="payment",
    )

    assert result["status"] == "success"
    kwargs = mock_stripe.checkout.Session.create.call_args.kwargs
    assert kwargs["success_url"] == "https://custom/success"
    assert kwargs["cancel_url"] == "https://custom/cancel"
    assert kwargs["mode"] == "payment"


def test_create_checkout_session_stripe_error(service, mock_stripe):
    mock_stripe.checkout.Session.create.side_effect = Exception("checkout failed")

    result = service.create_checkout_session("a@b.com", "proj_3", "price_123")

    assert result["status"] == "error"
    assert "checkout failed" in result["message"]


# --------------------------------------------------------------------------- #
# handle_webhook
# --------------------------------------------------------------------------- #
def test_handle_webhook_payment_succeeded(service, mock_stripe):
    event = {
        "type": "invoice.payment_succeeded",
        "data": {"object": {"id": "in_1", "customer": "cus_1", "amount_paid": 2500}},
    }
    mock_stripe.Webhook.construct_event.return_value = event

    with patch.object(service, "_handle_payment_succeeded") as handler:
        result = service.handle_webhook(b"payload", "sig_header")

    assert result == {"status": "success"}
    handler.assert_called_once_with(event["data"]["object"])
    mock_stripe.Webhook.construct_event.assert_called_once_with(
        b"payload", "sig_header", os.getenv("STRIPE_WEBHOOK_SECRET")
    )


def test_handle_webhook_payment_failed(service, mock_stripe):
    event = {"type": "invoice.payment_failed", "data": {"object": {"id": "in_2"}}}
    mock_stripe.Webhook.construct_event.return_value = event

    with patch.object(service, "_handle_payment_failed") as handler:
        result = service.handle_webhook(b"payload", "sig_header")

    assert result == {"status": "success"}
    handler.assert_called_once_with(event["data"]["object"])


def test_handle_webhook_subscription_deleted(service, mock_stripe):
    event = {
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": "sub_1"}},
    }
    mock_stripe.Webhook.construct_event.return_value = event

    with patch.object(service, "_handle_subscription_canceled") as handler:
        result = service.handle_webhook(b"payload", "sig_header")

    assert result == {"status": "success"}
    handler.assert_called_once_with(event["data"]["object"])


def test_handle_webhook_unknown_event_ignored(service, mock_stripe):
    event = {"type": "charge.succeeded", "data": {"object": {}}}
    mock_stripe.Webhook.construct_event.return_value = event

    with (
        patch.object(service, "_handle_payment_succeeded") as ps,
        patch.object(service, "_handle_payment_failed") as pf,
        patch.object(service, "_handle_subscription_canceled") as sc,
    ):
        result = service.handle_webhook(b"payload", "sig_header")

    assert result == {"status": "success"}
    ps.assert_not_called()
    pf.assert_not_called()
    sc.assert_not_called()


def test_handle_webhook_invalid_signature(service, mock_stripe):
    mock_stripe.Webhook.construct_event.side_effect = Exception("Invalid signature")

    result = service.handle_webhook(b"payload", "bad_sig")

    assert result["status"] == "error"
    assert "Invalid signature" in result["message"]


def test_handle_webhook_missing_secret_passes_none(service, mock_stripe, monkeypatch):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    event = {"type": "invoice.payment_succeeded", "data": {"object": {}}}
    mock_stripe.Webhook.construct_event.return_value = event

    with patch.object(service, "_handle_payment_succeeded"):
        result = service.handle_webhook(b"payload", "sig")

    assert result == {"status": "success"}
    _, _, secret = mock_stripe.Webhook.construct_event.call_args[0]
    assert secret is None


# --------------------------------------------------------------------------- #
# private handlers / audit
# --------------------------------------------------------------------------- #
def test_handle_payment_succeeded_audits_amount(service):
    invoice = {"id": "in_1", "customer": "cus_1", "amount_paid": 2500}

    with patch.object(service, "_audit_log") as audit:
        service._handle_payment_succeeded(invoice)

    audit.assert_called_once()
    action, event_type, details = audit.call_args[0]
    assert action == "payment_succeeded"
    assert event_type == "stripe_payment"
    assert details["amount_usd"] == 25.0
    assert details["invoice_id"] == "in_1"


def test_handle_payment_succeeded_missing_amount(service):
    with patch.object(service, "_audit_log") as audit:
        service._handle_payment_succeeded({"id": "in_2", "customer": "cus_2"})

    details = audit.call_args[0][2]
    assert details["amount_usd"] == 0


def test_handle_payment_failed_audits(service):
    with patch.object(service, "_audit_log") as audit:
        service._handle_payment_failed({"id": "in_9", "customer": "cus_9"})

    action, event_type, details = audit.call_args[0]
    assert action == "payment_failed"
    assert event_type == "stripe_payment"
    assert details["invoice_id"] == "in_9"


def test_handle_subscription_canceled_audits(service):
    with patch.object(service, "_audit_log") as audit:
        service._handle_subscription_canceled({"id": "sub_9", "customer": "cus_9"})

    action, event_type, details = audit.call_args[0]
    assert action == "subscription_canceled"
    assert event_type == "stripe_subscription"
    assert details["subscription_id"] == "sub_9"


def test_audit_log_returns_none(service):
    assert service._audit_log("test_action", "test_event", {"k": "v"}) is None
