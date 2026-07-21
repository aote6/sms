"""符号表 - 跨模块链接"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    module: str
    name: str

    @property
    def fullname(self) -> str:
        return f"{self.module}.{self.name}"

    def __str__(self):
        return self.fullname


@dataclass
class IRImport:
    """导入声明"""
    module: str
    function: str

    @property
    def fullname(self) -> str:
        return f"{self.module}.{self.function}"

    def __repr__(self):
        return f"IRImport({self.module}.{self.function})"
