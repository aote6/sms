"""PipelineDAG - 流水线 DAG"""

from typing import List, Dict, Set
from collections import deque
from pipeline.stage_base import PipelineStage
from pipeline.stage_node import StageNode


class PipelineDAG:
    def __init__(self):
        self.nodes: Dict[str, StageNode] = {}

    def add(self, stage: PipelineStage) -> StageNode:
        node = StageNode(stage)
        self.nodes[stage.name] = node
        return node

    def depends_on(self, stage_name: str, *dep_names: str):
        """声明 stage_name 依赖 dep_names"""
        if stage_name not in self.nodes:
            raise ValueError(f"阶段 {stage_name} 不存在")
        node = self.nodes[stage_name]
        for dep_name in dep_names:
            if dep_name not in self.nodes:
                raise ValueError(f"依赖阶段 {dep_name} 不存在")
            node.depends_on(self.nodes[dep_name])

    def topological_sort(self) -> List[StageNode]:
        """拓扑排序"""
        indegree = {}
        for name, node in self.nodes.items():
            indegree[name] = len(node.deps)

        queue = deque([name for name, d in indegree.items() if d == 0])
        result = []

        while queue:
            name = queue.popleft()
            node = self.nodes[name]
            result.append(node)

            for user in node.users:
                indegree[user.name] -= 1
                if indegree[user.name] == 0:
                    queue.append(user.name)

        if len(result) != len(self.nodes):
            remaining = set(self.nodes.keys()) - set([n.name for n in result])
            raise ValueError(f"循环依赖检测到: {remaining}")

        return result

    def ready_nodes(self) -> List[StageNode]:
        """获取所有就绪的节点"""
        return [n for n in self.nodes.values() if n.ready()]

    def has_ready(self) -> bool:
        return len(self.ready_nodes()) > 0

    def all_done(self) -> bool:
        return all(n.done for n in self.nodes.values())

    def summary(self):
        print()
        print("=" * 50)
        print("Pipeline DAG")
        print("=" * 50)
        for name, node in self.nodes.items():
            dep_names = [d.name for d in node.deps]
            user_names = [u.name for u in node.users]
            status = "✅" if node.done else "⏳" if node.running else "⬜"
            print(f"  {status} {name}")
            if dep_names:
                print(f"    deps : {', '.join(dep_names)}")
            if user_names:
                print(f"    users: {', '.join(user_names)}")
        print("=" * 50)
