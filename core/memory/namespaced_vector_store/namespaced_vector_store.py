"""
Namespaced Vector Store

Wraps VectorStore with tenant namespacing for Constitutional §4.6 isolation.
All vector operations automatically scoped to tenant:{id}:vector namespace.
"""

from typing import Any, Dict, List, Optional

from core.memory.vector_store.vector_store import VectorStore


class NamespacedVectorStore:
    """
    Tenant-scoped wrapper around VectorStore.

    All vector operations automatically prefixed with tenant:{tenant_id}:vector
    ensuring Constitutional §4.6 portfolio isolation.
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.namespace = f"tenant:{tenant_id}:vector"
        self._store = VectorStore()

    def _namespace_key(self, key: str) -> str:
        """Prefix key with tenant namespace."""
        return f"{self.namespace}:{key}"

    def _denamespace_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Remove namespace prefix from record keys."""
        record = record.copy()
        if "key" in record and record["key"].startswith(f"{self.namespace}:"):
            record["key"] = record["key"][len(self.namespace) + 1 :]
        return record

    def add(
        self, text: str, metadata: Optional[Dict[str, Any]] = None, key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a document to tenant-scoped vector store."""
        metadata = metadata or {}
        metadata["tenant_id"] = self.tenant_id
        metadata["namespace"] = self.namespace

        namespaced_key = self._namespace_key(key) if key else None

        result = self._store.add(text=text, metadata=metadata, key=namespaced_key)
        return self._denamespace_record(result)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search within tenant namespace."""
        # Search with namespace prefix to limit scope
        namespaced_query = f"{self.namespace}:{query}"
        results = self._store.search(query=namespaced_query, top_k=top_k)

        # Filter to ensure tenant isolation (defense in depth)
        filtered = [
            self._denamespace_record(r)
            for r in results
            if r.get("metadata", {}).get("tenant_id") == self.tenant_id
        ]
        return filtered

    def search_by_metadata(
        self, metadata_filter: Dict[str, Any], top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search by metadata within tenant namespace."""
        metadata_filter = metadata_filter.copy()
        metadata_filter["tenant_id"] = self.tenant_id

        results = self._store.search_by_metadata(metadata_filter, top_k=top_k)
        return [self._denamespace_record(r) for r in results]

    def count(self) -> int:
        """Count documents in tenant namespace."""
        # This is approximate - full count would require scanning
        results = self.search("", top_k=1000)
        return len(results)

    def clear(self) -> None:
        """Clear all vectors in tenant namespace."""
        all_records = self.search("", top_k=10000)
        for record in all_records:
            if "key" in record:
                self._store.delete(record["key"])

    def delete(self, key: str) -> bool:
        """Delete a vector by namespaced key."""
        namespaced_key = self._namespace_key(key)
        return self._store.delete(namespaced_key)

    def all(self) -> List[Dict[str, Any]]:
        """Get all vectors in tenant namespace."""
        return self.search("", top_k=10000)
