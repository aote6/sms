from core.node import Node, NodeType
from module import Module
from .plan import AssemblyPlan, PlanNode
from typing import Optional, List


class AssemblyEngine:
    def __init__(self, graph):
        self.graph = graph
        self.modules: dict[str, Module] = {}
        self.plan = AssemblyPlan()

    def register_module(self, node: Node, module: Module):
        self.modules[node.id] = module

    def create_plan(self, product: Node) -> AssemblyPlan:
        """从 Product 节点反向追溯，生成完整装配计划"""
        self.plan = AssemblyPlan()
        
        # 从 Product 出发，反向找所有参与这个产品的节点
        visited = set()
        self._trace_product(product, visited)
        
        # 建立依赖边
        self._build_dependencies()
        
        self._verify_plan()
        return self.plan

    def _trace_product(self, node: Node, visited: set):
        """反向追溯：从 Product -> Module -> Decision -> Problem"""
        if node.id in visited:
            return
        visited.add(node.id)
        
        # 添加到装配计划
        plan_node = PlanNode(
            id=node.id,
            name=node.name,
            kind=node.node_type.value,
            module=self.modules.get(node.id)
        )
        self.plan.add(plan_node)
        
        # 反向查找：谁指向了当前节点？
        parents = self._find_parents(node)
        for parent in parents:
            self._trace_product(parent, visited)

    def _find_parents(self, node: Node) -> List[Node]:
        """查找所有指向当前节点的节点（反向边）"""
        parents = []
        for edge in self.graph.edges:
            if edge.target == node.id:
                if edge.source in self.graph.nodes:
                    parents.append(self.graph.nodes[edge.source])
        return parents

    def _build_dependencies(self):
        """根据图谱中的边建立 PlanNode 之间的依赖关系"""
        for edge in self.graph.edges:
            if edge.source in self.plan.nodes and edge.target in self.plan.nodes:
                # source 依赖 target（target 必须先构建）
                # 只有 Module 之间的 DEPEND 才算真正的构建依赖
                # CREATE/ANSWER/COMPOSE 是逻辑关系，也需要体现在计划中
                self.plan.connect(edge.source, edge.target)

    def _verify_plan(self):
        for node in self.plan.nodes.values():
            if node.kind == NodeType.MODULE.value:
                if node.module is None:
                    continue
                errors = self._verify_module(node.module)
                if not hasattr(node.module, '_errors'):
                    node.module._errors = errors
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
