"""Module → Artifact 解析器"""

from module import Module
from compiler.artifact import IRArtifact


class ModuleParser:
    def parse(self, module: Module) -> IRArtifact:
        """将 Module 解析为 IRArtifact"""
        # 创建空的 IRArtifact，module 稍后由 IRBuilder 填充
        return IRArtifact(
            module=None,  # 稍后填充
            metadata={
                "state": module.state,
                "capabilities": [c.name for c in module.capabilities],
                "version": module.version,
                "original_module": module.name,
            }
        )
