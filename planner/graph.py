"""Plan Graph - 规划图"""

from planner.node import PlanNode
from typing import List


class PlanGraph:
    def __init__(self):
        self.nodes: dict[str, PlanNode] = {}

    def add(self, node: PlanNode) -> PlanNode:
        self.nodes[node.id] = node
        return node

    def roots(self) -> List[PlanNode]:
        return [n for n in self.nodes.values() if not n.parents]

    def products(self) -> List[PlanNode]:
        return [n for n in self.nodes.values() if n.kind == "product"]

    def get(self, node_id: str) -> PlanNode:
        return self.nodes.get(node_id)

    def all(self):
        return list(self.nodes.values())

    def summary(self):
        print()
        print("=" * 60)
        print("Plan Graph")
        print("=" * 60)
        for node in self.all():
            parent_names = [p.name for p in node.parents]
            child_names = [c.name for c in node.children]
            print(f"  {node.name} ({node.kind})")
            if parent_names:
                print(f"    parents: {', '.join(parent_names)}")
            if child_names:
                print(f"    children: {', '.join(child_names)}")
        print("=" * 60)
