"""
Voice Orchestrator - TaskRouter specialization for voice interactions.

Constitutional: Extends TaskRouter with voice-specific routing and barge-in handling.
Reuses 90% of TaskRouter codebase.
"""

from typing import Dict, Any, Optional, AsyncGenerator
import asyncio
import logging

from core.orchestration.task_router import TaskRouter
from core.integrations.elevenlabs.elevenlabs_client import ElevenLabsClient, STTResult
from core.memory.conversation_memory_adapter import ConversationMemoryAdapter
from core.orchestration.voice_session_manager import VoiceSessionManager

logger = logging.getLogger(__name__)


class VoiceOrchestrator(TaskRouter):
    """
    Voice Orchestrator - extends TaskRouter for voice-specific routing.
    
    Adds:
    - Voice session lifecycle management
    - Barge-in handling (interruption)
    - Voice context management
    - Streaming audio routing
    """
    
    def __init__(
        self,
        agent_manager,
        elevenlabs_client: ElevenLabsClient,
        memory_adapter: ConversationMemoryAdapter,
        voice_session_manager: VoiceSessionManager
    ):
        super().__init__()
        self.set_agent_manager(agent_manager)
        self.elevenlabs = elevenlabs_client
        self.memory_adapter = memory_adapter
        self.voice_session_manager = voice_session_manager
        self.voice_routes: Dict[str, str] = {
            "qualification": "voice_agent",
            "founder_discovery": "voice_agent",
            "business_launch": "voice_agent",
            "product_recommendation": "voice_agent",
            "onboarding": "onboarding_agent",
        }
        self._active_streams: Dict[str, asyncio.Queue] = {}
    
    async def route_voice_task(
        self,
        session_id: str,
        intent: str,
        audio_data: bytes,
        context: Optional[Dict] = None
    ) -> AsyncGenerator[bytes, None]:
        """
        Route voice task to appropriate agent.
        
        Pipeline:
        1. STT via ElevenLabs
        2. Intent classification
        3. Route to appropriate agent
        4. Execute with voice context
        5. TTS response
        """
        context = context or {}
        context["session_id"] = session_id
        
        # 1. STT via ElevenLabs
        stt_result = await self.elevenlabs.speech_to_text(audio_data)
        
        # Update context with transcribed text
        context["voice_input"] = stt_result.text
        context["voice_confidence"] = stt_result.confidence
        
        # 2. Classify intent from transcribed text
        classified_intent = self._classify_voice_intent(stt_result.text, context) if not intent or intent == "interruption" else intent
        
        # 3. Route to agent
        agent_name = self.voice_routes.get(classified_intent, "voice_agent")
        agent = self.agent_manager.get_agent(agent_name)
        
        if not agent:
            raise ValueError(f"No agent found for intent: {classified_intent}")
        
        # 4. Build input with voice context
        input_data = {
            "text": stt_result.text,
            "voice_mode": True,
            "session_id": session_id,
            "confidence": stt_result.confidence
        }
        
        # 5. Execute with voice context
        result = await self.agent_manager.execute_agent(
            agent_name=agent_name,
            input_data=input_data,
            context=context,
        )
        
        if not result.get("success"):
            logger.error(f"Voice agent execution failed: {result.get('error')}")
            return
        
        response_text = result.get("result", {}).get("response", "I understand. Let me help you with that.")
        
        # 6. TTS response
        async for chunk in self.elevenlabs.text_to_speech_stream(response_text):
            yield chunk
    
    def _classify_voice_intent(self, text: str, context: Dict) -> str:
        """Classify voice intent from transcribed text."""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["qualify", "lead", "interested", "interested in"]):
            return "qualification"
        
        if any(kw in text_lower for kw in ["founder", "startup", "business idea", "launch"]):
            return "founder_discovery"
        
        if any(kw in text_lower for kw in ["launch", "start business", "incorporate", "register"]):
            return "business_launch"
        
        if any(kw in text_lower for kw in ["recommend", "suggest", "product", "tool"]):
            return "product_recommendation"
        
        if any(kw in text_lower for kw in ["onboard", "setup", "get started", "begin"]):
            return "onboarding"
        
        return "qualification"
    
    async def handle_barge_in(
        self,
        session_id: str,
        interruption_audio: bytes
    ) -> AsyncGenerator[bytes, None]:
        """
        Handle barge-in interruption.
        
        1. Cancel active TTS stream
        2. Process interruption audio
        3. Route as new turn with interruption flag
        """
        await self._cancel_active_tts(session_id)
        
        stt_result = await self.elevenlabs.speech_to_text(interruption_audio)
        
        context = {
            "session_id": session_id,
            "interruption": True,
            "interruption_text": stt_result.text
        }
        
        async for chunk in self.route_voice_task(session_id, "interruption", interruption_audio, context):
            yield chunk
    
    async def _cancel_active_tts(self, session_id: str):
        """Cancel active TTS stream for session."""
        if callable(getattr(self.elevenlabs, 'cancel_stream', None)):
            await self.elevenlabs.cancel_stream(session_id)
    
    def register_stream(self, stream_id: str, queue: asyncio.Queue):
        """Register active TTS stream for barge-in cancellation."""
        self._active_streams[stream_id] = queue
    
    def unregister_stream(self, stream_id: str):
        """Unregister stream."""
        self._active_streams.pop(stream_id, None)
    
    async def cancel_stream(self, stream_id: str) -> bool:
        """Cancel active stream (for barge-in)."""
        queue = self._active_streams.pop(stream_id, None)
        return queue is not None


__all__ = ["VoiceOrchestrator"]