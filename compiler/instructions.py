"""控制流指令"""

from dataclasses import dataclass
from compiler.ssa import SSAValue


@dataclass
class Jump:
    """无条件跳转"""
    target: str

    def __str__(self):
        return f"jump {self.target}"


@dataclass
class Branch:
    """条件分支"""
    condition: str
    true_block: str
    false_block: str

    def __str__(self):
        return f"branch {self.condition} {self.true_block} {self.false_block}"


@dataclass
class Compare:
    """比较指令 - result 是 SSAValue"""
    op: str
    left: SSAValue
    right: SSAValue
    result: SSAValue

    def __str__(self):
        return f"{self.result} = cmp {self.left} {self.op} {self.right}"


@dataclass
class CallExtern:
    """外部函数调用: result = call module.function(args)"""
    result: str
    module: str
    function: str
    args: list

    def __str__(self):
        return f"{self.result} = call {self.module}.{self.function}({', '.join(self.args)})"
