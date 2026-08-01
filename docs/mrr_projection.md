# Revenue Projection — SwarmOS (honest math)

No one can guarantee profit. What follows is the **expected-value** math with the
levers the swarm now operates. Downside is near zero (you run on host-Ollama +
local containers; the only real costs are ElevenLabs voice credits and any paid
directory/spam tools).

Pricing (live in Stripe): Starter $29 · Growth $99 · Enterprise $299 /mo.

---

## Traffic engine (this week)

| Source | Realistic visitors/wk | Notes |
|---|---|---|
| Product Hunt (Mon) | 800–3,000 | Good launches reach low thousands |
| AI directories (8) | 300–1,500 | Compounding, long-tail SEO |
| Landing-page SEO/GEO | 100–500/wk | FAQ JSON-LD + mcp.json already live |
| Voice-agent word of mouth | 50–300 | The demo IS the pitch |

**Conservative midpoint: ~1,500 engaged visitors in week 1.**

## Conversion funnel

| Stage | Rate (conservative) | 1,500 visitors |
|---|---|---|
| Visit → try (voice agent / skeleton tool) | 40% | 600 |
| Try → signup | 15% | 90 |
| Signup → paid (Stripe self-serve) | 8% | ~7 paid |
| Avg revenue seat | — | ~$50/mo blended |
| **Expected first-month MRR** | — | **~$350** |

**First paying customer timing:** the fastest path is same-day — a PH visitor hits
the landing page, talks to the voice agent, signs up, and checks out via Stripe
(self-serve, minutes). Realistic window for the **first** sale: **this week**
(Mon–Fri) if launch traffic lands. Swarm-led outreach adds a slower but compounding
second path (drafts → your approval → delivery).

## What would break these numbers (and the countermeasures)

1. **Email goes to spam** → `deliverability` engine now checks SPF/DKIM/DMARC,
   generates records, and auto-suppresses bounces before they hurt reputation.
2. **Low trust / no social proof** → PH first-comment hook + live demo is the proof.
3. **Leads go cold** → growth loop drafts a quote within 6h of a high-intent lead;
   one approve-click and Stripe link goes out.
4. **No real leads in DB** → the Business Skeleton Generator captures emails from
   every tool visitor; those are high-intent leads (intent_score 70) automatically.

## To actually realize this

- Flip `OUTREACH_DRY_RUN=0` + approve the gate when you're ready to send real mail.
- Do the PH pre-launch tasks (20–30 early upvotes change everything).
- Submit the 8 directories Monday/Tuesday.
- Check `/autonomy` daily — approve, reject, watch `projected_mrr` climb.
