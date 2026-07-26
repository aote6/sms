from dataclasses import dataclass, field
from typing import Optional, Set
from collections import deque

@dataclass
class PlanNode:
    id: str
    name: str
    kind: str
    module: Optional[object] = None
    depends: Set[str] = field(default_factory=set)
    required_by: Set[str] = field(default_factory=set)

class AssemblyPlan:
    def __init__(self):
        self.nodes: dict[str, PlanNode] = {}
    
    def add(self, node: PlanNode):
        self.nodes[node.id] = node
    
    def connect(self, src: str, dst: str):
        if src not in self.nodes or dst not in self.nodes:
            return
        self.nodes[src].required_by.add(dst)
        self.nodes[dst].depends.add(src)
    
    def roots(self):
        return [n for n in self.nodes.values() if len(n.depends) == 0]
    
    def topological_sort(self):
        indegree = {}
        q = deque()
        result = []
        
        for node in self.nodes.values():
            indegree[node.id] = len(node.depends)
            if indegree[node.id] == 0:
                q.append(node)
        
        while q:
            node = q.popleft()
            result.append(node)
            for nxt in node.required_by:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(self.nodes[nxt])
        
        return result
    
    def show(self):
        print("\n" + "="*60)
        print("ASSEMBLY PLAN (DAG)")
        print("="*60)
        for node in self.topological_sort():
            dep_str = ", ".join(node.depends) if node.depends else "∅"
            req_str = ", ".join(node.required_by) if node.required_by else "∅"
            mod_str = f" [{node.module.name}]" if node.module else ""
            print(f"  {node.id}: {node.kind} {node.name}{mod_str}")
            print(f"    depends: {dep_str}")
            print(f"    required_by: {req_str}")
        print("="*60)
