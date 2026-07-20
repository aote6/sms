"""BuildScheduler - 调度器"""

from build.graph import BuildGraph
from build.node import BuildNode


class BuildScheduler:
    def __init__(self, graph: BuildGraph):
        self.graph = graph

    def schedule(self) -> list[BuildNode]:
        """返回需要构建的 dirty 节点（按拓扑序）"""
        result = []
        for node in self.graph.build_order():
            if node.dirty:
                result.append(node)
        return result

    def schedule_names(self) -> list[str]:
        """返回需要构建的节点名称列表"""
        return [n.name for n in self.schedule()]

    def summary(self):
        nodes = self.schedule()
        print()
        print("=" * 50)
        print("Build Scheduler")
        print("=" * 50)
        if not nodes:
            print("  (无需要构建的节点)")
        else:
            for node in nodes:
                print(f"  🔨 {node.name}")
        print("=" * 50)
