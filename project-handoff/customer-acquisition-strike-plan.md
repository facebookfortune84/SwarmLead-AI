# Customer Acquisition Strike Plan

**Generated**: 2026-07-26  
**Role**: Genesis Strike Team Commander  
**Objective**: Re-baseline execution plan around customer acquisition, conversion, retention, autonomous business creation

---

## 1. Voice System Plan

### Architecture Decision: Extend Existing Runtime Agents

| New Component | Implementation Strategy | Base Agent | Reuse % |
|---------------|------------------------|------------|---------|
| **VoiceAgent** | OutreachAgent specialization | OutreachAgent | 85% |
| **VoiceOrchestrator** | TaskRouter specialization | TaskRouter | 90% |
| **VoiceSessionManager** | Scheduler + SessionMemory extension | Scheduler | 80% |
| **ConversationMemoryAdapter** | LongTermMemory + VectorStore adapter | LongTermMemory | 85% |

### VoiceAgent Design (OutreachAgent Specialization)

**File**: `core/agents/voice/voice_agent.py` (new)

```python
# Extends OutreachAgent with voice capabilities
class VoiceAgent(OutreachAgent):
    async def process_voice_input(self, audio_stream, session_id, context):
        # 1. STT via ElevenLabs API
        # 2. Process via existing LLM pipeline (reuse StrategyAgent logic)
        # 3. TTS via ElevenLabs streaming
        # 4. Return audio stream
```

**Capabilities Added**:
- `speech_to_text(audio_stream)` → ElevenLabs STT
- `text_to_speech_stream(text)` → ElevenLabs TTS streaming
- `handle_interruption(audio_chunk)` → Barge-in detection
- `maintain_session_context(session_id)` → ConversationMemoryAdapter

### VoiceOrchestrator Design (TaskRouter Specialization)

**File**: `core/orchestration/voice_orchestrator.py` (new)

```python
# Extends TaskRouter for voice-specific routing
class VoiceOrchestrator(TaskRouter):
    def route_voice_task(self, session_id, intent, context):
        # Route to VoiceAgent, StrategyAgent, OutreachAgent based on intent
        # Handle voice-specific context (interruption, resumption)
```

### VoiceSessionManager Design (Scheduler Extension)

**File**: `core/orchestration/voice_session_manager.py` (new)

```python
# Extends Scheduler for voice session lifecycle
class VoiceSessionManager(Scheduler):
    def create_voice_session(self, visitor_id, greeting_type):
        # Initialize ElevenLabs conversation
        # Set up streaming audio pipes
        # Register with VoiceOrchestrator
    
    def handle_barge_in(self, session_id, interruption_audio):
        # Immediate stop TTS
        # Process interruption intent
        # Resume with new context
```

### ConversationMemoryAdapter Design (LongTermMemory Adapter)

**File**: `core/memory/conversation_memory_adapter.py` (new)

```python
# Adapts LongTermMemory for voice conversations
class ConversationMemoryAdapter:
    def store_turn(self, session_id, role, text, audio_meta):
        # Store as structured memory with audio metadata
    
    def get_context(self, session_id, window=10):
        # Return last N turns for context injection
    
    def resume_session(self, session_id):
        # Full conversation reconstruction
```

### ElevenLabs Integration

**File**: `core/integrations/elevenlabs/elevenlabs_client.py` (new)

```python
class ElevenLabsClient:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def text_to_speech_stream(self, text, voice_id="default", model_id="eleven_multilingual_v2"):
        # Streaming TTS with <200ms first-byte latency
    
    async def speech_to_text(self, audio_stream):
        # Streaming STT
    
    def create_conversation(self, agent_config):
        # Create persistent conversation for session resumption
```

### Barge-In Support Implementation

| Component | Mechanism |
|-----------|-----------|
| **Detection** | WebRTC VAD on client → send interruption signal via WebSocket |
| **Interruption** | VoiceOrchestrator receives signal → immediately cancels TTS stream via ElevenLabs API |
| **Processing** | VoiceAgent processes interruption as new turn with `interruption=true` flag |
| **Resumption** | ConversationMemoryAdapter provides full context; VoiceAgent continues |

### Environment Variables Required

```bash
ELEVENLABS_API_KEY=sk_xxx
ELEVENLABS_DEFAULT_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
ELEVENLABS_STT_MODEL=scribe_v1
VOICE_SESSION_TIMEOUT_MINUTES=30
VOICE_BARGE_IN_THRESHOLD_MS=100
```

---

## 2. Landing Page Agent Plan

### Agent Design: StrategyAgent Specialization

**File**: `core/agents/landing/landing_agent.py` (new)

```python
class LandingAgent(StrategyAgent):
    """Proactive voice-enabled landing page agent"""
    
    FLOWS = {
        "lead_qualification": LeadQualificationFlow,
        "founder_discovery": FounderDiscoveryFlow,
        "business_launch": BusinessLaunchDiscoveryFlow,
        "product_recommendation": ProductRecommendationFlow,
    }
    
    async def greet_visitor(self, session_id, visitor_context):
        # Proactive greeting based on visitor context
        # Voice-first, text fallback
    
    async def execute_flow(self, flow_name, session_id, context):
        # Execute specific flow with voice-first UX
```

### Flow Implementations (StrategyAgent Memory + LLM)

**LeadQualificationFlow** (`core/agents/landing/flows/lead_qualification.py`):
- Identify: "What brings you to Genesis today?"
- Qualify: Company stage, team size, current challenges
- Route: Self-serve vs. assisted onboarding

**FounderDiscoveryFlow** (`core/agents/landing/flows/founder_discovery.py`):
- Deep dive: Vision, constraints, timeline, budget
- Generate: Preliminary business concept
- Output: Founder profile for onboarding

**BusinessLaunchDiscoveryFlow** (`core/agents/landing/flows/business_launch.py`):
- Assess: Idea maturity, market, competition
- Recommend: Genesis tier, timeline, investment
- Output: Launch readiness score

**ProductRecommendationFlow** (`core/agents/landing/flows/product_recommendation.py`):
- Match: Visitor needs → Genesis capabilities
- Demo: Voice-guided feature walkthrough
- Convert: Trial → Paid path

### Frontend Integration

**File**: `frontend/src/components/landing/VoiceLandingAgent.tsx` (new)

```tsx
// Voice-first landing experience
// WebRTC audio capture → WebSocket → VoiceOrchestrator
// Proactive greeting on page load (with permission)
// Full voice navigation of flows
// Text fallback for accessibility
```

### Greeting Triggers

| Trigger | Delay | Greeting Type |
|---------|-------|---------------|
| Page load | 3s | Proactive voice greeting |
| Scroll 50% | 1s | Contextual offer |
| Exit intent | Immediate | Retention offer |
| Return visitor | 0s | Personalized welcome |

---

## 3. Frontend Premiumization Plan

### Current State Analysis

| Aspect | Current | Target | Gap |
|--------|---------|--------|-----|
| **Design System** | shadcn/ui + Tailwind | Custom luxury design system | High |
| **Animation** | None | Framer Motion + custom transitions | High |
| **Landing Page** | Redirect to /dashboard | Voice-first marketing page | Critical |
| **Onboarding** | Basic forms | Voice-guided multi-step | High |
| **Dashboard** | Basic cards | Agent workspace, real-time voice | High |
| **Agent Workspace** | Static list | Live agent monitoring, voice controls | Critical |
| **Mobile** | Responsive | Voice-optimized mobile | Medium |

### Missing Components

| Component | Purpose | Priority |
|-----------|---------|----------|
| `VoiceOrb.tsx` | Animated voice activity indicator | Critical |
| `VoiceWaveform.tsx` | Real-time audio visualization | High |
| `AgentAvatar.tsx` | Animated agent personas | Medium |
| `OnboardingWizard.tsx` | Voice-guided multi-step | Critical |
| `PremiumCard.tsx` | Luxury metric cards | Medium |
| `LiveMetrics.tsx` | Real-time animated metrics | High |
| `ConversionFunnel.tsx` | Visual funnel with voice narration | Medium |

### Animation System

**File**: `frontend/src/lib/animations.ts` (new)

```typescript
// Framer Motion variants for luxury feel
export const premiumVariants = {
  pageEnter: { opacity: 0, y: 20, transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] } },
  cardHover: { scale: 1.02, boxShadow: "0 20px 40px rgba(0,0,0,0.1)" },
  voicePulse: { scale: [1, 1.05, 1], transition: { repeat: Infinity, duration: 1.5 } },
  metricCount: { initial: 0, animate: { value: 100 }, transition: { duration: 2 } },
}
```

### Missing Screens

| Screen | Purpose | Voice Integration |
|--------|---------|-------------------|
| `/` (Landing) | Marketing + voice agent | Full voice experience |
| `/onboarding` | Voice-guided setup | Full voice |
| `/voice-demo` | Live voice trial | Full voice |
| `/pricing` | Interactive with voice FAQ | Voice FAQ |
| `/dashboard` | Agent workspace | Live voice controls |
| `/agents` | Agent management | Voice commands |

### Conversion Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| No voice on landing | High bounce | Implement VoiceLandingAgent first |
| Basic dashboard | Low perceived value | Premium dashboard with live agents |
| No mobile voice | 60% traffic loss | Voice-optimized mobile UX |
| Slow TTFB | SEO penalty | Edge deployment, streaming |

---

## 4. SEO Domination Plan

### Technical SEO (Foundation)

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| **Core Web Vitals** | Next.js 16 + Turbopack + edge | Partial |
| **Structured Data** | JSON-LD for SaaS, Product, FAQ | Missing |
| **Schema.org** | Organization, SoftwareApplication, Service | Missing |
| **Sitemap** | Auto-generated with `next-sitemap` | Missing |
| **Robots.txt** | Dynamic with environment awareness | Missing |
| **Canonical URLs** | All pages | Partial |
| **Hreflang** | Multi-language ready | Missing |
| **CSP Headers** | Security + SEO friendly | Missing |

### Content SEO (Landing + Programmatic)

**Landing Page Content Structure**:
```html
<!-- Schema.org: SoftwareApplication + Service -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Genesis",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Cloud",
  "offers": { "@type": "Offer", "price": "39", "priceCurrency": "USD" },
  "featureList": ["Voice AI Agents", "Autonomous Business Launch", "Lead Generation", "Workflow Automation"]
}
</script>
```

### Programmatic SEO Opportunities

| Page Type | Template | Target Keywords | Volume |
|-----------|----------|-----------------|--------|
| **Industry Templates** | `/templates/{industry}` | "{industry} lead generation", "{industry} automation" | 50k+/mo |
| **Use Cases** | `/use-cases/{problem}` | "automate {task}", "AI {outcome}" | 100k+/mo |
| **Templates** | `/templates/{type}` | "{type} template", "free {type}" | 200k+/mo |
| **Comparisons** | `/vs/{competitor}` | "{competitor} alternative", "{competitor} vs" | 50k+/mo |
| **Glossary** | `/glossary/{term}` | "{term} definition", "what is {term}" | 1M+/mo |

### Long-Tail Capture Strategy

| Content Cluster | Target Intent | Content Format |
|-----------------|---------------|----------------|
| **Founder/Business Creation** | "how to start a business", "startup launch checklist" | Guides + voice walkthrough |
| **Lead Generation** | "B2B lead gen", "cold email templates" | Templates + voice agent |
| **Workflow Automation** | "automate {process}", "no-code automation" | Demos + voice walkthrough |
| **AI Agents** | "AI sales agent", "autonomous AI" | Voice demos + case studies |

### Core Web Vitals Targets

| Metric | Target | Implementation |
|------|--------|----------------|
| **LCP** | <2.5s | Edge rendering, image optimization, font preloading |
| **FID** | <100ms | Code splitting, web workers, minimal main thread |
| **CLS** | <0.1 | Font display swap, aspect ratios, reserved space |
| **INP** | <200ms | React 19 concurrent features, useTransition |

---

## 5. Customer Acquisition Plan

### Funnel Architecture

```
Traffic Funnel → Lead Funnel → Qualification Funnel → Conversion Funnel → Retention Funnel → Expansion Funnel
```

### Agent Automation by Funnel Stage

| Funnel | Agent | Automation Level | Human Touchpoint |
|--------|-------|------------------|------------------|
| **Traffic** | SEOAgent + ContentAgent | 90% | Strategy review |
| **Lead** | LandingAgent (Voice) | 100% | None |
| **Qualification** | LandingAgent + StrategyAgent | 95% | Edge cases |
| **Conversion** | StrategyAgent + PaymentAgent | 80% | Legal/financial review |
| **Retention** | MonitoringAgent + OutreachAgent | 90% | Success manager |
| **Expansion** | GrowthAgent + StrategyAgent | 85% | Account manager |

### Agent Implementation Classification

| Agent | Type | Base Agent | Rationale |
|-------|------|------------|-----------|
| **VoiceAgent** | Specialization | OutreachAgent | 85% reuse; voice = new channel |
| **OnboardingAgent** | Specialization | StrategyAgent | 80% reuse; onboarding = strategy subset |
| **SEOAgent** | New Runtime | BaseAgent | No existing pattern; content + technical |
| **ContentAgent** | Specialization | BuilderAgent | 75% reuse; content = code-like generation |
| **GrowthAgent** | Specialization | StrategyAgent | 85% reuse; growth = strategy application |

### New Runtime Agents Required

| Agent | File | Base | New Code % |
|-------|------|------|------------|
| **VoiceAgent** | `core/agents/voice/voice_agent.py` | OutreachAgent | 15% |
| **SEOAgent** | `core/agents/seo/seo_agent.py` | BaseAgent | 100% |
| **ContentAgent** | `core/agents/content/content_agent.py` | BuilderAgent | 25% |
| **GrowthAgent** | `core/agents/growth/growth_agent.py` | StrategyAgent | 15% |

### Specializations (No New Runtime)

| Agent | Base | Implementation |
|-------|------|----------------|
| **OnboardingAgent** | StrategyAgent | `core/agents/onboarding/onboarding_agent.py` |
| **LandingAgent** | StrategyAgent | `core/agents/landing/landing_agent.py` |

---

## 6. Agent Workforce Recommendations

### Final Agent Architecture (15 Runtime + 2 Specializations = 17)

| Category | Agents | Status |
|----------|--------|--------|
| **Core Runtime (12)** | Strategy, Outreach, Builder, Repair, Review, AgentManager, TaskRouter, Scheduler, SwarmCoordinator, SwarmDecisionEngine, SwarmEvaluator, AutonomousSwarm | ✅ Active |
| **Constitutional (3)** | GovernanceAgent, AuditAgent, MonitoringAgent | 🔄 Build |
| **Voice (1)** | VoiceAgent | 🔄 Build |
| **Growth (2)** | SEOAgent, ContentAgent | 🔄 Build |
| **Specializations (2)** | OnboardingAgent, LandingAgent | 🔄 Build (StrategyAgent) |
| **Total** | **17** | |

### Activation Priority

| Priority | Agents | Reason |
|----------|--------|--------|
| **P0** | GovernanceAgent, AuditAgent, MonitoringAgent | Constitutional blockers |
| **P0** | VoiceAgent | Tier-0 requirement |
| **P1** | SEOAgent, ContentAgent | Revenue acceleration |
| **P1** | OnboardingAgent, LandingAgent | Conversion |
| **P2** | GrowthAgent | Expansion |

---

## 7. Updated Production Priorities

| Priority | Work | Sprint | Dependency |
|----------|------|--------|------------|
| **1** | Portfolio Isolation (tenant scoping) | 1 | None |
| **2** | Monetary Rules (7 rules) | 1 | None |
| **3** | Agent Identity + Domain Gating | 1 | #1 |
| **4** | Monitoring Implementation | 1 | None |
| **5** | Voice System (Agent + Orchestrator + Session + Memory + ElevenLabs) | 1 | #1 |
| **6** | LandingAgent + VoiceLandingPage | 2 | #5 |
| **7** | GovernanceAgent + AuditAgent + MonitoringAgent | 2 | #1, #3 |
| **8** | SEOAgent + ContentAgent | 2 | #7 |
| **9** | OnboardingAgent + Premium Frontend | 2 | #5, #6 |
| **10** | httpOnly Auth + Rate Limiting + Cloud LLM | 3 | #3 |
| **11** | Compliance Tests + Load Test + Security Audit | 3 | #7, #10 |
| **12** | Beta Launch + Billing Validation | 3 | #8, #9 |

---

## 8. Updated Critical Path

```
Day 1:     Streams A+B+C+E parallel (Tenant Isolation, Monetary Rules, Monitoring, Security)
           ↓
Day 1-3:   Voice System (parallel with above - independent)
           ↓
Day 4:     Stream D: GovernanceAgent + AuditAgent + MonitoringAgent (requires tenant context)
           ↓
Day 5-7:   LandingAgent + VoiceLandingPage + OnboardingAgent (requires VoiceAgent)
           ↓
Day 8-10:  SEOAgent + ContentAgent + Premium Frontend (requires GovernanceAgent)
           ↓
Day 11-14: httpOnly Auth, Rate Limiting, Cloud LLM, Compliance Tests
           ↓
Day 15:    Beta Launch
```

**Total: 15 days to revenue** (vs 8 weeks original)

---

## 9. Updated MVP Definition

### Smallest Revenue-Generating Genesis

| Capability | Implementation | Voice |
|------------|----------------|-------|
| **Landing** | VoiceLandingAgent + SEO content | ✅ Full |
| **Onboarding** | OnboardingAgent (voice-guided) | ✅ Full |
| **Lead Gen** | StrategyAgent + OutreachAgent | ✅ Text + Voice |
| **Tenant Provisioning** | BoxDeployer + tenant scoping | ⚠️ Text |
| **Payments** | Stripe + Monetary Rules | ⚠️ Text |
| **Dashboard** | Premium + Agent Workspace + Live Voice | ✅ Full |
| **Governance** | GovernanceAgent + AuditAgent + MonitoringAgent | ⚠️ Text |
| **SEO** | Programmatic + Technical | ✅ Full |

### MVP Agent Count: 15 Runtime

---

## 10. Updated Revenue Acceleration Strategy

### Revenue Streams (Priority Order)

| Stream | Readiness | Target Launch | Monthly Target |
|--------|-----------|---------------|----------------|
| **Genesis Cloud ($39/$149/$499)** | 90% | Day 15 | $10k MRR |
| **Real-Launch Fee ($299)** | 80% | Day 30 | $5k MRR |
| **Usage Overage ($1.50/hr)** | 60% | Day 60 | $3k MRR |
| **Revenue Share (5%)** | 40% | Day 90 | Variable |

### Acquisition Channels (Automated)

| Channel | Agent | CAC Target | Timeline |
|---------|-------|------------|----------|
| **Organic SEO** | SEOAgent | $0 | Month 1-3 |
| **Voice Landing** | LandingAgent | $50 | Day 15 |
| **Content Marketing** | ContentAgent | $100 | Month 1 |
| **Referral/Expansion** | GrowthAgent | $0 | Month 2 |

### Conversion Optimization Loop

```
LandingAgent (voice) → OnboardingAgent (voice) → StrategyAgent (plan) 
    → BuilderAgent (build) → OutreachAgent (execute) → MonitoringAgent (optimize)
        ↓
    Conversion Funnel Analytics → SEOAgent (content) → ContentAgent (create) 
        ↓
    Programmatic SEO Pages → Traffic → LandingAgent
```

### Key Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Voice Engagement Rate** | >60% | Sessions with >2 turns |
| **Voice-to-Signup** | >15% | Voice session → trial |
| **Time-to-First-Value** | <10 min | Onboarding completion |
| **LTV/CAC** | >10x | 12-month cohort |
| **Voice Session Duration** | >5 min | Engagement quality |

---

## Implementation Leverage Summary

| Leverage Point | Impact | Effort |
|----------------|--------|--------|
| **OutreachAgent → VoiceAgent** | 85% reuse, new channel | 15% new |
| **StrategyAgent → Landing/Onboarding/Growth** | 80-85% reuse, 3 agents | 15-20% each |
| **BuilderAgent → ContentAgent** | 75% reuse, content = code | 25% new |
| **TaskRouter → VoiceOrchestrator** | 90% reuse, routing = routing | 10% new |
| **Scheduler → VoiceSessionManager** | 80% reuse, sessions = tasks | 20% new |
| **LongTermMemory → ConversationMemoryAdapter** | 85% reuse, adapter pattern | 15% new |
| **Constitution → GovernanceAgent** | Policy as code, not docs | New but high leverage |
| **Existing 559 Tests** | Zero regression work | Test-first new features |

---

**Strike Team Execution Order**: 
1. **Parallel Streams A-E** (Constitutional + Voice)
2. **Governance Agents** (enforcement layer)
3. **Growth Agents + Premium Frontend** (revenue layer)
4. **Beta Launch** (validation)
4. **Scale** (autonomous)

**The platform acquires, converts, and onboards itself. The agents are the product.**