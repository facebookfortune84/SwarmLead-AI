from core.orchestration.dependency_graph import (
    DependencyGraph,
    DependencyNode,
)


def test_add_node():
    graph = DependencyGraph()

    graph.add_node("a")

    assert graph.node_exists("a") is True


def test_add_node_duplicate():
    graph = DependencyGraph()

    graph.add_node("a")
    graph.add_node("a")

    assert graph.node_count() == 1


def test_add_dependency():
    graph = DependencyGraph()

    graph.add_dependency(
        "a",
        "b",
    )

    assert graph.dependencies_of("a") == ["b"]


def test_add_multiple_dependencies():
    graph = DependencyGraph()

    graph.add_dependency(
        "a",
        "b",
    )

    graph.add_dependency(
        "a",
        "c",
    )

    deps = graph.dependencies_of("a")

    assert len(deps) == 2


def test_dependencies_missing():
    graph = DependencyGraph()

    assert graph.dependencies_of("missing") == []


def test_node_exists_false():
    graph = DependencyGraph()

    assert graph.node_exists("x") is False


def test_node_count():
    graph = DependencyGraph()

    graph.add_node("a")
    graph.add_node("b")

    assert graph.node_count() == 2


def test_dependency_count():
    graph = DependencyGraph()

    graph.add_dependency(
        "a",
        "b",
    )

    graph.add_dependency(
        "a",
        "c",
    )

    assert graph.dependency_count() == 2


def test_summary_empty():
    graph = DependencyGraph()

    summary = graph.summary()

    assert summary["nodes"] == 0
    assert summary["dependencies"] == 0


def test_summary_populated():
    graph = DependencyGraph()

    graph.add_dependency(
        "a",
        "b",
    )

    summary = graph.summary()

    assert summary["nodes"] == 2
    assert summary["dependencies"] == 1


def test_clear():
    graph = DependencyGraph()

    graph.add_dependency(
        "a",
        "b",
    )

    graph.clear()

    assert graph.node_count() == 0


def test_dependency_node_dataclass():
    node = DependencyNode(name="demo")

    assert node.name == "demo"
    assert node.dependencies == set()
