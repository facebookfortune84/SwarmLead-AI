import importlib
from typing import Any, Type, cast

VectorStore: Any

try:
    from core.memory.vector_store import VectorStore as _VectorStore
except ImportError:
    vector_store_module = importlib.import_module("core.memory.vector_store")
    vector_store_class = cast(Type[Any], getattr(vector_store_module, "VectorStore", None))
    if vector_store_class is None:
        try:
            vector_store_submodule = importlib.import_module(
                "core.memory.vector_store.vector_store"
            )
        except ImportError:
            vector_store_submodule = None
        if vector_store_submodule is not None:
            vector_store_class = cast(
                Type[Any], getattr(vector_store_submodule, "VectorStore", None)
            )
    if vector_store_class is None:
        for attr in vars(vector_store_module).values():
            if (
                isinstance(attr, type)
                and "vector" in attr.__name__.lower()
                and "store" in attr.__name__.lower()
            ):
                vector_store_class = cast(Type[Any], attr)
                break
    if vector_store_class is None:
        raise
    VectorStore = vector_store_class
else:
    VectorStore = _VectorStore


def test_add_document():
    store = VectorStore()
    store.add("hello world")

    assert store.count() == 1


def test_clear():
    store = VectorStore()
    store.add("test")
    store.clear()

    assert store.count() == 0


def test_all():
    store = VectorStore()
    store.add("first")
    store.add("second")

    assert len(store.all()) == 2


def test_search_single_match():
    store = VectorStore()
    store.add("python developer")
    store.add("marketing campaign")

    results = store.search("python")

    assert results[0]["text"] == "python developer"


def test_search_ranks_best_match():
    store = VectorStore()
    store.add("python developer outreach")
    store.add("python")
    store.add("sales campaign")

    results = store.search("python developer")

    assert results[0]["text"] == "python developer outreach"


def test_search_with_metadata():
    store = VectorStore()
    store.add("builder archetype campaign", metadata={"type": "archetype"})

    results = store.search("builder")

    assert results[0]["metadata"]["type"] == "archetype"


def test_search_empty_store():
    store = VectorStore()

    results = store.search("anything")

    assert results == []


def test_search_top_k():
    store = VectorStore()

    for i in range(10):
        store.add(f"python document {i}")

    results = store.search("python", top_k=5)

    assert len(results) == 5
