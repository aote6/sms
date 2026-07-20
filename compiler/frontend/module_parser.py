"""Module → Artifact 解析器"""

from module import Module
from compiler.artifact import Artifact


class ModuleParser:
    def parse(self, module: Module) -> Artifact:
        """将 Module 解析为 Artifact"""
        return Artifact(
            module=module,
            runtime=module.contract.runtime if module.contract else "python",
            metadata={
                "state": module.state,
                "capabilities": [c.name for c in module.capabilities],
                "version": module.version,
            }
        )
