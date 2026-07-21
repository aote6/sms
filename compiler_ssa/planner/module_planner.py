"""Module Planner - 从决策生成模块定义"""

from module import Module, Capability, Contract, Evidence


class ModulePlanner:
    def plan(self, decision: dict) -> list[Module]:
        """从决策生成模块列表"""
        modules = []

        # 根据决策类型生成模块
        approach = decision.get("approach", "default")

        if approach == "default":
            # 默认生成一个模块
            module = Module(
                name=decision["name"],
                version="1.0.0",
                state="ready",
                capabilities=[
                    Capability(
                        name="process",
                        description=f"处理 {decision['requirements']['name']}",
                        parameters=[("data", "any")],
                        implementation="return"
                    )
                ],
                contract=Contract(runtime="python"),
                evidence=Evidence(test_pass=True)
            )
            modules.append(module)

        return modules
