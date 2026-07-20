from .block import IRBlock
from .instruction import (
    IRInstruction,
    Assign,
    Store,
    Load,
    Return,
    Call,
    Branch,
    Jump,
    Const,
    BinaryOp,
)
from .function import IRFunction
from .module import IRModule
from .value import IRValue, Constant, Variable, Binary, Unary
from .builder import IRBuilder
from .printer import IRPrinter

# 从旧 ir_old 导入（兼容）
from compiler.ir_old import IRCapability, IRContract

__all__ = [
    "IRBlock",
    "IRInstruction",
    "Assign",
    "Store",
    "Load",
    "Return",
    "Call",
    "Branch",
    "Jump",
    "Const",
    "BinaryOp",
    "IRFunction",
    "IRModule",
    "IRValue",
    "Constant",
    "Variable",
    "Binary",
    "Unary",
    "IRBuilder",
    "IRPrinter",
    "IRCapability",
    "IRContract",
]
