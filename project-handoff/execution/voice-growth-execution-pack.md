# Voice & Growth Execution Pack

**Branch**: `implementation/voice-and-growth`  
**Base Commit**: `c6aabdd` (upstream)  
**Target**: Voice-first customer acquisition — VoiceAgent, LandingAgent, OnboardingAgent, SEOAgent, ContentAgent, GrowthAgent  
**Swarm**: 11 agents (Voice × 4, Growth × 5, Landing/Onboarding × 2)  
**Duration**: Parallel execution, Voice-first priority

---

## 1. Voice System (Tier-0 Launch Critical)

### 1.1 VoiceAgent — OutreachAgent Specialization (85% Reuse)

**File**: `core/agents/voice/voice_agent.py`

```python
# Extends OutreachAgent with voice capabilities
class VoiceAgent(OutreachAgent):
    def __init__(self, name: str, config, elevenlabs_client):
        super().__init__(name, config)
        self.elevenlabs = elevenlabs_client
        self.memory_adapter = ConversationMemoryAdapter()
    
    async def process_voice_input(self, audio_stream, session_id: str, context: dict):
        # 1. STT via ElevenLabs
        stt_result = await self.elevenlabs.speech_to_text(audio_stream)
        
        # 2. Process via existing LLM pipeline (reuse StrategyAgent logic)
        text_response = await self._process_with_context(
            stt_result.text, 
            session_id, 
            context
        )
        
        # 3. TTS via ElevenLabs streaming
        tts_stream = self.elevenlabs.text_to_speech_stream(text_response)
        
        return tts_stream
    
    async def handle_interruption(self, session_id: str, interruption_audio: bytes):
        """Barge-in support: stop TTS, process interruption, resume"""
        await self.elevenlabs.cancel_stream(session_id)
        stt_result = await self.elevenlabs.speech_to_text(interruption_audio)
        context = await self.memory_adapter.get_context(session_id)
        return await self.process_voice_input(stt_result.text, session_id, context)
```

**Reuses from OutreachAgent:**
- `execute()` — core execution logic
- `validate()` — input validation
- `call_llm()` — LLM integration
- Memory integration (LongTermMemory, VectorStore)

---

### 1.2 VoiceOrchestrator — TaskRouter Specialization (90% Reuse)

**File**: `core/orchestration/voice_orchestrator.py`

```python
class VoiceOrchestrator(TaskRouter):
    def __init__(self, agent_manager, elevenlabs_client, memory_adapter):
        super().__init__(agent_manager)
        self.elevenlabs = elevenlabs_client
        self.memory_adapter = memory_adapter
        self.active_streams = {}  # session_id -> stream
    
    async def route_voice_task(self, session_id: str, intent: str, context: dict):
        """Route voice intent to appropriate agent"""
        route_map = {
            "qualify": "voice_agent",
            "founder_discovery": "voice_agent", 
            "business_launch": "voice_agent",
            "product_recommendation": "voice_agent",
            "onboarding": "onboarding_agent",
            "strategy": "strategy_agent"
        }
        agent_name = route_map.get(intent, "voice_agent")
        agent = self.agent_manager.get_agent(agent_name)
        return await agent.execute(context, session_id)
    
    async def handle_barge_in(self, session_id: str, interruption_audio: bytes):
        # 1. Immediately cancel active TTS stream
        if session_id in self.active_streams:
            await self.elevenlabs.cancel_stream(session_id)
        
        # 2. Process interruption as new turn
        stt_result = await self.elevenlabs.speech_to_text(interruption_audio)
        context = await self.memory_adapter.get_context(session_id)
        
        # Route interruption as new turn with flag
        context["interruption"] = True
        return await self.route_voice_task(session_id, "qualify", context)
```

---

### 1.3 VoiceSessionManager — Scheduler Extension (80% Reuse)

**File**: `core/orchestration/voice_session_manager.py`

```python
class VoiceSessionManager(Scheduler):
    def __init__(self, elevenlabs_client, memory_adapter):
        super().__init__()
        self.elevenlabs = elevenlabs_client
        self.memory_adapter = memory_adapter
        self.sessions = {}  # session_id -> VoiceSession
    
    def create_voice_session(self, visitor_id: str, greeting_type: str = "proactive") -> VoiceSession:
        session_id = f"voice_{visitor_id}_{uuid.uuid4().hex[:8]}"
        session = VoiceSession(
            id=session_id,
            visitor_id=visitor_id,
            greeting_type=greeting_type,
            elevenlabs_conversation=self.elevenlabs.create_conversation(),
            memory_adapter=self.memory_adapter
        )
        self.sessions[session_id] = session
        return session
    
    async def handle_barge_in(self, session_id: str, interruption_audio: bytes):
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # 1. Cancel active TTS
        await self.elevenlabs.cancel_stream(session.elevenlabs_conversation_id)
        
        # 2. Process interruption
        stt_result = await self.elevenlabs.speech_to_text(interruption_audio)
        
        # 3. Process as new turn with interruption context
        context = await self.memory_adapter.get_context(session_id)
        context["interruption"] = True
        
        # Resume session with new context
        return await session.resume(stt_result.text, context)
    
    def cleanup_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
```

---

### 1.4 ConversationMemoryAdapter — LongTermMemory Adapter (85% Reuse)

**File**: `core/memory/conversation_memory_adapter.py`

```python
class ConversationMemoryAdapter:
    """Adapts LongTermMemory for voice conversations"""
    
    def __init__(self, long_term_memory: LongTermMemory):
        self.ltm = long_term_memory
    
    def store_turn(self, session_id: str, role: str, text: str, audio_meta: dict):
        """Store voice turn with audio metadata"""
        turn = {
            "session_id": session_id,
            "role": role,  # "user" | "assistant"
            "text": text,
            "audio_meta": audio_meta,  # duration, voice_id, model, latency
            "timestamp": datetime.utcnow().isoformat(),
            "turn_type": "interruption" if audio_meta.get("interruption") else "normal"
        }
        self.ltm.add({"content": json.dumps(turn), "type": "voice_turn"})
    
    def get_context(self, session_id: str, window: int = 10) -> List[dict]:
        """Get last N turns for context injection"""
        all_turns = self.ltm.query(f"session_id:{session_id} AND type:voice_turn")
        return all_turns[-window:]
    
    def resume_session(self, session_id: str) -> List[dict]:
        """Full conversation reconstruction for resumption"""
        return self.get_context(session_id, window=100)
```

---

### 1.5 ElevenLabs Integration

**File**: `core/integrations/elevenlabs/elevenlabs_client.py`

```python
class ElevenLabsClient:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = os.getenv("ELEVENLABS_DEFAULT_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        self.model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
        self.stt_model = os.getenv("ELEVENLABS_STT_MODEL", "scribe_v1")
    
    async def text_to_speech_stream(self, text: str, voice_id: str = None, model_id: str = None):
        """Streaming TTS with <200ms first-byte latency"""
        voice_id = voice_id or self.default_voice_id
        model_id = model_id or self.model_id
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/text-to-speech/{voice_id}/stream",
                headers={"xi-api-key": self.api_key},
                json={
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                }
            ) as resp:
                async for chunk in resp.content.iter_chunked(1024):
                    yield chunk
    
    async def speech_to_text(self, audio_stream: bytes) -> STTResult:
        """Streaming STT"""
        data = aiohttp.FormData()
        data.add_field('file', audio_stream, filename='audio.webm', content_type='audio/webm')
        data.add_field('model_id', self.stt_model)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/speech-to-text",
                headers={"xi-api-key": self.api_key},
                data=data
            ) as resp:
                data = await resp.json()
                return STTResult(text=data["text"], confidence=data.get("confidence", 1.0))
    
    def create_conversation(self, agent_config: dict) -> str:
        """Create persistent conversation for session resumption"""
        # POST /v1/conversations
        return "conversation_id"
    
    async def cancel_stream(self, conversation_id: str):
        """Cancel active TTS stream for barge-in"""
        # POST /v1/conversations/{id}/cancel
        pass
```

### Barge-In Engine — Critical Path

```python
# In VoiceOrchestrator
async def handle_barge_in(self, session_id: str, interruption_audio: bytes):
    # 1. IMMEDIATELY cancel active TTS stream via ElevenLabs API
    await self.elevenlabs.cancel_stream(self.active_streams.get(session_id))
    
    # 2. Process interruption as new turn with STT
    stt_result = await self.elevenlabs.speech_to_text(interruption_audio)
    
    # 3. Get current context from ConversationMemoryAdapter
    context = await self.memory_adapter.get_context(session_id)
    
    # 4. Process with interruption flag
    result = await self.voice_agent.process_turn(
        text=stt_result.text,
        session_id=session_id,
        context=context,
        interruption=True
    )
    
    # 5. Stream new TTS response
    await self.stream_tts(session_id, result.text)
```

---

## 2. Landing Agent (StrategyAgent Specialization — 80% Reuse)

### Files to Create
```
core/agents/landing/
├── __init__.py
├── landing_agent.py
└── flows/
    ├── __init__.py
    ├── lead_qualification.py
    ├── founder_discovery.py
    ├── business_launch.py
    └── product_recommendation.py
```

### Implementation Spec

**core/agents/landing/landing_agent.py**
```python
class LandingAgent(StrategyAgent):
    """Proactive voice-enabled landing page agent"""
    
    FLOWS = {
        "lead_qualification": LeadQualificationFlow,
        "founder_discovery": FounderDiscoveryFlow,
        "business_launch": BusinessLaunchDiscoveryFlow,
        "product_recommendation": ProductRecommendationFlow,
    }
    
    async def greet_visitor(self, session_id: str, visitor_context: dict):
        """Proactive greeting based on visitor context"""
        flow = self._select_flow(visitor_context)
        greeting = self._generate_greeting(flow, visitor_context)
        return await self.voice_agent.text_to_speech_stream(greeting)
    
    async def execute_flow(self, flow_name: str, session_id: str, context: dict):
        flow_class = self.FLOWS.get(flow_name)
        if not flow_class:
            raise ValueError(f"Unknown flow: {flow_name}")
        flow = flow_class(self)
        return await flow.execute(session_id, context)
```

### Flow Implementations

**lead_qualification.py**
```python
class LeadQualificationFlow:
    async def execute(self, agent, session_id, context):
        # Identify
        await agent.say("What brings you to Genesis today?")
        # Qualify
        company = await agent.ask("What's your company stage?")
        team_size = await agent.ask("How many people on your team?")
        challenges = await agent.ask("What's your biggest challenge right now?")
        # Route
        if team_size <= 5:
            return await agent.route_to("self_serve_onboarding")
        return await agent.route_to("assisted_onboarding")
```

**founder_discovery.py**
```python
class FounderDiscoveryFlow:
    async def execute(self, agent, session_id, context):
        vision = await agent.ask("What's your vision for this business?")
        constraints = await agent.ask("What constraints are you working with?")
        timeline = await agent.ask("What's your ideal timeline?")
        budget = await agent.ask("What's your budget range?")
        return FounderProfile(vision, constraints, timeline, budget)
```

**business_launch.py**
```python
class BusinessLaunchDiscoveryFlow:
    async def execute(self, agent, session_id, context):
        idea = await agent.ask("Describe your business idea in one sentence.")
        market = await agent.ask("Who's your target market?")
        competition = await agent.ask("Who are your main competitors?")
        return LaunchReadinessScore(idea, market, competition)
```

---

## 3. Onboarding Agent (StrategyAgent Specialization — 80% Reuse)

**File**: `core/agents/onboarding/onboarding_agent.py`

```python
class OnboardingAgent(StrategyAgent):
    """Voice-guided multi-step onboarding"""
    
    STEPS = [
        "welcome",
        "business_profile", 
        "goals",
        "voice_setup",
        "launch"
    ]
    
    async def start_onboarding(self, session_id: str, visitor_context: dict):
        self.current_step = 0
        await self.execute_step(self.STEPS[0], session_id, visitor_context)
    
    async def execute_step(self, step_name: str, session_id: str, context: dict):
        step_method = getattr(self, f"_step_{step_name}")
        return await step_method(session_id, context)
    
    async def _step_welcome(self, session_id, context):
        greeting = "Welcome to Genesis. I'll help you launch your business in minutes."
        await self.say(greeting)
        return await self.next_step(session_id)
    
    async def _step_business_profile(self, session_id, context):
        name = await self.ask("What's your business name?")
        industry = await self.ask("What industry are you in?")
        offer = await self.ask("What's your core offer?")
        return self._save_profile(name, industry, offer)
```

---

## 3. SEO Agent (New Runtime — 100% New Code)

**File**: `core/agents/seo/seo_agent.py`

```python
class SEOAgent(BaseAgent):
    """Technical SEO, programmatic SEO, schema.org, Core Web Vitals"""
    
    async def generate_technical_seo(self, page_type: str, context: dict):
        """Generate technical SEO tags"""
        return {
            "json_ld": self._generate_json_ld(page_type, context),
            "meta_tags": self._generate_meta_tags(page_type, context),
            "canonical": self._generate_canonical(page_type, context),
            "sitemap_entry": self._generate_sitemap_entry(page_type, context)
        }
    
    async def generate_programmatic_pages(self, template: str, data: List[dict]):
        """Generate programmatic SEO pages in bulk"""
        pages = []
        for item in data:
            content = await self._render_template(template, item)
            pages.append({
                "url": self._generate_url(template, item),
                "content": content,
                "schema": self._generate_json_ld(template, item)
            })
        return pages
    
    async def optimize_core_web_vitals(self, page_metrics: dict):
        """Analyze and recommend CWV improvements"""
        return CWVOptimizationReport(
            lcp=self._analyze_lcp(page_metrics),
            fid=self._analyze_fid(page_metrics),
            cls=self._analyze_cls(page_metrics),
            inp=self._analyze_inp(page_metrics)
        )
```

---

## 4. Content Agent (BuilderAgent Specialization — 75% Reuse)

**File**: `core/agents/content/content_agent.py`

```python
class ContentAgent(BuilderAgent):
    """Programmatic content generation: landing, industry pages, use cases, glossary"""
    
    async def generate_landing_copy(self, template: str, context: dict):
        return await self.generate(
            prompt=f"Write high-converting landing page copy for {context}",
            template=template
        )
    
    async def generate_programmatic_pages(self, template: str, data: List[dict]):
        """Generate 420+ programmatic pages in parallel"""
        tasks = [self._render_page(template, item) for item in data]
        return await asyncio.gather(*tasks)
    
    async def _render_page(self, template: str, data: dict):
        content = await self.generate(
            prompt=f"Generate {template} page for {data}",
            output_format="markdown+schema"
        )
        return Page(url=self._generate_url(template, data), content=content, schema=data.get("schema"))
```

---

## 4. Growth Agent (StrategyAgent Specialization — 85% Reuse)

**File**: `core/agents/growth/growth_agent.py`

```python
class GrowthAgent(StrategyAgent):
    """Funnel optimization, referral loops, expansion revenue"""
    
    async def optimize_conversion_funnel(self, funnel_data: dict):
        """Analyze and optimize conversion funnel"""
        analysis = await self.analyze(funnel_data)
        return GrowthRecommendations(
            traffic_optimization=analysis.traffic,
            conversion_optimization=analysis.conversion,
            retention_optimization=analysis.retention,
            expansion_optimization=analysis.expansion
        )
    
    async def generate_referral_program(self, customer_data: dict):
        return ReferralProgram(
            incentive=self._design_referral_incentive(customer_data),
            tracking=self._setup_referral_tracking(customer_data)
        )
```

---

## 5. Voice Analytics

**File**: `core/agents/voice/voice_analytics.py`

```python
class VoiceAnalytics:
    def track_session(self, session_id: str, event: VoiceEvent):
        metrics = {
            "session_duration": event.duration,
            "turn_count": event.turns,
            "interruptions": event.interruptions,
            "barge_in_rate": event.barge_ins / event.turns,
            "sentiment": event.sentiment,
            "conversion": event.converted,
            "conversion_value": event.value
        }
        return VoiceMetrics(metrics)
    
    def track_conversion(self, session_id: str, value: float):
        return ConversionEvent(session_id=session_id, value=value, timestamp=now())
```

---

## Parallel Execution Map

| Agent | Base | Reuse | Can Start | Parallel |
|-------|------|-------|-----------|----------|
| VoiceAgent | OutreachAgent | 85% | **Immediate** | ✅ |
| VoiceOrchestrator | TaskRouter | 90% | **Immediate** | ✅ |
| VoiceSessionManager | Scheduler | 80% | **Immediate** | ✅ |
| ConversationMemoryAdapter | LongTermMemory | 85% | **Immediate** | ✅ |
| ElevenLabsClient | New | 0% | **Immediate** | ✅ |
| VoiceAnalytics | New | 0% | **Immediate** | ✅ |
| LandingAgent | StrategyAgent | 80% | After VoiceAgent | ✅ |
| OnboardingAgent | StrategyAgent | 80% | After VoiceAgent | ✅ |
| SEOAgent | BaseAgent | 0% | **Immediate** | ✅ |
| ContentAgent | BuilderAgent | 75% | **Immediate** | ✅ |
| GrowthAgent | StrategyAgent | 85% | **Immediate** | ✅ |

---

## Files Summary

### New Files (22)
```
core/agents/voice/voice_agent.py
core/orchestration/voice_orchestrator.py
core/orchestration/voice_session_manager.py
core/memory/conversation_memory_adapter.py
core/integrations/elevenlabs/elevenlabs_client.py
core/integrations/elevenlabs/__init__.py
core/integrations/__init__.py
core/agents/voice/__init__.py
core/agents/voice/voice_analytics.py
core/agents/voice/__init__.py
core/agents/landing/landing_agent.py
core/agents/landing/flows/__init__.py
core/agents/landing/flows/lead_qualification.py
core/agents/landing/flows/founder_discovery.py
core/agents/landing/flows/business_launch.py
core/agents/landing/flows/product_recommendation.py
core/agents/onboarding/onboarding_agent.py
core/agents/seo/seo_agent.py
core/agents/content/content_agent.py
core/agents/growth/growth_agent.py
core/agents/voice/voice_analytics.py
```

### Extended Files (6)
```
core/agents/outreach/outreach_agent.py          # +VoiceAgent methods
core/orchestration/task_router.py               # Voice routing
core/orchestration/scheduler.py                 # Voice session lifecycle
core/memory/long_term_memory/long_term_memory.py # Namespace support
core/agents/base_agent.py                       # Voice capabilities
core/agents/__init__.py                         # Export VoiceAgent
```

### Frontend New Files (10)
```
frontend/src/components/voice/VoiceOrb.tsx
frontend/src/components/voice/VoiceWaveform.tsx
frontend/src/components/voice/VoiceControls.tsx
frontend/src/components/voice/VoiceSession.tsx
frontend/src/components/voice/VoiceTranscript.tsx
frontend/src/hooks/use-voice-session.ts
frontend/src/components/landing/VoiceLandingAgent.tsx
frontend/src/components/landing/VoiceGreeting.tsx
frontend/src/components/onboarding/OnboardingWizard.tsx
frontend/src/hooks/use-voice-analytics.ts
```

---

## Acceptance Criteria

| Component | Criteria |
|-----------|----------|
| VoiceAgent | Handles STT→LLM→TTS pipeline, barge-in <100ms, session resume |
| VoiceOrchestrator | Routes intents, handles barge-in, manages streams |
| VoiceSessionManager | Creates/resumes/cleans sessions, 30min timeout |
| ConversationMemoryAdapter | Stores turns with audio metadata, windowed context, full resumption |
| ElevenLabsClient | TTS streaming <200ms first-byte, STT real-time, conversation persistence |
| LandingAgent | 4 flows execute, proactive greeting triggers work |
| OnboardingAgent | 5 voice steps complete, voice-guided wizard |
| SEOAgent | Generates technical SEO, 420 programmatic pages, schema |
| ContentAgent | Generates landing copy, 420 programmatic pages |
| GrowthAgent | Funnel optimization, referral program generation |
| VoiceAnalytics | Tracks engagement, barge-in rate, conversion, sentiment |

---

## Tests Required

- `tests/unit/test_voice_agent.py` — STT/TTS pipeline, barge-in, session resume
- `tests/unit/test_voice_orchestrator.py` — Routing, barge-in handling, stream management
- `tests/unit/test_conversation_memory.py` — Store/get/resume context
- `tests/unit/test_elevenlabs_client.py` — TTS streaming, STT, conversation creation
- `tests/unit/test_landing_agent.py` — 4 flows, greeting triggers
- `tests/unit/test_onboarding_agent.py` — 5 steps, voice guidance
- `tests/unit/test_seo_agent.py` — Technical SEO, 420 pages, schema
- `tests/unit/test_content_agent.py` — Programmatic generation
- `tests/unit/test_growth_agent.py` — Funnel optimization, referrals

---

## Definition of Done

- [ ] VoiceAgent handles full duplex conversation with barge-in <100ms
- [ ] VoiceOrchestrator routes all intents, cancels TTS on interruption
- [ ] VoiceSessionManager manages session lifecycle with resume
- [ ] ConversationMemoryAdapter stores/retrieves with audio metadata
- [ ] ElevenLabsClient streams TTS <200ms first-byte, STT real-time
- [ ] LandingAgent executes all 4 flows with voice greetings
- [ ] OnboardingAgent guides 5 voice steps to completion
- [ ] SEOAgent generates 420 programmatic pages + technical SEO
- [ ] ContentAgent generates landing copy + programmatic content
- [ ] GrowthAgent produces funnel optimization + referral programs
- [ ] All voice components integrated on landing page
- [ ] All tests passing