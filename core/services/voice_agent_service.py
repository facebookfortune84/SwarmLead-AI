"""
Voice Agent Service - powers the landing page voice assistant.

Full-duplex conversational loop:
- create_session() -> greeting text + audio
- process_message() -> reply text + audio (guided conversation)

Graceful degradation:
- If ElevenLabs TTS fails, returns text only (frontend falls back to
  browser speech synthesis).
- If Ollama is unreachable, returns a scripted guided response so the
  conversation always stays on track.
"""

import base64
import logging
import uuid
from typing import Any, Dict, Optional

from core.integrations.elevenlabs.elevenlabs_client import ElevenLabsClient
from core.models.local_llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Genesis voice assistant, a friendly and confident launch guide for \
Genesis, the first autonomous business launch platform powered by constitutional voice AI.

Your job is to lead a live, voice-first conversation that guides the visitor step by step:
1. WELCOME: Greet warmly and briefly, then ask what brings them here today.
2. DISCOVER: Ask about their business - what it is, who it serves, and their top goal.
3. QUALIFY: Ask 1-2 light questions (budget range, timeline) - keep it casual, never interrogate.
4. RECOMMEND: Based on their answers recommend the right plan:
   - Starter ($49/mo): solo founders validating an idea.
   - Growth ($149/mo): small teams ready to scale outreach.
   - Enterprise ($499/mo): established companies needing unlimited tenants and voice runtime.
5. GUIDE: Direct them to action - create a free account, complete onboarding, or make a payment.

CONVERSATION RULES:
- Respond in 1-3 short spoken sentences. Be warm, concise, and human.
- Never dump features or pricing tables. Keep it conversational.
- If they ask to "qualify leads", explain Genesis qualifies inbound leads automatically.
- If they ask to "launch a business", start the launch discovery flow.
- If they mention pricing/payment/plans, recommend the best plan and direct them to the \
pricing section or to create an account.
- If they want to sign up, encourage them to click "Launch Your Business" or "Get Started" \
to begin onboarding.
- Stay on brand: Genesis helps people launch and grow businesses with AI agents.
"""

SCRIPTED_REPLY = (
    "I'd love to help you with that. Genesis can launch and run your business with AI agents - "
    "from lead qualification to outreach. Let's get you set up - go ahead and click Launch Your "
    "Business to begin your onboarding, or ask me about pricing."
)

GREETINGS = {
    "proactive": "Hi there! Welcome to Genesis. I'm your launch assistant. We help people start "
    "and grow real businesses using AI agents. What brings you here today - are you looking to "
    "qualify more leads, or launch a business?",
    "scroll": "I noticed you're exploring our features. Genesis can automate your entire customer "
    "acquisition - from inbound leads to follow-up. What's the biggest thing you want to automate?",
    "exit_intent": "Before you go - Genesis could be launching your business within the hour. "
    "Would you like me to walk you through how it works?",
    "voice": "Hey there! Great to meet you. I'm your voice launch guide. Tell me a little about "
    "the business you want to build, and I'll point you in the right direction.",
}


class VoiceAgentService:
    """Conversational voice assistant powering the landing page."""

    def __init__(self) -> None:
        self._llm = OllamaClient()
        self._elevenlabs = ElevenLabsClient()
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._session_limit = 2000

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    async def create_session(self, greeting_type: str = "proactive") -> Dict[str, Any]:
        """Create a session and return the greeting (text + audio)."""
        session_id = f"voice_{uuid.uuid4().hex[:12]}"
        greeting = GREETINGS.get(greeting_type, GREETINGS["proactive"])
        self._sessions[session_id] = {
            "visitor_id": f"visitor_{uuid.uuid4().hex[:12]}",
            "greeting_type": greeting_type,
            "history": [],
            "context": {"intent": None, "recommended_plan": None},
        }

        if len(self._sessions) > self._session_limit:
            self._evict_oldest()

        return {
            "session_id": session_id,
            "visitor_id": self._sessions[session_id]["visitor_id"],
            "greeting": greeting,
            "greeting_audio_b64": await self._synthesize(greeting),
        }

    def end_session(self, session_id: str) -> bool:
        """Remove a session (privacy / cleanup)."""
        return self._sessions.pop(session_id, None) is not None

    # ------------------------------------------------------------------
    # Conversation
    # ------------------------------------------------------------------

    async def process_message(self, session_id: str, user_text: str) -> Dict[str, Any]:
        """Process user input and return a guided reply (text + audio)."""
        session = self._sessions.get(session_id)
        if session is None:
            created = self.create_session("voice")
            session = self._sessions[created["session_id"]]
            session_id = created["session_id"]

        history = session["history"]
        history.append({"role": "user", "content": user_text})

        try:
            reply = await self._generate_reply(session_id, history)
        except Exception as exc:
            logger.warning("LLM reply failed for %s: %s", session_id, exc)
            reply = SCRIPTED_REPLY

        history.append({"role": "assistant", "content": reply})

        intent = self._detect_intent(user_text)

        return {
            "session_id": session_id,
            "reply": reply,
            "reply_audio_b64": await self._synthesize(reply),
            "intent": intent,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _generate_reply(self, session_id: str, history: list) -> str:
        """Build a guided prompt and call the LLM."""
        transcript = "\n".join(
            f"{'User' if turn['role'] == 'user' else 'Assistant'}: {turn['content']}"
            for turn in history[-12:]
        )

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            "Here is the conversation so far (most recent last):\n"
            f"{transcript}\n\n"
            "Reply now as the assistant, continuing the conversation and steering toward "
            "creating an account / onboarding / payment when appropriate:"
        )

        result = await self._llm.generate(prompt=prompt)
        reply = (result.get("response") or "").strip()
        if not reply:
            reply = SCRIPTED_REPLY
        return reply[:600]

    async def _synthesize(self, text: str) -> Optional[str]:
        """Synthesize speech to base64 mp3. Returns None on failure."""
        try:
            audio = await self._elevenlabs.text_to_speech_bytes(text)
            if audio:
                return base64.b64encode(audio).decode("ascii")
        except Exception as exc:
            logger.warning("TTS failed: %s", exc)
        return None

    def _detect_intent(self, text: str) -> str:
        """Detect the visitor's intent from their message."""
        lower = text.lower()
        if any(k in lower for k in ["pay", "pricing", "price", "plan", "cost", "billing", "subscribe"]):
            return "pricing"
        if any(k in lower for k in ["sign up", "register", "create account", "get started", "start"]):
            return "onboarding"
        if any(k in lower for k in ["qualify", "lead"]):
            return "qualify"
        if any(k in lower for k in ["launch", "business", "startup", "incorporate", "start a"]):
            return "launch"
        return "general"

    def _evict_oldest(self) -> None:
        """Evict the oldest session when over the limit."""
        first_key = next(iter(self._sessions))
        self._sessions.pop(first_key, None)


voice_agent_service = VoiceAgentService()
__all__ = ["VoiceAgentService", "voice_agent_service"]
