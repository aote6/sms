"""SMS Intermediate Representation (IR) - 兼容层
所有 Backend 只依赖 IR，不依赖 Module。
"""

from compiler.ir import (
    IRModule,
    IRFunction,
    IRBlock,
    Assign,
    Return,
    Call,
    Branch,
    Jump,
    Const,
    BinaryOp,
    IRInstruction,
)

# 保留旧接口
from dataclasses import dataclass, field
from typing import List, Dict, Any as AnyType, Optional
from compiler.types import IRType, ANY, VOID, Parameter


@dataclass(slots=True)
class IRCapability:
    name: str
    description: str = ""
    function: Optional[IRFunction] = None


@dataclass(slots=True)
class IRContract:
    runtime: str = "python"
    thread_safe: bool = False
    deterministic: bool = True
    metadata: Dict[str, AnyType] = field(default_factory=dict)


# 重新导出
__all__ = [
    "IRModule",
    "IRFunction",
    "IRBlock",
    "IRCapability",
    "IRContract",
    "Assign",
    "Return",
    "Call",
    "Branch",
    "Jump",
    "Const",
    "BinaryOp",
    "IRInstruction",
]
