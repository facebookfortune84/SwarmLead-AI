# Stripe Production Readiness

**Date:** 2026-07-26

---

## Current Integration

| Component | File | Status |
|---|---|---|
| Checkout Session API | `interfaces/api/routers/payments.py` | ✅ `POST /api/stripe/create-checkout-session` |
| Payment Service | `core/services/payment_service.py` | ✅ Full subscription CRUD |
| Webhook Handler | `core/services/payment_service.py:152` | ✅ Method exists but **NO route registered** |
| Stripe API Key | `.env:21` | `sk_live_*` — LIVE key (was in dev .env) |

## Checkout Flow

1. User visits `/billing`
2. Frontend calls `POST /api/stripe/create-checkout-session`
3. Backend creates Stripe CheckoutSession with `mode="subscription"`
4. User redirected to Stripe hosted checkout
5. Success → `{FRONTEND_URL}/success?session_id={CHECKOUT_SESSION_ID}`
6. Cancel → `{FRONTEND_URL}/cancel`

## Products Required in Stripe Dashboard

| # | Product | Type | Price ID | Notes |
|---|---|---|---|---|
| 1 | "SwarmOS Hosting" | Recurring (monthly) | `price_hosting_monthly` (or create new) | This is the default expected by `payment_service.py:30` |

### Steps to create in Stripe Dashboard

1. Log into Stripe Dashboard → Products → Add Product
2. Name: `SwarmOS Hosting`
3. Description: `Monthly hosting subscription for SwarmOS tenant`
4. Pricing model: Standard pricing
5. Price: Set your monthly rate (e.g., $29.00/month)
6. Click "Save"
7. Copy the Price ID (starts with `price_`)
8. Set as `STRIPE_HOSTING_PRICE_ID` in production environment

## Webhook Configuration

**Not currently registered in the API.** The code (`payment_service.py:152`) supports:
- `invoice.payment_succeeded` — log payment, grant access
- `invoice.payment_failed` — log failure, notify user
- `customer.subscription.deleted` — clean up tenant resources

### To register webhooks:

1. In Stripe Dashboard → Developers → Webhooks → Add endpoint
2. Endpoint URL: `https://api.realms2riches.com/api/stripe/webhook` (or comparable)
3. Events to send:
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`
4. Copy signing secret (`whsec_*`) → set as `STRIPE_WEBHOOK_SECRET`
5. A FastAPI route needs to be added to `main.py`:
   ```python
   from core.services.payment_service import payment_service
   
   @app.post("/api/stripe/webhook")
   async def stripe_webhook(request: Request):
       payload = await request.body()
       sig_header = request.headers.get("stripe-signature")
       return payment_service.handle_webhook(payload, sig_header)
   ```

## Customer Portal

Not configured. Post-launch enhancement to allow users to manage their own subscriptions.

## Verification Checklist

- [ ] Product created in Stripe Dashboard
- [ ] Price ID set as `STRIPE_HOSTING_PRICE_ID` in production env
- [ ] `STRIPE_API_KEY` set to live key (verify starts with `sk_live_`)
- [ ] Webhook endpoint registered in Stripe Dashboard
- [ ] `STRIPE_WEBHOOK_SECRET` set in production env
- [ ] `FRONTEND_URL` set correctly for success/cancel redirects
- [ ] Test checkout in test mode before going live
