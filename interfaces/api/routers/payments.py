"""
Stripe checkout session API.

This module exposes endpoints for creating Stripe Checkout sessions.
It supports both predefined price IDs and dynamic product/price creation.
"""

import logging
import os
from types import ModuleType

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from core.site import site_url

# Lazy import to avoid hard dependency at import time
stripe: ModuleType | None = None
try:
    import stripe as _stripe

    stripe = _stripe
except Exception:  # pylint: disable=broad-except
    stripe = None

router = APIRouter(prefix="/api/stripe", tags=["Stripe"])
logger = logging.getLogger("StripeAPI")

# Configure Stripe API key if available
# Use setattr to avoid static-analysis errors when the stripe module
# may not expose api_key at type-check time.
if stripe is not None:
    setattr(stripe, "api_key", os.getenv("STRIPE_API_KEY"))


class CheckoutCreate(BaseModel):
    """Payload for creating a Stripe checkout session."""

    product_name: str | None = None
    amount_cents: int | None = None
    price_id: str | None = None
    billing: str = "monthly"  # "monthly" | "annual" (annual = 2 months free)


@router.post("/create-checkout-session")
async def create_checkout_session(payload: CheckoutCreate):
    """
    Create a Stripe Checkout session.

    Args:
        payload (CheckoutCreate): Product or price information.

    Raises:
        HTTPException: If Stripe is unavailable or request is invalid.

    Returns:
        dict: Checkout session URL and ID.
    """
    if stripe is None:
        raise HTTPException(
            status_code=500,
            detail="Stripe library not available",
        )

    try:
        frontend_url = site_url()
        success_url = f"{frontend_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{frontend_url}/cancel"

        annual = payload.billing == "annual"

        # Use existing price ID if provided
        if payload.price_id:
            price_id = payload.price_id
        else:
            # Validate dynamic product creation
            if not payload.product_name or not payload.amount_cents:
                raise HTTPException(
                    status_code=400,
                    detail=("Either price_id or (product_name and amount_cents) is required"),
                )

            product = stripe.Product.create(name=payload.product_name)
            price = stripe.Price.create(
                product=product.id,
                # Annual = 10x monthly (2 months free). Exact USD math so the
                # pricing page and Stripe always agree.
                unit_amount=(
                    payload.amount_cents * 10 if annual else payload.amount_cents
                ),
                currency="usd",
                recurring={
                    "interval": "year" if annual else "month",
                },
            )
            price_id = price.id

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return {"url": session.url, "id": session.id}

    except HTTPException:
        raise

    except stripe.error.StripeError as exc:
        logger.exception("Stripe API error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected error creating checkout session: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.

    Expects:
        - Raw JSON body from Stripe
        - `stripe-signature` header

    Processes:
        - invoice.payment_succeeded
        - invoice.payment_failed
        - customer.subscription.deleted
    """
    from core.services.payment_service import payment_service

    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(
            status_code=400,
            detail="Missing stripe-signature header",
        )

    payload = await request.body()
    if not payload:
        raise HTTPException(
            status_code=400,
            detail="Empty request body",
        )

    try:
        result = payment_service.handle_webhook(payload, sig_header)
        if result["status"] == "error":
            logger.error("Webhook processing error: %s", result.get("message"))
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Webhook processing failed"),
            )
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected webhook error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
