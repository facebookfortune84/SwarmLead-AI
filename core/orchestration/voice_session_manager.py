"""
Voice Session Manager - Scheduler extension for voice session lifecycle.

Constitutional: Extends Scheduler with voice session management.
Reuses 80% of Scheduler codebase.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

from core.memory.conversation_memory_adapter import ConversationMemoryAdapter
from core.orchestration.scheduler import Scheduler

logger = logging.getLogger(__name__)


class VoiceSessionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    EXPIRED = "expired"


@dataclass
class VoiceSession:
    """Voice session data."""

    session_id: str
    visitor_id: str
    greeting_type: str
    tenant_id: Optional[str] = None
    status: VoiceSessionStatus = VoiceSessionStatus.CREATED
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_activity: datetime = field(default_factory=datetime.utcnow)
    turn_count: int = 0
    barge_in_count: int = 0
    context: Dict = field(default_factory=dict)
    elevenlabs_conversation_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class VoiceSessionManager(Scheduler):
    """
    Voice Session Manager - extends Scheduler for voice session lifecycle.

    Inherits scheduling capabilities, adds voice-specific session management.
    """

    def __init__(
        self, memory_adapter: ConversationMemoryAdapter, default_timeout_minutes: int = 30
    ):
        super().__init__()
        self.memory_adapter = memory_adapter
        self.default_timeout_minutes = default_timeout_minutes
        self._sessions: Dict[str, VoiceSession] = {}
        self._visitor_sessions: Dict[str, List[str]] = {}  # visitor_id -> session_ids
        self._cleanup_task = None
        self._running = False

    async def start(self, interval_seconds: int = 60):
        """Start session manager with cleanup loop."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop(interval_seconds))
        logger.info("VoiceSessionManager started")

    async def stop(self):
        """Stop session manager."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def create_session(
        self,
        visitor_id: str,
        greeting_type: str = "proactive",
        tenant_id: Optional[str] = None,
        timeout_minutes: Optional[int] = None,
    ) -> VoiceSession:
        """Create a new voice session."""
        f"voice_{uuid.uuid4().hex[:12]}"
        timeout = timeout_minutes or self.default_timeout_minutes

        session = VoiceSession(
            session_id=f"voice_{uuid.uuid4().hex[:12]}",
            visitor_id=visitor_id,
            greeting_type=greeting_type,
            tenant_id=tenant_id,
            expires_at=datetime.utcnow()
            + timedelta(minutes=timeout or self.default_timeout_minutes),
            context={"greeting_type": greeting_type},
        )

        self._sessions[session.session_id] = session

        # Index by visitor
        if visitor_id not in self._visitor_sessions:
            self._visitor_sessions[visitor_id] = []
        self._visitor_sessions[visitor_id].append(session.session_id)

        # Initialize memory context
        await self.memory_adapter.store_turn(
            session_id=session.session_id,
            role="system",
            text=f"Voice session started with {greeting_type} greeting",
            metadata={"type": "session_start", "greeting_type": greeting_type},
        )

        logger.info(f"Created voice session: {session.session_id} for visitor {visitor_id}")
        return session

    async def get_session(self, session_id: str) -> Optional[VoiceSession]:
        """Get voice session by ID."""
        session = self._sessions.get(session_id)
        if session and session.expires_at and session.expires_at < datetime.utcnow():
            # Session expired
            await self.end_session(session_id)
            return None
        return session

    async def get_sessions_by_visitor(self, visitor_id: str) -> List[VoiceSession]:
        """Get all sessions for a visitor."""
        session_ids = self._visitor_sessions.get(visitor_id, [])
        return [self._sessions[sid] for sid in session_ids if sid in self._sessions]

    async def get_session_by_visitor(self, visitor_id: str) -> Optional[VoiceSession]:
        """Get active session for visitor."""
        sessions = await self.get_sessions_by_visitor(visitor_id)
        active = [s for s in sessions if s.status == VoiceSessionStatus.ACTIVE]
        return active[0] if active else None

    async def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session fields."""
        session = await self.get_session(session_id)
        if not session:
            return False

        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.last_activity = datetime.utcnow()
        return True

    async def add_turn(
        self, session_id: str, role: str, text: str, audio_meta: Dict = None
    ) -> bool:
        """Add a conversation turn to session."""
        session = await self.get_session(session_id)
        if not session:
            return False

        session.turn_count += 1
        session.last_activity = datetime.utcnow()

        # Store in memory adapter
        await self.memory_adapter.store_turn(
            session_id=session_id, role=role, text=text, audio_meta=audio_meta or {}
        )

        return True

    async def record_barge_in(self, session_id: str) -> bool:
        """Record barge-in event."""
        session = await self.get_session(session_id)
        if not session:
            return False

        session.barge_in_count += 1
        return True

    async def end_session(self, session_id: str, reason: str = "ended") -> bool:
        """End voice session."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.status = VoiceSessionStatus.ENDED
        session.context["end_reason"] = reason
        session.context["ended_at"] = datetime.utcnow().isoformat()

        # Store final summary in memory
        await self.memory_adapter.store_turn(
            session_id=session_id,
            role="system",
            text=f"Voice session ended: {reason}",
            metadata={"type": "session_end", "reason": reason},
        )

        logger.info(f"Ended voice session: {session_id}, reason: {reason}")
        return True

    async def _cleanup_loop(self, interval: int = 60):
        """Periodic cleanup of expired sessions."""
        while self._running:
            try:
                await self._cleanup_expired()
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
            await asyncio.sleep(interval)

    async def _cleanup_expired(self) -> int:
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired = [
            sid
            for sid, session in self._sessions.items()
            if session.expires_at and session.expires_at < now
        ]

        count = 0
        for sid in expired:
            session = self._sessions[sid]
            session.status = VoiceSessionStatus.EXPIRED
            logger.info(f"Expired session: {sid}")
            count += 1

        return count


# Export
__all__ = ["VoiceSessionManager", "VoiceSession", "VoiceSessionStatus"]
