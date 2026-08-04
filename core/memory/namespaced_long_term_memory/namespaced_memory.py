"""
Namespaced Long-Term Memory

Wraps LongTermMemory with tenant namespacing for Constitutional §4.6 isolation.
All memory operations are automatically scoped to tenant:{id}:memory namespace.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.memory.long_term_memory.long_term_memory import LongTermMemory


class NamespacedLongTermMemory:
    """
    Tenant-scoped wrapper around LongTermMemory.

    All memory operations automatically prefixed with tenant:{tenant_id}:
    ensuring Constitutional §4.6 portfolio isolation.
    """

    def __init__(self, tenant_id: str, base_path: Optional[str] = None):
        self.tenant_id = tenant_id
        self.namespace = f"tenant:{tenant_id}:memory"
        if base_path is None:
            base_path = "data/long_term_memory.json"
        self._ltm = LongTermMemory(path=base_path)

    def _namespace_key(self, key: str) -> str:
        """Prefix key with tenant namespace."""
        return f"{self.namespace}:{key}"

    def _denamespace_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Remove namespace prefix from record keys."""
        record = record.copy()
        if "key" in record and record["key"].startswith(f"{self.namespace}:"):
            record["key"] = record["key"][len(self.namespace) + 1 :]
        return record

    def add(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add a memory record with tenant namespace."""
        # Add tenant context to record
        namespaced_record = record.copy()
        namespaced_record["tenant_id"] = self.tenant_id
        namespaced_record["namespace"] = self.namespace
        namespaced_record["created_at"] = namespaced_record.get(
            "created_at", datetime.now(timezone.utc).isoformat()
        )

        # Namespace the key if present
        if "key" in namespaced_record:
            namespaced_record["key"] = self._namespace_key(namespaced_record["key"])

        result = self._ltm.add(namespaced_record)
        return self._denamespace_record(result)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a memory record by namespaced key."""
        namespaced_key = self._namespace_key(key)
        result = self._ltm.get(namespaced_key)
        return self._denamespace_record(result) if result else None

    def query(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query memories within tenant namespace."""
        # Search the raw query text, then filter to this tenant's namespace
        results = self._ltm.search_text(query)
        namespaced = [
            r for r in results if r.get("key", "").startswith(f"{self.namespace}:")
        ]
        return [self._denamespace_record(r) for r in namespaced[:top_k]]

    def all(self) -> List[Dict[str, Any]]:
        """Get all memories within tenant namespace."""
        all_records = self._ltm.all()
        namespaced = [
            self._denamespace_record(r)
            for r in all_records
            if r.get("key", "").startswith(f"{self.namespace}:")
        ]
        return namespaced

    def delete(self, key: str) -> bool:
        """Delete a memory record by namespaced key."""
        namespaced_key = self._namespace_key(key)
        return self._ltm.delete(namespaced_key)

    def clear(self) -> None:
        """Clear all memories within tenant namespace."""
        all_records = self.all()
        for record in all_records:
            self.delete(record["key"])

    def count(self) -> int:
        """Count memories in tenant namespace."""
        return len(self.all())


class NamespacedSessionMemory:
    """
    Tenant-scoped wrapper around SessionMemory.

    In-memory ephemeral storage scoped to tenant:{tenant_id}:session.
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.namespace = f"tenant:{tenant_id}:session"
        self._memory = {}

    def _namespace_key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    def set(self, key: str, value: Any) -> None:
        self._memory[self._namespace_key(key)] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._memory.get(self._namespace_key(key), default)

    def append(self, key: str, value: Any) -> None:
        namespaced = self._namespace_key(key)
        if namespaced not in self._memory:
            self._memory[namespaced] = []
        self._memory[namespaced].append(value)

    def delete(self, key: str) -> None:
        self._memory.pop(self._namespace_key(key), None)

    def clear(self) -> None:
        keys_to_delete = [k for k in self._memory if k.startswith(f"{self.namespace}:")]
        for k in keys_to_delete:
            del self._memory[k]

    def all(self) -> Dict[str, Any]:
        return {
            k[len(self.namespace) + 1 :]: v
            for k, v in self._memory.items()
            if k.startswith(f"{self.namespace}:")
        }
