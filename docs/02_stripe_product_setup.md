# Genesis — Stripe Product Setup Reference
*Companion to Section 9 of the Genesis Charter. Use this to create the actual Products/Prices in the Stripe Dashboard or via API.*

---

## Important architectural note before you start

Stripe Products/Prices (standard Billing) work directly for Layers 1-4 below. **Layer 5 (Revenue Share) is architecturally different** — it's a percentage of a *third party's* (the created company's) revenue, not a charge on your own customer. That requires **Stripe Connect**, not a standard Product. Don't try to model revenue share as a normal recurring Price — it won't work. See the note at the bottom.

---

## Products to create in Stripe (standard Billing)

### 1. Genesis Cloud — Starter
- **Product name:** `Genesis Cloud — Starter`
- **Description:** Hosted Genesis orchestration, entry tier
- **Price:** $39.00 USD, recurring monthly
- **Metadata suggestion:** `tier: starter`, `included_hours: 50`

### 2. Genesis Cloud — Builder
- **Product name:** `Genesis Cloud — Builder`
- **Description:** Hosted Genesis orchestration, priority build queue, real-launch eligible
- **Price:** $149.00 USD, recurring monthly
- **Metadata suggestion:** `tier: builder`, `included_hours: 250`

### 3. Genesis Cloud — Scale
- **Product name:** `Genesis Cloud — Scale`
- **Description:** Hosted Genesis orchestration, dedicated review-queue priority, multi-project
- **Price:** $499.00 USD, recurring monthly
- **Metadata suggestion:** `tier: scale`, `included_hours: 1000`

*(Optional: add annual variants of each at a ~15-20% discount — matches the 2026 norm of offering annual discounts to reduce churn, referenced in the pricing research.)*

### 4. Agent Compute Overage
- **Product name:** `Agent Compute Hour (Overage)`
- **Price type:** **Metered** usage-based price, not standard recurring
- **Unit:** 1 agent-compute-hour
- **Price:** $1.50 USD per unit
- **Billing scheme:** `per_unit`, `usage_type: metered`, `aggregate_usage: sum`
- **Setup note:** attach this Price to the same Subscription as whichever tier the customer is on (Stripe supports multiple Prices per Subscription). Report usage via `usage_records` as agent-compute-hours are consumed beyond the plan's included allowance.

### 5. Real-Launch Facilitation Fee
- **Product name:** `Real-Launch Facilitation Fee`
- **Price type:** **One-time** (not recurring)
- **Price:** $299.00 USD
- **Trigger point in your app:** fire this charge (via a one-off Invoice Item or PaymentIntent using this Price) exactly when a project crosses into the §5.1 real-launch step — this should be a discrete, code-triggered event in your orchestration logic, not something the customer manually purchases.

---

## Layer 5 — Revenue Share (requires Stripe Connect, not a Product)

Since companies built on Genesis will have their *own* Stripe accounts to accept their own customers' payments, revenue share only works through **Stripe Connect**:

1. Each real-launched company's Stripe account becomes a **Connected Account** under your Genesis Platform account.
2. On every payment that connected company processes, use an **application fee** — either:
   - `application_fee_percent: 5` on a **destination charge**, or
   - `application_fee_amount` calculated per-transaction if you need more control than a flat percentage
3. Stripe automatically routes 5% to your platform balance and the rest to the company's connected account — no manual reconciliation needed.
4. **You'll need to build the cap/term logic yourself** — Stripe doesn't natively track "stop collecting once 2x is reached" or "stop after 7 years." That has to live in your own backend: track cumulative application fees collected per connected account against that account's recorded build cost, and stop applying the fee once the cap or term limit hits (per Charter §9).

This is meaningfully more setup than Layers 1-4 (which are close to plug-and-play) — budget real engineering time for the Connect integration specifically.

---

## Quick-reference summary table

| # | Product | Stripe Price type | Amount | Recurring? |
|---|---|---|---|---|
| 1 | Genesis Cloud — Starter | Standard | $39/mo | Yes |
| 2 | Genesis Cloud — Builder | Standard | $149/mo | Yes |
| 3 | Genesis Cloud — Scale | Standard | $499/mo | Yes |
| 4 | Agent Compute Overage | Metered | $1.50/unit | Yes (usage-based) |
| 5 | Real-Launch Facilitation Fee | One-time | $299 | No |
| 6 | Revenue Share | Connect application fee (not a Product) | 5%, capped 2x, 7yr | Ongoing, per-transaction |
