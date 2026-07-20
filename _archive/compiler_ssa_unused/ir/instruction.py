"""IR 指令 - 使用 SSAValue + 类型"""

from dataclasses import dataclass
from typing import List, Any, Optional
from compiler.value import SSAValue
from compiler.typesystem import ANY, Type


class IRInstruction:
    pass


@dataclass
class Load(IRInstruction):
    result: SSAValue
    source: str
    result_type: Type = ANY


@dataclass
class Store(IRInstruction):
    target: str
    value: SSAValue
    value_type: Type = ANY


@dataclass
class BinaryOp(IRInstruction):
    result: SSAValue
    op: str
    left: SSAValue
    right: SSAValue
    result_type: Type = ANY
    left_type: Type = ANY
    right_type: Type = ANY


@dataclass
class Return(IRInstruction):
    value: Optional[SSAValue] = None
    value_type: Type = ANY


@dataclass
class Call(IRInstruction):
    result: SSAValue
    fn_name: str
    args: List[SSAValue] = None
    result_type: Type = ANY
    arg_types: List[Type] = None

    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.arg_types is None:
            self.arg_types = []


@dataclass
class Const(IRInstruction):
    result: SSAValue
    value: Any
    result_type: Type = ANY


@dataclass
class Parameter:
    name: str
    type: Type = ANY
