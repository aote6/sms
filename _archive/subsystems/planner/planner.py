"""Planner - 从 Plan Graph 生成执行计划"""

from planner.graph import PlanGraph
from planner.node import PlanNode
from typing import List


class Planner:
    def create(self, graph: PlanGraph) -> List[PlanNode]:
        """从 Plan Graph 生成拓扑排序的执行计划"""
        order = []
        visited = set()

        def dfs(node: PlanNode):
            if node.id in visited:
                return
            visited.add(node.id)

            for child in node.children:
                dfs(child)

            order.append(node)

        # 从 products 开始 DFS
        for root in graph.products():
            dfs(root)

        # 反转得到依赖在前
        return order[::-1]

    def create_from_graph(self, graph: PlanGraph) -> List[PlanNode]:
        """别名"""
        return self.create(graph)
