from dataclasses import dataclass
from typing import List, Any, Optional


class IRInstruction:
    """IR 指令基类"""
    pass


@dataclass
class Assign(IRInstruction):
    """变量赋值"""
    target: str
    value: Any


@dataclass
class Store(IRInstruction):
    """存储变量"""
    target: str
    value: Any


@dataclass
class Load(IRInstruction):
    """加载变量"""
    name: str


@dataclass
class Return(IRInstruction):
    """返回值"""
    value: Optional[Any] = None


@dataclass
class Call(IRInstruction):
    """函数调用"""
    target: str
    args: List[Any] = None

    def __post_init__(self):
        if self.args is None:
            self.args = []


@dataclass
class Branch(IRInstruction):
    """条件分支"""
    condition: Any
    true_block: str
    false_block: str


@dataclass
class Jump(IRInstruction):
    """无条件跳转"""
    target: str


@dataclass
class Const(IRInstruction):
    """常量指令"""
    value: Any


@dataclass
class BinaryOp(IRInstruction):
    """二元运算指令"""
    target: str
    op: str
    left: Any
    right: Any
