"""BuildGraph - 构建依赖图"""

from build.node import BuildNode
from collections import deque


class BuildGraph:
    def __init__(self):
        self.nodes: dict[str, BuildNode] = {}

    def node(self, name: str) -> BuildNode:
        if name not in self.nodes:
            self.nodes[name] = BuildNode(name)
        return self.nodes[name]

    def add_dependency(self, target: str, dependency: str):
        """target 依赖 dependency"""
        a = self.node(target)
        b = self.node(dependency)
        a.deps.add(dependency)
        b.users.add(target)

    def add_deps(self, target: str, dependencies: list[str]):
        for dep in dependencies:
            self.add_dependency(target, dep)

    def mark_dirty(self, name: str):
        if name not in self.nodes:
            return
        self._mark(name)

    def _mark(self, name: str):
        node = self.nodes[name]
        if node.dirty:
            return
        node.dirty = True
        for user in node.users:
            self._mark(user)

    def clear_dirty(self):
        for node in self.nodes.values():
            node.dirty = False
            node.built = False

    def build_order(self) -> list[BuildNode]:
        indegree = {}
        for name, node in self.nodes.items():
            indegree[name] = len(node.deps)

        q = deque()
        for name, d in indegree.items():
            if d == 0:
                q.append(name)

        result = []
        while q:
            name = q.popleft()
            node = self.nodes[name]
            result.append(node)
            for user in node.users:
                indegree[user] -= 1
                if indegree[user] == 0:
                    q.append(user)

        if len(result) != len(self.nodes):
            remaining = set(self.nodes.keys()) - set([n.name for n in result])
            raise ValueError(f"循环依赖检测到: {remaining}")

        return result

    def dirty_nodes(self) -> list[BuildNode]:
        return [n for n in self.nodes.values() if n.dirty]

    def summary(self):
        print()
        print("=" * 50)
        print("Build Graph")
        print("=" * 50)
        for name, node in sorted(self.nodes.items()):
            deps = sorted(node.deps)
            users = sorted(node.users)
            print(f"  {name} (dirty={node.dirty})")
            if deps:
                print(f"    deps : {', '.join(deps)}")
            if users:
                print(f"    users: {', '.join(users)}")
        print("=" * 50)
