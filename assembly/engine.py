from core.node import Node, NodeType
from module import Module
from .plan import AssemblyPlan, PlanNode
from typing import Optional, List
import uuid

class AssemblyEngine:
    def __init__(self, graph):
        self.graph = graph
        self.modules: dict[str, Module] = {}
        self.plan = AssemblyPlan()
    
    def register_module(self, node: Node, module: Module):
        self.modules[node.id] = module
    
    def create_plan(self, product: Node) -> AssemblyPlan:
        self.plan = AssemblyPlan()
        self._build_plan(product)
        self._connect_edges(product)
        self._verify_plan()
        return self.plan
    
    def _build_plan(self, node: Node):
        children = self.graph.find_children(node)
        for child in children:
            self._build_plan(child)
        
        # 避免重复添加
        if node.id not in self.plan.nodes:
            plan_node = PlanNode(
                id=node.id,
                name=node.name,
                kind=node.node_type.value,
                module=self.modules.get(node.id)
            )
            self.plan.add(plan_node)
    
    def _connect_edges(self, node: Node):
        children = self.graph.find_children(node)
        for child in children:
            self._connect_edges(child)
            # 从child指向parent (依赖关系)
            self.plan.connect(child.id, node.id)
    
    def _verify_plan(self):
        for node in self.plan.nodes.values():
            if node.kind == NodeType.MODULE.value:
                if node.module is None:
                    continue
                errors = self._verify_module(node.module)
                node.module._errors = errors  # 暂存错误
                node.module._verified = len(errors) == 0
    
    def _verify_module(self, module: Module) -> List[str]:
        errors = []
        if module.contract is None:
            errors.append("missing contract")
        if len(module.capabilities) == 0:
            errors.append("missing capability")
        if module.evidence is None:
            errors.append("missing evidence")
        elif not module.evidence.test_pass:
            errors.append("test failed")
        return errors
