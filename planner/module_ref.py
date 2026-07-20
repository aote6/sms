"""ModuleRef - 模块引用"""

from dataclasses import dataclass


@dataclass
class ModuleRef:
    name: str
    version: str = "latest"
    runtime: str = "python"
    optional: bool = False

    def __str__(self):
        return f"{self.name}@{self.version}"

    def __repr__(self):
        return self.__str__()
