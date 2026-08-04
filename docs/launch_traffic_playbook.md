# Launch Traffic Playbook — Genesis Forge × Realms 2 Riches

The system drafts everything; **you are the launch amplifier**. This playbook
is your explicit day-by-day job list for the launch window (Aug 3–10, 2026).
Do these once a day — each is 5–10 minutes.

> Where does automation end and you begin?
> The growth loop (every 6h) discovers leads, drafts outreach + traffic posts,
> and queues them for approval. **The human gate is the publish step.** This
> playbook is that step, made repeatable.

---

## 0. Every morning — the 3-minute approval sweep

1. Open the Autonomy console (or `curl http://localhost:8000/api/launch/traffic/queue`).
2. Review the queued **traffic posts** (X / LinkedIn / Facebook / Reddit copy
   already drafted and personalized to the launch).
3. Approve the ones you like → copy → paste → post. Record the post URL in the
   queue notes so the loop never re-drafts it.
4. Check the **outreach queue** and approve the best 2–3 cold emails
   (they only go out after you press approve — that is the product's single
   human gate in action).

## 1. Daily social blast (10 min)

Use the share buttons on the landing page — they pre-fill everything:

| Day | X (Twitter) | LinkedIn | Facebook |
| --- | --- | --- | --- |
| Aug 3 | Launch post + PH link | "I built this" post | Launch announcement |
| Aug 4 | Feature: barge-in | Barge-in demo angle | ROI story |
| Aug 5 | "15 agents" thread | Agentic OS explainer | Voice AI demo clip |
| Aug 6 | Testimonial retweet | Customer story | Checklist giveaway |
| Aug 7 | Pricing thread | Comparison to manual ops | Video: 3-min setup |
| Aug 8 | FAQ thread | Behind the scenes | Referral program post |
| Aug 9 | Last-chance: 1 month free | Metrics post | Countdown to end of week |
| Aug 10 | Thank-you + recap | Lessons learned | Referral reminder |

Always tag **@ProductHunt**, add `#ProductHunt #LaunchDay`, and reply to
every comment within 1 hour (reply velocity is a ranking factor).

## 2. Product Hunt daily loop (15 min)

- **Morning:** upvote the launch, comment on the top 5 other launches of the
  day (real, useful comments — never spam).
- **Noon:** post one of the drafted PH comments
  (`/api/launch/traffic/drafts`, network `product_hunt`).
- **Evening:** reply to every question on your own page. Suggest the
  "Genesis Forge" product tag to friends — upvotes in the first 24h decide
  "Product of the Day".

## 3. Communities (choose 2, stay consistent)

1. **r/Entrepreneur / r/SideProject / r/SaaS** — post the Reddit draft, then
   answer every comment. No link-dumps: lead with the story, link at the end.
2. **Indie Hackers** — "I built a business that launches businesses" post.
3. **Facebook founder groups** — 1–2 groups where you're already active.
4. **Discord/Slack for startup founders** — the voice demo link lands well.

## 4. Email your network (once, not spammy)

One personal email to your contacts: what you built, the 1-month-free code
`LAUNCH100`, the link. Ask for one thing: an upvote, not a sale.

## 5. Weekly live demo (optional but high-converting)

A 15-minute Loom or live stream: "Watch an AI launch a business by voice."
The voice agent + company builder ARE the demo — no slide deck needed.

---

## Automation you already have (do not rebuild)

- **Lead discovery** — Bing RSS + DuckDuckGo → real businesses with contact
  emails, MX-validated, junk filtered (`core/services/lead_discovery.py`).
- **Outreach drafting** — personalized emails queued for approval every 6h.
- **Voice capture** — every visitor who talks to the voice agent and leaves
  an email becomes a high-intent lead (`source: voice`).
- **Landing captures** — the plan quiz, exit-intent popup and 30-point
  checklist magnet all write leads through `/api/voice/capture`.
- **SEO** — 12 programmatic industry pages + sitemap + JSON-LD.
- **Referral** — referrer gets $50 credit, referee gets 20% off.
- **Traffic drafts** — the growth loop composes social + PH copy into your
  approval queue during launch week (`/api/launch/traffic/drafts`).

## Conversion checklist (every lead)

| Lead source | First action the system takes | You approve |
| --- | --- | --- |
| Voice capture | High-intent lead, `needs_review` | Reach out within 24h |
| Plan quiz | High-intent (90) lead | Send plan + checklist |
| Checklist magnet | Lead + nurture email queued | Approve the send |
| Exit intent | Lead + 1-month-free offer queued | Approve the send |
| Discovery | Business-domain lead, outreach draft | Approve send |
| High-intent (score ≥60) | Stripe checkout offer drafted | Approve quote |

## Deliverability rules (protect the pipeline)

- Keep `OUTREACH_DRY_RUN=1` until DNS is verified (see
  `docs/email_alias.md`), then flip to `0`.
- Never exceed the 40/hr rate cap or 2/cycle per domain — the loop enforces it.
- Bounces / unsubscribes auto-suppress forever.
