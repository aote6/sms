from core.node import Node, NodeType
from module import Module
from .plan import AssemblyPlan, PlanNode
from .verifier import BehaviorVerifier
from typing import Optional, List


class AssemblyEngine:
    def __init__(self, graph):
        self.graph = graph
        self.modules: dict[str, Module] = {}
        self.plan = AssemblyPlan()
        self.verifier = BehaviorVerifier()

    def register_module(self, node: Node, module: Module):
        self.modules[node.id] = module

    def create_plan(self, product: Node) -> AssemblyPlan:
        self.plan = AssemblyPlan()
        visited = set()
        self._trace_product(product, visited)
        self._build_dependencies()
        self._verify_plan()
        return self.plan

    def verify_product(self, product: Node) -> dict:
        plan = self.create_plan(product)
        all_modules = [node.module for node in plan.nodes.values() if node.module]
        module_results = [self.verifier.verify_contract(mod) for mod in all_modules]
        composition_result = self.verifier.verify_composition(all_modules)
        all_passed = all(r["passed"] for r in module_results) and composition_result["passed"]
        return {
            "product": product.name,
            "passed": all_passed,
            "modules_verified": len(all_modules),
            "module_results": module_results,
            "composition": composition_result,
            "compatible_pairs": composition_result.get("compatible_pairs", []),
        }

    def _trace_product(self, node: Node, visited: set):
        if node.id in visited:
            return
        visited.add(node.id)
        plan_node = PlanNode(id=node.id, name=node.name, kind=node.node_type.value, module=self.modules.get(node.id))
        self.plan.add(plan_node)
        for parent in self._find_parents(node):
            self._trace_product(parent, visited)

    def _find_parents(self, node: Node) -> List[Node]:
        parents = []
        for edge in self.graph.edges:
            if edge.target == node.id and edge.source in self.graph.nodes:
                parents.append(self.graph.nodes[edge.source])
        return parents

    def _build_dependencies(self):
        for edge in self.graph.edges:
            if edge.source in self.plan.nodes and edge.target in self.plan.nodes:
                self.plan.connect(edge.source, edge.target)

    def _verify_plan(self):
        for node in self.plan.nodes.values():
            if node.kind == NodeType.MODULE.value and node.module:
                errors = self._verify_module(node.module)
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
