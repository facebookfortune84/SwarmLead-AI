class VectorStore:
    """
    Lightweight semantic-like memory store.

    Version 1 uses simple keyword overlap scoring.
    Can later be replaced with embeddings.
    """

    def __init__(self):
        self._documents = []

    def add(self, text, metadata=None, key=None):
        doc = {
            "text": text,
            "metadata": metadata or {},
        }
        if key:
            doc["key"] = key
        self._documents.append(doc)
        return doc

    def count(self):
        return len(self._documents)

    def all(self):
        return list(self._documents)

    def clear(self):
        self._documents.clear()

    def delete(self, key: str) -> bool:
        """Delete a document by key."""
        for i, doc in enumerate(self._documents):
            if doc.get("key") == key:
                del self._documents[i]
                return True
        return False

    def search(
        self,
        query,
        top_k=3,
    ):
        query_words = set(query.lower().split())

        scored = []

        for doc in self._documents:
            text_words = set(doc["text"].lower().split())

            score = len(query_words.intersection(text_words))

            scored.append(
                {
                    "score": score,
                    **doc,
                }
            )

        scored.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return scored[:top_k]

    def search_by_metadata(self, metadata_filter: dict, top_k: int = 10) -> list:
        """Search documents by metadata filter."""
        results = []
        for doc in self._documents:
            metadata = doc.get("metadata", {})
            match = True
            for key, value in metadata_filter.items():
                if metadata.get(key) != value:
                    match = False
                    break
            if match:
                results.append(doc)
        return results[:top_k]