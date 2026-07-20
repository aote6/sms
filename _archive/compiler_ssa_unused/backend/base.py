"""Backend 基类 - 所有后端必须实现"""

from abc import ABC, abstractmethod


class Backend(ABC):
    name = "unknown"
    extension = ".txt"

    @abstractmethod
    def emit_module(self, module) -> str:
        """从 IRModule 生成源代码字符串"""
        pass

    def filename(self, module) -> str:
        """生成文件名"""
        return f"{module.name.lower().replace(' ', '_')}{self.extension}"
