"""IR 指令 - 使用 SSA 值"""

from dataclasses import dataclass
from typing import List, Any, Optional
from compiler.ssa import SSAValue


class IRInstruction:
    """IR 指令基类"""
    pass


@dataclass
class Load(IRInstruction):
    """加载变量: result = load name"""
    result: SSAValue
    source: str


@dataclass
class Store(IRInstruction):
    """存储变量: store value -> target"""
    target: str
    value: SSAValue


@dataclass
class BinaryOp(IRInstruction):
    """二元运算: result = op left, right"""
    result: SSAValue
    op: str
    left: SSAValue
    right: SSAValue


@dataclass
class Return(IRInstruction):
    """返回值"""
    value: Optional[SSAValue] = None


@dataclass
class Call(IRInstruction):
    """函数调用: result = call fn_name(args)"""
    result: SSAValue
    fn_name: str
    args: List[SSAValue] = None

    def __post_init__(self):
        if self.args is None:
            self.args = []


@dataclass
class Const(IRInstruction):
    """常量: result = const value"""
    result: SSAValue
    value: Any


@dataclass
class Parameter:
    """函数参数"""
    name: str
    type: Any = None
