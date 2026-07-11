from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class DependencyNode:
    name: str
    dependencies: Set[str] = field(default_factory=set)


class DependencyGraph:
    """
    Tracks repository relationships.

    Example:

        A -> B
        B -> C
        C -> D
    """

    def __init__(self) -> None:
        # map of node name -> DependencyNode
        self.nodes: Dict[str, DependencyNode] = {}

    def add_node(
        self,
        name: str,
    ):

        if name not in self.nodes:
            self.nodes[name] = DependencyNode(name=name)

    def add_dependency(
        self,
        source: str,
        target: str,
    ):

        self.add_node(source)
        self.add_node(target)

        self.nodes[source].dependencies.add(target)

    def dependencies_of(
        self,
        name: str,
    ) -> List[str]:
        if name not in self.nodes:
            return []

        return sorted(self.nodes[name].dependencies)

    def node_exists(
        self,
        name: str,
    ) -> bool:

        return name in self.nodes

    def node_count(
        self,
    ) -> int:

        return len(self.nodes)

    def dependency_count(
        self,
    ) -> int:

        return sum(len(node.dependencies) for node in self.nodes.values())

    def summary(
        self,
    ) -> Dict:

        return {
            "nodes": self.node_count(),
            "dependencies": self.dependency_count(),
        }

    def clear(self):

        self.nodes = {}
