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

import asyncio
import base64
import logging
import uuid
from typing import Any, Dict, Optional

from core.integrations.elevenlabs.elevenlabs_client import ElevenLabsClient
from core.models.local_llm.ollama_client import OllamaClient
from core.services.product_knowledge import product_knowledge

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
- Use the RETRIEVED KNOWLEDGE sections below to answer "how do I use Genesis" and
  "how do I run my business" questions with real, specific guidance from the docs.
- If the question is not covered by the retrieved knowledge, steer them to the
  right part of Genesis (onboarding, agents, workflows, outreach, tickets, voice)
  or to creating an account rather than guessing.
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

    def __init__(self, llm_timeout_s: int = 25) -> None:
        self._llm = OllamaClient()
        self._elevenlabs = ElevenLabsClient()
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._session_limit = 2000
        # Hard cap on LLM generation for voice. This hardware (CPU-only) can take
        # minutes per generation; the cap keeps the agent responsive via the
        # scripted fallback. Raise it when a fast hosted model is wired up.
        self._llm_timeout_s = llm_timeout_s

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
        """Build a guided prompt and call the LLM, grounding it in the docs.

        The LLM call is hard-capped: on this hardware a full generation can take
        minutes, which reads as a frozen agent. If it exceeds ``_llm_timeout_s``
        we return an intent-matched scripted reply so the conversation always
        stays responsive. Swap to a fast hosted model (Groq/cloud GPU) and the
        cap simply stops being hit.
        """
        transcript = "\n".join(
            f"{'User' if turn['role'] == 'user' else 'Assistant'}: {turn['content']}"
            for turn in history[-12:]
        )

        last_user = next(
            (turn["content"] for turn in reversed(history) if turn["role"] == "user"),
            "",
        )
        # Bounded knowledge slice — keep the prompt small so the voice reply stays fast.
        knowledge = product_knowledge.format_context(last_user, max_chars=900, top_k=2)

        knowledge_block = (
            "\nRETRIEVED KNOWLEDGE FROM GENESIS DOCS:\n"
            f"{knowledge}\n"
            "Use this to give accurate, concrete guidance about using Genesis.\n"
            if knowledge
            else ""
        )

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"{knowledge_block}"
            "Here is the conversation so far (most recent last):\n"
            f"{transcript}\n\n"
            "Reply now as the assistant, continuing the conversation and steering toward "
            "creating an account / onboarding / payment when appropriate:"
        )

        try:
            result = await asyncio.wait_for(
                self._llm.generate(prompt=prompt, num_predict=120),
                timeout=self._llm_timeout_s,
            )
            reply = (result.get("response") or "").strip()
        except Exception:
            logger.info("Voice LLM capped at %ss — using scripted fallback", self._llm_timeout_s)
            reply = self._scripted_for(last_user)
        if not reply:
            reply = SCRIPTED_REPLY
        return reply[:600]

    @staticmethod
    def _scripted_for(user_text: str) -> str:
        """Fast, intent-relevant fallback so the agent never freezes."""
        lower = user_text.lower()
        if any(k in lower for k in ["company builder", "build", "provision", "launch", "startup", "start a"]):
            return (
                "I can absolutely help you build that. In Genesis, open the Company Builder, describe "
                "your business, and it generates your landing copy, workflows, and launch checklist in "
                "minutes. Sign up free and I'll walk you through it live."
            )
        if any(k in lower for k in ["outreach", "email", "campaign", "lead", "qualif"]):
            return (
                "Great question. Genesis handles that with the Outreach page: pick a template, add your "
                "prospects, and our outreach agent drafts every message for you to review and send. "
                "Inbound leads get qualified automatically and turn into tickets."
            )
        if any(k in lower for k in ["workflow", "automate", "follow-up", "sequence"]):
            return (
                "Workflows are the easy part. Go to the Workflows page, choose a template like Email "
                "Follow-Up or Hot Lead Escalation, and apply it to a lead. It runs automatically and "
                "creates tickets when it needs a human."
            )
        if any(k in lower for k in ["ticket", "support", "handoff", "escalat"]):
            return (
                "You can create a ticket for any lead from the Leads page, or ask the AI to open one. "
                "Tickets route to the right department and show up in the Ticket Center for follow-up."
            )
        if any(k in lower for k in ["price", "plan", "cost", "pay", "pricing"]):
            return (
                "Plans start free at 29 a month for Starter, 99 for Growth, and 299 for Enterprise. "
                "Every plan begins with a free trial, no credit card needed."
            )
        return SCRIPTED_REPLY

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
