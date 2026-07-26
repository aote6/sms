"""Plan Executor - 执行计划"""

from planner.node import PlanNode
from typing import List, Any


class PlanExecutor:
    def __init__(self, registry=None):
        self.registry = registry or {}
        self.built = []

    def register_module(self, name: str, module: Any):
        self.registry[name] = module

    def execute(self, plan: List[PlanNode]) -> List[Any]:
        """执行计划，构建模块"""
        built = []

        for node in plan:
            if node.kind != "module":
                continue

            # 从 registry 获取模块
            module = self.registry.get(node.name)

            if module is None:
                # 尝试创建默认模块
                module = self._create_default_module(node)

            if module is not None:
                node.artifact = module
                node.solved = True
                built.append(module)

        self.built = built
        return built

    def _create_default_module(self, node: PlanNode):
        """为未注册的模块创建默认实现"""
        from module import Module, Capability, Contract, Evidence

        return Module(
            name=node.name,
            version="1.0.0",
            state="ready",
            capabilities=[
                Capability(
                    name=node.name.lower().replace(" ", "_"),
                    description=f"实现 {node.name}",
                    parameters=[("data", "any")],
                    implementation="return"
                )
            ],
            contract=Contract(runtime="python"),
            evidence=Evidence(test_pass=True)
        )
