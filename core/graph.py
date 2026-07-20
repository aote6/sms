from .node import Node
from .edge import Edge, EdgeType

class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        return node

    def connect(self, source: Node, target: Node, edge_type: EdgeType):
        self.edges.append(
            Edge(source.id, target.id, edge_type)
        )

    def find_children(self, node):
        result = []
        for edge in self.edges:
            if edge.source == node.id:
                result.append(self.nodes[edge.target])
        return result

    def show(self):
        for node in self.nodes.values():
            print(node.node_type.value, ":", node.name)
            for child in self.find_children(node):
                print(" ->", child.node_type.value, child.name)
