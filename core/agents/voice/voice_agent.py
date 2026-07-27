"""
Voice Agent - OutreachAgent specialization for voice interactions.

Constitutional: Extends OutreachAgent with voice capabilities.
Reuses 85% of OutreachAgent codebase.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from core.agents.outreach.outreach_agent import OutreachAgent
from core.integrations.elevenlabs.elevenlabs_client import ElevenLabsClient, STTResult
from core.memory.conversation_memory_adapter import ConversationMemoryAdapter

logger = logging.getLogger(__name__)


class VoiceAgent(OutreachAgent):
    """
    Voice-enabled agent for real-time voice conversations.
    
    Extends OutreachAgent with:
    - Speech-to-Text via ElevenLabs
    - Text-to-Speech streaming via ElevenLabs
    - Barge-in support (interruption handling)
    - Session context persistence
    """
    
    def __init__(
        self,
        name: str,
        config,
        elevenlabs_client: ElevenLabsClient,
        memory_adapter: Optional[ConversationMemoryAdapter] = None
    ):
        super().__init__(name, config)
        self.elevenlabs = elevenlabs_client
        self.memory_adapter = memory_adapter or ConversationMemoryAdapter()
        self._active_streams: Dict[str, asyncio.Queue] = {}
    
    async def text_to_speech(
        self,
        text: str,
    ) -> Optional[bytes]:
        """
        Generate audio bytes from text via ElevenLabs TTS.

        Graceful degradation:
        - On TTS failure, logs error and returns None
        - Caller should use text response as fallback
        """
        try:
            return await self.elevenlabs.text_to_speech_bytes(text)
        except Exception as exc:
            logger.error("TTS failed for text '%s': %s", text[:50], exc)
            return None

    async def process_voice_input(
        self,
        audio_stream: bytes,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[bytes, None]:
        """
        Process voice input and stream TTS response.
        
        Pipeline:
        1. STT via ElevenLabs
        2. Process through existing LLM pipeline (reuse parent logic)
        3. TTS via ElevenLabs streaming
        4. Return audio stream

        Graceful degradation:
        - If STT fails, uses empty text and continues
        - If TTS fails, yields response text as UTF-8 bytes
        """
        context = context or {}
        context["session_id"] = session_id

        try:
            stt_result = await self.elevenlabs.speech_to_text(audio_stream)
            user_text = stt_result.text
            logger.info("STT result: %s", user_text[:100])
        except Exception as exc:
            logger.error("STT failed: %s", exc)
            user_text = ""

        context["voice_mode"] = True

        history = self.memory_adapter.get_context(session_id, window=10)
        context["history"] = history

        response_text = await self._process_with_voice_context(user_text, context)

        await self.memory_adapter.store_turn(
            session_id=session_id,
            role="user",
            text=user_text,
            audio_meta={"duration": len(audio_stream)}
        )
        await self.memory_adapter.store_turn(
            session_id=session_id,
            role="assistant",
            text=response_text,
            audio_meta={}
        )

        try:
            async for chunk in self.elevenlabs.text_to_speech_stream(response_text):
                yield chunk
        except Exception as exc:
            logger.error("TTS streaming failed: %s", exc)
            yield response_text.encode("utf-8")
    
    async def _process_with_voice_context(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> str:
        """Process text through existing LLM pipeline with voice context."""
        input_data = {
            "text": text,
            "voice_mode": True,
            "session_id": context.get("session_id"),
            "history": context.get("history", [])
        }
        
        result = await self.execute(input_data, context, trace_id=uuid.uuid4().hex)
        
        if result.get("success"):
            return result.get("result", {}).get("response", "I understand. Let me help you with that.")
        return "I understand. Let me help you with that."
    
    async def handle_interruption(
        self,
        session_id: str,
        interruption_audio: bytes
    ) -> AsyncGenerator[bytes, None]:
        """
        Handle barge-in interruption.

        Graceful degradation:
        - If STT fails, uses empty text
        - If TTS fails, yields response text as UTF-8 bytes
        """
        try:
            stt_result = await self.elevenlabs.speech_to_text(interruption_audio)
            user_text = stt_result.text
        except Exception as exc:
            logger.error("Interruption STT failed: %s", exc)
            user_text = ""

        response_text = await self._process_with_voice_context(
            user_text,
            {"interruption": True, "session_id": session_id}
        )

        try:
            async for chunk in self.elevenlabs.text_to_speech_stream(response_text):
                yield chunk
        except Exception as exc:
            logger.error("Interruption TTS failed: %s", exc)
            yield response_text.encode("utf-8")
    
    async def maintain_session_context(self, session_id: str) -> Dict[str, Any]:
        """Maintain session context for resumption."""
        return self.memory_adapter.resume_session(session_id)
    
    async def handle_session_resume(self, session_id: str) -> AsyncGenerator[bytes, None]:
        """
        Resume a paused voice session.

        Graceful degradation:
        - If TTS fails, yields greeting text as UTF-8 bytes
        """
        session_data = self.memory_adapter.resume_session(session_id)

        greeting = f"Welcome back! You were asking about {session_data.get('context', 'your business')}. How can I continue helping?"

        try:
            async for chunk in self.elevenlabs.text_to_speech_stream(greeting):
                yield chunk
        except Exception as exc:
            logger.error("Resume TTS failed: %s", exc)
            yield greeting.encode("utf-8")
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get session statistics."""
        return self.memory_adapter.get_session_stats(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear session data (for privacy/GDPR)."""
        return self.memory_adapter.clear_session(session_id)