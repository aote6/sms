"""Module → Artifact 解析器"""

from module import Module
from compiler.artifact import IRArtifact


class ModuleParser:
    def parse(self, module: Module) -> IRArtifact:
        """将 Module 解析为 IRArtifact"""
        # 保存完整的 capability 信息
        caps_info = []
        for c in module.capabilities:
            caps_info.append({
                "name": c.name,
                "description": c.description,
                "parameters": c.parameters if hasattr(c, 'parameters') else [],
                "implementation": c.implementation if hasattr(c, 'implementation') else "",
                "input_type": c.input_type if hasattr(c, 'input_type') else "any",
                "output_type": c.output_type if hasattr(c, 'output_type') else "any",
            })

        return IRArtifact(
            module=None,
            metadata={
                "state": module.state,
                "capabilities": caps_info,
                "version": module.version,
                "original_module": module.name,
                "contract": module.contract,
            }
        )
