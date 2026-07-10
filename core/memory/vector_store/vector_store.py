class VectorStore:
    """
    Lightweight semantic-like memory store.

    Version 1 uses simple keyword overlap scoring.
    Can later be replaced with embeddings.
    """

    def __init__(self):
        self._documents = []

    def add(self, text, metadata=None):
        self._documents.append(
            {
                "text": text,
                "metadata": metadata or {},
            }
        )

    def count(self):
        return len(self._documents)

    def all(self):
        return list(self._documents)

    def clear(self):
        self._documents.clear()

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