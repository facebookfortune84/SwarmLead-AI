"""Unit tests for tenant-namespaced memory + vector stores (Constitutional §4.6)."""

import pytest

from core.memory.namespaced_long_term_memory.namespaced_memory import (
    NamespacedLongTermMemory,
    NamespacedSessionMemory,
)
from core.memory.namespaced_vector_store.namespaced_vector_store import NamespacedVectorStore


@pytest.fixture
def ltm(tmp_path):
    return NamespacedLongTermMemory(tenant_id="t1", base_path=str(tmp_path / "ltm.json"))


def test_namespace_key_prefixes(ltm):
    assert ltm._namespace_key("k") == "tenant:t1:memory:k"


def test_add_returns_denamespaced_record(ltm):
    record = ltm.add({"key": "k1", "content": "hello", "type": "note"})
    assert record["key"] == "k1"
    assert record["tenant_id"] == "t1"
    assert record["namespace"] == "tenant:t1:memory"


def test_get_roundtrip(ltm):
    ltm.add({"key": "k1", "content": "hello"})
    result = ltm.get("k1")
    assert result["key"] == "k1"
    assert "hello" in result["content"]


def test_get_missing(ltm):
    assert ltm.get("ghost") is None


def test_query_scoped_to_tenant(ltm):
    ltm.add({"key": "a1", "content": "funding round for acme"})
    ltm.add({"key": "a2", "content": "unrelated note about weather"})
    results = ltm.query("funding acme", top_k=10)
    assert len(results) >= 1
    assert all(r["tenant_id"] == "t1" for r in results)


def test_all_and_count(ltm):
    ltm.add({"key": "x1", "content": "one"})
    ltm.add({"key": "x2", "content": "two"})
    assert ltm.count() == 2
    assert len(ltm.all()) == 2


def test_delete(ltm):
    ltm.add({"key": "d1", "content": "bye"})
    assert ltm.delete("d1") is True
    assert ltm.count() == 0


def test_delete_missing(ltm):
    assert ltm.delete("nope") is False


def test_clear(ltm):
    ltm.add({"key": "c1", "content": "a"})
    ltm.add({"key": "c2", "content": "b"})
    ltm.clear()
    assert ltm.count() == 0


def test_tenant_isolation_between_instances(tmp_path):
    m1 = NamespacedLongTermMemory(tenant_id="t1", base_path=str(tmp_path / "ltm.json"))
    m2 = NamespacedLongTermMemory(tenant_id="t2", base_path=str(tmp_path / "ltm.json"))
    m1.add({"key": "secret", "content": "t1-only"})
    assert m2.get("secret") is None
    assert m1.get("secret") is not None


def test_session_memory_scope():
    s = NamespacedSessionMemory("t1")
    s.set("theme", "dark")
    assert s.get("theme") == "dark"
    assert s.get("missing", "default") == "default"
    s.append("msgs", "one")
    s.append("msgs", "two")
    assert s.get("msgs") == ["one", "two"]
    assert s.all() == {"theme": "dark", "msgs": ["one", "two"]}
    s.delete("theme")
    assert s.get("theme") is None
    s.clear()
    assert s.all() == {}


def test_session_memory_isolated():
    a = NamespacedSessionMemory("t1")
    b = NamespacedSessionMemory("t2")
    a.set("k", "v1")
    assert b.get("k") is None
    assert a.get("k") == "v1"


@pytest.fixture
def vec():
    return NamespacedVectorStore("t1")


def test_vector_add_denamespaces_key(vec):
    result = vec.add("some text", key="doc1")
    assert result["key"] == "doc1"
    assert result["metadata"]["tenant_id"] == "t1"
    assert result["metadata"]["namespace"] == "tenant:t1:vector"


def test_vector_search_filters_tenant(vec):
    vec.add("genesis voice agent demo", key="doc1")
    other = NamespacedVectorStore("t2")
    other.add("genesis voice agent demo", key="doc-other")
    results = vec.search("genesis voice agent", top_k=5)
    assert all(r["metadata"]["tenant_id"] == "t1" for r in results)
    assert len(results) == 1


def test_vector_search_by_metadata(vec):
    vec.add("text a", metadata={"kind": "lead"}, key="l1")
    vec.add("text b", metadata={"kind": "ticket"}, key="l2")
    results = vec.search_by_metadata({"kind": "lead"})
    assert len(results) == 1
    assert results[0]["key"] == "l1"


def test_vector_count_clear_delete(vec):
    vec.add("alpha", key="a")
    vec.add("beta", key="b")
    assert vec.count() == 2
    assert vec.delete("a") is True
    assert vec.delete("a") is False
    assert vec.count() == 1
    vec.clear()
    assert vec.count() == 0


def test_vector_all(vec):
    vec.add("one", key="1")
    vec.add("two", key="2")
    assert len(vec.all()) == 2
