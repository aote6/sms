"""通用图数据结构"""


class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = {}

    def add_node(self, node):
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = set()

    def connect(self, a, b):
        self.add_node(a)
        self.add_node(b)
        self.edges[a].add(b)

    def successors(self, node):
        return list(self.edges.get(node, []))

    def predecessors(self, node):
        result = []
        for src, dsts in self.edges.items():
            if node in dsts:
                result.append(src)
        return result

    def has_edge(self, a, b):
        return b in self.edges.get(a, set())

    def __repr__(self):
        lines = []
        for node in sorted(self.nodes):
            succ = sorted(self.successors(node))
            lines.append(f"  {node} -> {succ}")
        return "\n".join(lines)
