from core.node import Node, NodeType
from module import Module, Capability, Contract, Evidence
from registry import ModuleRegistry
from assembly import AssemblyPlan
from typing import List

class GapResolver:
    def __init__(self, registry: ModuleRegistry):
        self.registry = registry
        self.generated: List[Module] = []
    
    def resolve(self, plan: AssemblyPlan) -> AssemblyPlan:
        """扫描计划，对缺少模块的节点自动生成"""
        for node in plan.nodes.values():
            if node.kind == NodeType.MODULE.value and node.module is None:
                module = self._generate_todo_module(node.name)
                self.registry.register(module)
                node.module = module
                self.generated.append(module)
                print(f"⚡ GAP RESOLVED: 生成模块 '{module.name}'")
        return plan
    
    def _generate_todo_module(self, name: str) -> Module:
        return Module(
            name=name,
            version="0.0.1",
            state="todo",
            capabilities=[
                Capability(
                    name="TODO",
                    description=f"需要实现 {name} 的能力",
                    input_type="any",
                    output_type="any"
                )
            ],
            contract=Contract(
                version="0.1",
                runtime="python",
                constraints=["需要人工实现"]
            ),
            evidence=Evidence(
                test_pass=False,
                coverage=0.0,
                benchmark=0.0
            ),
            implementation=f"# TODO: 实现 {name}\npass"
        )
    
    def summary(self):
        if not self.generated:
            print("✓ 无缺失模块，所有依赖已满足")
        else:
            print(f"⚡ 共生成 {len(self.generated)} 个TODO模块:")
            for m in self.generated:
                print(f"   - {m.name} v{m.version} [{m.state}]")
