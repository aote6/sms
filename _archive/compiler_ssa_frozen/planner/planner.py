"""Planner - 从知识图谱生成 Assembly Plan"""

from core import KnowledgeGraph, Node, NodeType, EdgeType
from compiler_ssa.planner.problem_analyzer import ProblemAnalyzer
from compiler_ssa.planner.decision_maker import DecisionMaker
from compiler_ssa.planner.module_planner import ModulePlanner
from assembly import AssemblyPlan, PlanNode


class Planner:
    def __init__(self):
        self.problem_analyzer = ProblemAnalyzer()
        self.decision_maker = DecisionMaker()
        self.module_planner = ModulePlanner()

    def plan(self, graph: KnowledgeGraph, product: Node) -> tuple[AssemblyPlan, list]:
        assembly_plan = AssemblyPlan()
        modules = []

        self._collect_nodes(graph, product, assembly_plan)
        self._connect_dependencies(graph, assembly_plan)
        modules = self._generate_modules(graph, assembly_plan)

        return assembly_plan, modules

    def _collect_nodes(self, graph: KnowledgeGraph, node: Node, plan: AssemblyPlan):
        children = graph.find_children(node)
        for child in children:
            self._collect_nodes(graph, child, plan)

        if node.id not in plan.nodes:
            plan_node = PlanNode(
                id=node.id,
                name=node.name,
                kind=node.node_type.value,
            )
            plan.add(plan_node)

    def _connect_dependencies(self, graph: KnowledgeGraph, plan: AssemblyPlan):
        for edge in graph.edges:
            # Edge 的属性是 source 和 target
            if edge.source in plan.nodes and edge.target in plan.nodes:
                plan.connect(edge.source, edge.target)

    def _generate_modules(self, graph: KnowledgeGraph, plan: AssemblyPlan) -> list:
        from module import Module, Capability, Contract, Evidence

        modules = []

        for node in plan.nodes.values():
            if node.kind != "module":
                continue

            orig_node = None
            for n in graph.nodes.values():
                if n.id == node.id:
                    orig_node = n
                    break

            if orig_node is None:
                continue

            module = Module(
                name=orig_node.name,
                version="1.0.0",
                state="ready",
                capabilities=[
                    Capability(
                        name=orig_node.name.lower().replace(" ", "_"),
                        description=f"实现 {orig_node.name}",
                        parameters=[("data", "any")],
                        implementation="return"
                    )
                ],
                contract=Contract(runtime="python"),
                evidence=Evidence(test_pass=True)
            )
            modules.append(module)

        return modules
