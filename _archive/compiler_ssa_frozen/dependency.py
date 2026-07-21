"""依赖图 - 用于链接顺序解析"""

from collections import defaultdict, deque
from typing import List, Set, Dict


class DependencyGraph:
    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)   # src -> dsts (src 依赖 dst)
        self.reverse: Dict[str, Set[str]] = defaultdict(set) # dst -> srcs

    def add(self, src: str, dst: str):
        """src 依赖 dst"""
        self.graph[src].add(dst)
        self.reverse[dst].add(src)

    def dependencies(self, node: str) -> List[str]:
        return list(self.graph.get(node, []))

    def dependents(self, node: str) -> List[str]:
        return list(self.reverse.get(node, []))

    def nodes(self) -> List[str]:
        return list(set(self.graph.keys()) | set(self.reverse.keys()))

    def topo_sort(self) -> List[str]:
        """拓扑排序，依赖在前"""
        all_nodes = self.nodes()
        indegree: Dict[str, int] = {}

        for n in all_nodes:
            indegree[n] = len(self.graph.get(n, []))

        q = deque([n for n, d in indegree.items() if d == 0])
        result = []

        while q:
            node = q.popleft()
            result.append(node)

            for parent in self.reverse.get(node, []):
                indegree[parent] -= 1
                if indegree[parent] == 0:
                    q.append(parent)

        if len(result) != len(all_nodes):
            # 检测循环依赖
            cycle = set(all_nodes) - set(result)
            raise ValueError(f"循环依赖检测到: {cycle}")

        return result

    def __repr__(self):
        lines = []
        for src, dsts in self.graph.items():
            lines.append(f"  {src} -> {list(dsts)}")
        return "\n".join(lines) if lines else "  (empty)"
