"""
Voice Analytics

Tracks and analyzes voice session metrics for optimization.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.monitoring.metrics_collector import (
    record_voice_session,
    voice_barge_in_latency,
)


@dataclass
class VoiceSessionMetrics:
    """Metrics for a single voice session."""

    session_id: str
    visitor_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: float = 0
    turn_count: int = 0
    barge_in_count: int = 0
    avg_latency_ms: float = 0
    stt_latency_ms: float = 0
    tts_latency_ms: float = 0
    llm_latency_ms: float = 0
    interruptions: int = 0
    conversion: bool = False
    conversion_value: float = 0.0
    errors: List[str] = field(default_factory=list)


class VoiceAnalytics:
    """
    Voice session analytics and metrics collection.

    Tracks:
    - Session duration and engagement
    - Voice quality metrics (latency, barge-in)
    - Conversion tracking
    - Error tracking
    """

    def __init__(self):
        self._sessions: Dict[str, VoiceSessionMetrics] = {}
        self._visitor_sessions: Dict[str, List[str]] = defaultdict(list)
        self._aggregates: Dict[str, Dict] = defaultdict(lambda: defaultdict(int))

    def start_session(self, session_id: str, visitor_id: str) -> VoiceSessionMetrics:
        """Start tracking a voice session."""
        metrics = VoiceSessionMetrics(
            session_id=session_id, visitor_id=visitor_id, started_at=datetime.now(timezone.utc)
        )
        self._sessions[session_id] = metrics
        self._visitor_sessions[visitor_id].append(session_id)
        return metrics

    def end_session(
        self, session_id: str, conversion: bool = False, conversion_value: float = 0.0
    ) -> Optional[VoiceSessionMetrics]:
        """End session and record final metrics."""
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]
        session.ended_at = datetime.now(timezone.utc)
        session.duration_seconds = (session.ended_at - session.started_at).total_seconds()
        session.conversion = conversion
        session.conversion_value = conversion_value

        record_voice_session(status="completed")

        return session

    def record_turn(
        self, session_id: str, latency_ms: float = 0, stt_ms: float = 0, tts_ms: float = 0
    ):
        """Record a conversation turn."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.turn_count += 1

            # Update rolling average latency
            n = session.turn_count
            session.avg_latency_ms = ((session.avg_latency_ms * (n - 1)) + latency_ms) / n

    def record_barge_in(self, session_id: str, latency_ms: float = 0):
        """Record barge-in event."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.barge_in_count += 1
            session.interruptions += 1
            voice_barge_in_latency.observe(latency_ms / 1000)

            # Update aggregate
            self._aggregates["barge_in"]["total"] += 1

    def record_error(self, session_id: str, error: str):
        """Record an error in session."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.errors.append(f"{datetime.now(timezone.utc).isoformat()}: {error}")

    def record_stt_latency(self, session_id: str, latency_ms: float):
        """Record STT latency."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.stt_latency_ms = latency_ms

    def record_tts_latency(self, session_id: str, latency_ms: float):
        """Record TTS latency."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.tts_latency_ms = latency_ms

    def record_llm_latency(self, session_id: str, latency_ms: float):
        """Record LLM latency."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.llm_latency_ms = latency_ms

    def record_conversion(self, session_id: str, value: float):
        """Record conversion."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.conversion = True
            session.conversion_value = value

    def get_session(self, session_id: str) -> Optional[VoiceSessionMetrics]:
        """Get session metrics."""
        return self._sessions.get(session_id)

    def get_visitor_sessions(self, visitor_id: str) -> List[str]:
        """Get all sessions for a visitor."""
        return self._visitor_sessions.get(visitor_id, [])

    def get_aggregate_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics."""
        len(self._sessions)
        completed = sum(1 for s in self._sessions.values() if s.ended_at)
        converted = sum(1 for s in self._sessions.values() if s.conversion)

        avg_duration = 0
        if completed > 0:
            avg_duration = (
                sum(s.duration_seconds for s in self._sessions.values() if s.ended_at) / completed
            )

        return {
            "total_sessions": len(self._sessions),
            "completed_sessions": completed,
            "conversion_rate": converted / completed if completed > 0 else 0,
            "avg_duration_seconds": avg_duration,
            "total_barge_ins": sum(s.barge_in_count for s in self._sessions.values()),
            "avg_turns_per_session": sum(s.turn_count for s in self._sessions.values())
            / len(self._sessions)
            if self._sessions
            else 0,
        }


# Global instance
voice_analytics = VoiceAnalytics()

__all__ = ["VoiceAnalytics", "VoiceSessionMetrics", "voice_analytics"]
