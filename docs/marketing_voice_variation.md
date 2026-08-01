# Genesis Go-To-Market — VARIATION A (focal point: Zero-to-Provisioned Launch OS)

> This is the exact `marketing_voice_plan.md` with **one change**: the marketing
> campaign's focal point is the **Zero-to-Provisioned autonomous business launch
> OS** instead of the full-duplex voice agent. Everything else (structure, phases,
> checklist, agent task array, founder's role) is unchanged.

Use this variation to go to market **now** while the voice agent is still being
refined. The launch OS is already real and verifiable: Company Builder, workflow
templates, the 15-agent workforce, and real ticket/lead pipelines all work today.

## The one change: focal point

| Aspect | Original (voice-first) | Variation A (launch-first) |
|---|---|---|
| Hero claim | "Talk to your business OS" | "**Launch a real business in minutes**" |
| Proof asset | Barge-in demo video | **Side-by-side provisioning video** (OS builds the company, infra, content, and launch plan while you watch) |
| Lead magnet | Voice Latency Test | **Business Skeleton Generator** (type an idea → get a provisionable roadmap) |
| Distribution hook | "The first OS that builds your business while you talk to it." | "**The OS that goes from idea to provisioned business while you're on your coffee break.**" |
| Secondary highlight | Voice agent (as it improves) | 15-agent workforce + auto-provisioning + workflow templates |

## What stays identical
- Week 1 GEO/MCP/latency steps (the schema, `mcp.json`, metadata work is the same).
- Week 2 content moats & distribution mechanics.
- SEO checklist (minus voice-specific latency item, which is folded into "Time to
  provisioned outcome").
- Agent-digestible JSON task array (same tasks, wording unchanged).
- Founder's role and the swarm-outreach flow.

## Variation A mini-task array (reworded hook only)

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
    "phase": "Content Marketing",
    "task": "Draft_ZeroToProvisioned_Post",
    "details": "500-word post: 'Why an OS that provisions your business beats another AI wrapper'.",
    "keywords": ["zero-config", "business provisioning", "autonomous launch"],
    "agent_action": "Draft the article + 3 LinkedIn hooks.",
    "priority": "Medium"
  },
  {
    "phase": "Product-Led Growth",
    "task": "Wire_Business_Skeleton_Generator",
    "details": "1-field tool wired to BuilderAgent returning a build manifest + roadmap.",
    "agent_action": "Add the UI + endpoint; stop at the email-gate before full provisioning.",
    "priority": "High"
  },
  {
    "phase": "Distribution",
    "task": "Record_Provisioning_SideBySide",
    "details": "Screen capture: manual setup vs. Genesis auto-provisioning to a live dashboard.",
    "agent_action": "Draft the script + shot list; founder records.",
    "priority": "High"
  }
]
```

## Recommended sequencing
1. Ship Variation A immediately (launch OS is real today).
2. Keep the voice agent live on the landing page as the conversion layer — it is the
   "wow" once it's natural enough.
3. Pivot to the voice-first plan (`marketing_voice_plan.md`) when the voice agent
   passes the natural-conversation bar.
