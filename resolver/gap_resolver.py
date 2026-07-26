from module import Module, Capability, Contract, Evidence, QualityState
from registry import ModuleRegistry
from typing import List


class GapResolver:
    """扫描依赖图，对声明了依赖但 registry 里没有真实模块的名字，
    自动生成一个 TODO 占位模块（quality_state=PENDING）。

    注意：2026-07-26 结构清理后，assembly/ 已归档，本类不再依赖
    AssemblyPlan/NodeType，改为直接扫描 build.BuildGraph 的节点名。
    """

    def __init__(self, registry: ModuleRegistry):
        self.registry = registry
        self.generated: List[Module] = []

    def resolve_graph(self, build_graph) -> List[Module]:
        for name in list(build_graph.nodes.keys()):
            if self.registry.get(name) is None:
                module = self._generate_todo_module(name)
                self.registry.register(module)
                self.generated.append(module)
                print(f"⚡ GAP RESOLVED: 生成模块 '{module.name}'")
        return self.generated

    def _generate_todo_module(self, name: str) -> Module:
        return Module(
            name=name,
            version="0.0.1",
            quality_state=QualityState.PENDING,
            capabilities=[
                Capability(
                    name="TODO",
                    description=f"需要实现 {name} 的能力",
                    input_type="any",
                    output_type="any",
                )
            ],
            contract=Contract(
                version="0.1",
                runtime="python",
                constraints=["需要人工实现"],
            ),
            evidence=Evidence(test_pass=False, coverage=0.0, benchmark=0.0),
            implementation=f"# TODO: 实现 {name}\npass",
        )

    def summary(self):
        if not self.generated:
            print("✓ 无缺失模块，所有依赖已满足")
        else:
            print(f"⚡ 共生成 {len(self.generated)} 个TODO模块:")
            for m in self.generated:
                print(f"   - {m.name} v{m.version} [{m.quality_state}]")
