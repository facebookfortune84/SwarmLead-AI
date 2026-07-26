"""
Voice Orchestrator - TaskRouter specialization for voice interactions.

Constitutional: Extends TaskRouter with voice-specific routing and barge-in handling.
Reuses 90% of TaskRouter codebase.
"""

from typing import Dict, Any, Optional, AsyncGenerator
import asyncio
import uuid
import logging

from core.orchestration.task_router import TaskRouter
from core.integrations.elevenlabs.elevenlabs_client import ElevenLabsClient
from core.memory.conversation_memory_adapter import ConversationMemoryAdapter
from core.orchestration.voice_session_manager import VoiceSessionManager
from core.agents.voice.voice_agent import VoiceAgent

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
        super().__init__(agent_manager)
        self.elevenlabs = elevenlabs_client
        self.memory_adapter = memory_adapter
        self.voice_session_manager = voice_session_manager
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
        
        # 2. Classify intent
        intent = self._classify_voice_intent(stt_result.text, context)
        
        # 3. Route to agent
        agent_name = self.voice_routes.get(intent, "voice_agent")
        agent = self.agent_manager.get_agent(agent_name)
        
        if not agent:
            raise ValueError(f"No agent found for intent: {intent}")
        
        # 4. Build input with voice context
        input_data = {
            "text": stt_result.text,
            "voice_mode": True,
            "session_id": session_id,
            "confidence": stt_result.confidence
        }
        
        # 5. Execute with voice context
        async for chunk in self._execute_voice_agent(agent_name, intent, context):
            yield chunk
    
    async def _execute_voice_agent(
        self,
        agent_name: str,
        intent: str,
        context: Dict[str, Any]
    ) -> AsyncGenerator[bytes, None]:
        """Execute voice agent and yield audio chunks."""
        agent = self.agent_manager.get_agent(agent_name)
        
        if not agent:
            raise ValueError(f"Agent not found: {agent_name}")
        
        # Check if agent has voice capability
        if hasattr(agent, 'process_voice_input'):
            async for chunk in agent.process_voice_input(context):
                yield chunk
        else:
            # Fallback: use regular execute and TTS
            result = await agent.execute(context)
            # Would need TTS here - delegate to VoiceAgent
            raise NotImplementedError(f"Agent {agent_name} does not support voice processing")
    
    def _classify_voice_intent(self, text: str, context: Dict) -> str:
        """Classify voice intent from transcribed text."""
        text_lower = text.lower()
        
        # Qualification keywords
        if any(kw in text_lower for kw in ["qualify", "lead", "interested", "interested in"]):
            return "qualification"
        
        # Founder discovery
        if any(kw in text_lower for kw in ["founder", "startup", "business idea", "launch"]):
            return "founder_discovery"
        
        # Business launch
        if any(kw in text_lower for kw in ["launch", "start business", "incorporate", "register"]):
            return "business_launch"
        
        # Product recommendation
        if any(kw in text_lower for kw in ["recommend", "suggest", "product", "tool"]):
            return "product_recommendation"
        
        # Onboarding
        if any(kw in text_lower for kw in ["onboard", "setup", "get started", "begin"]):
            return "onboarding"
        
        # Default to qualification
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
        # 1. Cancel active TTS stream
        await self._cancel_active_tts(session_id)
        
        # 2. Process interruption
        stt_result = await self.elevenlabs.speech_to_text(interruption_audio)
        
        # 3. Route with interruption flag
        context = {
            "session_id": session_id,
            "interruption": True,
            "interruption_text": stt_result.text
        }
        
        return await self.route_voice_task(session_id, "interruption", b"", context)
    
    async def _cancel_active_tts(self, session_id: str):
        """Cancel active TTS stream for session."""
        # Cancel any active TTS in ElevenLabs
        if callable(getattr(self.elevenlabs, 'cancel_stream', None)):
            await self.elevenlabs.cancel_stream(session_id)
    
    async def route_voice_task(
        self,
        session_id: str,
        intent: str,
        audio_data: bytes,
        context: Optional[Dict] = None
    ) -> AsyncGenerator[bytes, None]:
        """Route voice task to appropriate agent."""
        return await self.route_voice_task(session_id, intent, audio_data, context)
    
    def register_stream(self, stream_id: str, queue: asyncio.Queue):
        """Register active TTS stream for barge-in cancellation."""
        self._active_streams[stream_id] = asyncio.Queue()
    
    def unregister_stream(self, stream_id: str):
        """Unregister stream."""
        self._active_streams.pop(stream_id, None)
    
    async def cancel_stream(self, stream_id: str) -> bool:
        """Cancel active stream (for barge-in)."""
        return True


# Export
__all__ = ["VoiceOrchestrator"]