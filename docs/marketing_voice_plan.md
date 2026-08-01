# Genesis Go-To-Market Plan — Integrated from `marketing_voice.md`

This plan operationalizes `docs/marketing_voice.md` into a 14-day sprint the swarm
can execute alongside the founder. The differentiator is **"Zero-to-Provisioned"** —
an agentic OS that launches a real, runnable business in minutes — with the
**full-duplex voice agent** as the flagship proof of competence.

> Principle from the source doc: *"Because your product sounds like magic, your
> marketing needs to be highly tangible."* Every asset must show, not claim.

---

## Week 1 — Technical SEO & Agent-Readable Infrastructure

### Step 1. GEO Foundation (Generative Engine Optimization) — DONE CORE
- Add `SoftwareApplication` JSON-LD (featureList: "Full Duplex Voice AI",
  "Autonomous Business Provisioning", "Agentic OS") to the landing page `<head>`.
  [implemented in `frontend/src/app/page.tsx`]
- Add an FAQPage JSON-LD block (10 Q&As, answers under 50 words) so ChatGPT /
  Perplexity can cite Genesis directly.
- Verify with Google's Rich Results Test + Schema.org validator.
- **Success:** structured data validates; GPTBot fetch shows JSON-LD.

### Step 2. MCP (Model Context Protocol) integration
- Add `mcp.json` at repo root describing tools the OS exposes
  (`create_landing_page`, `provision_db`, `generate_content`, `create_ticket`).
- Keep provisioning logic out of the file — describe, don't expose (§ review by founder).
- **Success:** an agent can parse the tool manifest without reading source.

### Step 3. Latency-first landing page
- Voice agent is "warm" on load; barge-in detection is browser-side (local VAD)
  so interrupt latency stays sub-200ms. Already true: `BargeInDetector` is client-side.
- Measure "Time to First Word" and keep it under ~2s.
- **Success:** recorded demo shows interrupt <200ms.

### Step 4. Core Web Vitals / metadata
- Keep existing page SEO metadata (per-feature titles/descriptions) — do NOT strip.
- Add any missing canonical/OG image per page.
- Run Lighthouse + the founder's own speed/SEO re-analysis; fix only regressions.

---

## Week 2 — Content Moats & Distribution

### Step 5. "Barge-In" comparison assets (voice variant) / "Side-by-Side" provisioning (plan variant)
- Video A: user talks over the agent — it stops instantly.
- Video B: agent asks a clarifying question mid-typing.
- Video C: the fully "provisioned" business dashboard appears.
- Reels/TikTok/LinkedIn clips from these; hook: *"The first OS that builds your
  business while you talk to it."*

### Step 6. Product-led lead magnets (mini-tools)
- **Business Skeleton Generator** — 1-field tool; user types an idea → OS drafts the
  schema/roadmap → stop and ask for an email to continue. (BuilderAgent already
  produces a build manifest — wire it to this tool.)
- **Voice Latency Test** — in-browser tool comparing agent latency; show how Genesis wins.
- **"Alternative to X"** pages: *"Why wait for a dev team when the OS provisions itself?"*

### Step 7. The 2026 Business Velocity Report
- Publish an original data piece: time to launch a business via Genesis vs.
  traditional. AI answer engines prioritize unique, structured data.

### Step 8. Distribution
- Submit to Futurepedia, There's An AI For That, Product Hunt ("Natural
  Conversational Agentic OS").
- Reddit/Discord: r/SaaS, r/OpenAI — offer to "provision 5 businesses for free"
  in exchange for voice-naturalness feedback. No spam; always add value first.
- GitHub starter kit: open-source the `voice-engine.ts` barge-in wrapper as an SDK.

---

## SEO Checklist (verify, don't regress)

- [ ] `SoftwareApplication` JSON-LD live on `/`
- [ ] FAQPage JSON-LD live on `/`
- [ ] `mcp.json` at repo root
- [ ] Long-tail pages: "how to launch a business with AI 2026", "zero-config
      business provisioning", "full duplex voice AI for SaaS"
- [ ] Audio socket / Time-to-First-Word < 200ms (browser-side barge-in)
- [ ] Existing per-page meta preserved (do not strip working SEO)
- [ ] Re-run speed + SEO analysis after deploy; fix only regressions

---

## Agent-Digestible Task Array (JSON)

The swarm parses this to execute or draft each item.

```json
[
  {
    "phase": "Technical SEO",
    "task": "Generate_JSON_LD_Schema",
    "details": "SoftwareApplication + FAQPage schema for the landing page.",
    "agent_action": "Add the script tags to the homepage head; validate via schema.org.",
    "priority": "Critical"
  },
  {
    "phase": "Technical SEO",
    "task": "Create_MCP_Manifest",
    "details": "Root mcp.json describing provisioning/content/ticket tools.",
    "agent_action": "Write the manifest; do NOT include secrets or provisioning internals.",
    "priority": "High"
  },
  {
    "phase": "Content Marketing",
    "task": "Draft_BargeIn_Feature_Post",
    "details": "500-word technical post: Half-Duplex vs Full-Duplex AI voice agents.",
    "keywords": ["VAD", "AEC", "Latency", "Human-grade AI"],
    "agent_action": "Draft the article + 3 LinkedIn hooks.",
    "priority": "Medium"
  },
  {
    "phase": "GEO Optimization",
    "task": "Create_FAQ_for_AI_Answer_Engines",
    "details": "10 Q&As: 'How to launch a business in 5 minutes', 'What is an agentic OS'.",
    "agent_action": "Generate direct, authoritative Q&A pairs; answers under 50 words.",
    "priority": "High"
  },
  {
    "phase": "Product-Led Growth",
    "task": "Generate_Provisioning_Demo_Scripts",
    "details": "5 launch scenarios (E-commerce, Newsletter, SaaS, Agency, Local Service).",
    "agent_action": "Write full voice-agent dialogue scripts incl. likely barge-in points.",
    "priority": "Medium"
  },
  {
    "phase": "Distribution",
    "task": "Identify_Outreach_Targets",
    "details": "Find communities complaining about stilted voice AI / slow business setup.",
    "agent_action": "List top 10 thread URLs + draft non-spammy helpful responses.",
    "priority": "Low"
  }
]
```

## Founder's Role (what the swarm cannot do)
- Approve/send external communications (constitution §4.4: `ai_drafted_human_reviewed`).
- Choose the voice persona's "warmth" — the human feel of the duplex interaction.
- Review `mcp.json` before deploy so no provisioning logic leaks.
- Verify the provisioning infra the OS creates is secure and cost-optimized.

## How the swarm goes live with founder outreach
1. Founder runs the Outreach page: pick a campaign template, fill in targets, save it.
2. The `outreach_agent` drafts each message (human-reviewed per constitution).
3. Founder reviews and approves the send queue.
4. Leads come back as new leads; the leads page auto-qualifies; tickets auto-create
   for follow-ups; workflows nurture and re-engage.
5. Repeat with the refined voice agent on the landing page converting visitors.
