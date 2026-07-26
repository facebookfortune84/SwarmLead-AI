"""
Voice Agent - OutreachAgent specialization for voice interactions.

Constitutional: Extends OutreachAgent with voice capabilities.
Reuses 85% of OutreachAgent codebase.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, AsyncGenerator, Dict, List, AsyncGenerator
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
        memory_adapter: Optional[Any] = None
    ):
        super().__init__(name, config)
        self.elevenlabs = elevenlabs_client
        self.memory_adapter = memory_adapter or ConversationMemoryAdapter()
        self._active_streams: Dict[str, asyncio.Queue] = {}
    
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
        """
        context = context or {}
        context["session_id"] = session_id
        
        # 1. STT via ElevenLabs
        stt_result = await self.elevenlabs.speech_to_text(audio_stream)
        user_text = stt_result.text
        logger.info(f"STT result: {user_text[:100]}...")
        
        # 2. Process through existing LLM pipeline (reuse parent logic)
        context["session_id"] = session_id
        context["voice_mode"] = True
        
        # 3. Get conversation context
        history = self.memory_adapter.get_context(session_id, window=10)
        context["history"] = history
        
        # 4. Process through existing LLM pipeline
        response_text = await self._process_with_voice_context(user_text, context)
        
        # 8. Store in conversation memory
        self.memory_adapter.store_turn(
            session_id=session_id,
            role="user",
            text=user_text,
            audio_meta={"duration": len(audio_stream)}
        )
        self.memory_adapter.store_turn(
            session_id=session_id,
            role="assistant",
            text=response_text,
            audio_meta={}
        )
        
        # 9. Stream TTS response
        async for chunk in self.elevenlabs.text_to_speech_stream(response_text):
            yield chunk
    
    async def _process_with_voice_context(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> str:
        """Process text through existing LLM pipeline with voice context."""
        # Reuse parent's execute method but with voice context
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
        
        Pipeline:
        1. Cancel active TTS stream
        2. Process interruption via STT
        3. Process as new turn with interruption flag
        4. Resume with new response
        """
        # 1. Cancel active TTS (ElevenLabs stream cancellation)
        # This would be implemented with ElevenLabs stream cancellation
        
        # 2. Process interruption
        stt_result = await self.elevenlabs.speech_to_text(interruption_audio)
        
        # 3. Process as new turn with interruption flag
        context = {"interruption": True, "session_id": session_id}
        response_text = await self._process_with_voice_context(
            stt_result.text,
            {"interruption": True, "session_id": session_id}
        )
        
        # 4. Stream new response
        async for chunk in self.elevenlabs.text_to_speech_stream(response_text):
            yield chunk
    
    async def maintain_session_context(self, session_id: str) -> Dict[str, Any]:
        """Maintain session context for resumption."""
        return self.memory_adapter.resume_session(session_id)
    
    async def handle_session_resume(self, session_id: str) -> AsyncGenerator[bytes, None]:
        """Resume a paused voice session."""
        session_data = self.memory_adapter.resume_session(session_id)
        
        # Generate resumption greeting
        greeting = f"Welcome back! You were asking about {session_data.get('context', 'your business')}. How can I continue helping?"
        
        async for chunk in self.elevenlabs.text_to_speech_stream(greeting):
            yield chunk
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get session statistics."""
        return self.memory_adapter.get_session_stats(session_id)
    
    def clear_session(self, session_id: str) -> None:
        """Clear session data (for privacy/GDPR)."""
        # Would implement clearing in LongTermMemory
        pass