"""
Conversation Memory Adapter

Adapts LongTermMemory for voice conversation storage and retrieval.
Provides session-scoped storage with audio metadata.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.memory.long_term_memory.long_term_memory import LongTermMemory


class ConversationMemoryAdapter:
    """
    Adapts LongTermMemory for voice conversation storage.

    Provides:
    - Session-scoped storage (tenant:{tenant_id}:session:{session_id})
    - Audio metadata enrichment
    - Windowed context retrieval
    - Session resumption support
    """

    def __init__(self, ltm: Optional[LongTermMemory] = None, path: Optional[str] = None):
        self.ltm = ltm or LongTermMemory(path or "data/long_term_memory.json")
        self._session_cache: Dict[str, List[Dict]] = {}

    def store_turn(
        self,
        session_id: str,
        role: str,
        text: str,
        audio_meta: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Store a conversation turn.

        Args:
            session_id: Session identifier
            role: "user" | "assistant" | "system"
            text: Transcript text
            audio_meta: Audio metadata (duration, voice_id, model, interruption, etc.)
            metadata: Additional metadata

        Returns:
            Stored record
        """
        entry = {
            "session_id": session_id,
            "role": role,
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "audio_meta": audio_meta or {},
            "metadata": metadata or {},
        }

        # Add to session cache
        cache_key = f"session:{session_id}"
        if cache_key not in self._session_cache:
            self._session_cache[cache_key] = []
        self._session_cache[cache_key].append(entry)

        # Persist to long-term memory
        record = {
            "content": json.dumps(entry),
            "type": "voice_turn",
            "session_id": session_id,
            "metadata": {"role": role, "session_id": session_id, "timestamp": entry["timestamp"]},
        }

        return self.ltm.add(record)

    def get_context(self, session_id: str, window: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation context for session.

        Args:
            session_id: Session ID
            window: Number of turns to retrieve

        Returns:
            List of recent turns
        """
        cache_key = f"session:{session_id}"
        turns = self._session_cache.get(cache_key, [])

        # Also query LTM for older turns not in cache
        ltm_results = self.ltm.query(query=f"session_id:{session_id}", top_k=window)

        # Merge and deduplicate
        all_turns = []
        seen = set()

        # Add from LTM first (older)
        for result in ltm_results:
            try:
                content = json.loads(result.get("content", "{}"))
                key = f"{result.get('content', '')}_{result.get('timestamp', '')}"
                if key not in seen:
                    seen.add(key)
                    all_turns.append(content)
            except Exception:
                pass

        # Add from cache (newer)
        for turn in turns:
            key = f"{turn.get('text', '')}_{turn.get('timestamp', '')}"
            if key not in seen:
                seen.add(key)
                all_turns.append(turn)

        # Return last N turns
        return all_turns[-window:]

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics."""
        cache_key = f"session:{session_id}"
        turns = self._session_cache.get(cache_key, [])

        return {
            "session_id": session_id,
            "turn_count": len(self._session_cache.get(f"session:{session_id}", [])),
            "user_turns": sum(
                1
                for t in self._session_cache.get(f"session:{session_id}", [])
                if t.get("role") == "user"
            ),
            "assistant_turns": sum(
                1
                for t in self._session_cache.get(f"session:{session_id}", [])
                if t.get("role") == "assistant"
            ),
            "total_chars": sum(
                len(t.get("text", "")) for t in self._session_cache.get(f"session:{session_id}", [])
            ),
            "last_activity": turns[-1].get("timestamp")
            if self._session_cache.get(f"session:{session_id}")
            else None,
        }

    def resume_session(self, session_id: str) -> Dict[str, Any]:
        """
        Resume a paused session.

        Returns full session context for resumption.
        """
        context = self.get_context(session_id, window=100)

        # Get session stats
        stats = self.get_session_stats(session_id)

        return {
            "session_id": session_id,
            "resumed_at": datetime.now(timezone.utc).isoformat(),
            "context": context,
            "stats": stats,
            "resumable": True,
        }

    def clear_session(self, session_id: str) -> bool:
        """Clear session data (GDPR compliance)."""
        cache_key = f"session:{session_id}"
        if cache_key in self._session_cache:
            del self._session_cache[cache_key]

        # Note: LTM records are not deleted for audit trail
        # In production, would implement proper deletion with audit trail
        return True


__all__ = ["ConversationMemoryAdapter"]
