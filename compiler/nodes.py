"""SMS IR Nodes
编译器中间表示节点，所有Backend只认识这些节点。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Any
from compiler.types import IRType, ANY


# ============================================================
# IR Node Base
# ============================================================

@dataclass(slots=True)
class IRNode:
    """所有IR节点的基类"""
    pass


# ============================================================
# Expressions
# ============================================================

@dataclass(slots=True)
class IRConstant(IRNode):
    """常量值"""
    value: Any


@dataclass(slots=True)
class IRVariable(IRNode):
    """变量引用"""
    name: str
    type: IRType = ANY


@dataclass(slots=True)
class IRCall(IRNode):
    """函数调用"""
    target: str
    args: List[IRNode] = field(default_factory=list)
    kwargs: dict[str, IRNode] = field(default_factory=dict)


@dataclass(slots=True)
class IRAttribute(IRNode):
    """属性访问"""
    target: IRNode
    attr: str


@dataclass(slots=True)
class IRBinaryOp(IRNode):
    """二元运算"""
    op: str  # +, -, *, /, ==, !=, <, >, etc.
    left: IRNode
    right: IRNode


@dataclass(slots=True)
class IRUnaryOp(IRNode):
    """一元运算"""
    op: str  # -, not, ~
    operand: IRNode


# ============================================================
# Statements
# ============================================================

@dataclass(slots=True)
class IRAssign(IRNode):
    """变量赋值"""
    target: str
    value: IRNode


@dataclass(slots=True)
class IRAttributeAssign(IRNode):
    """属性赋值"""
    target: IRNode
    attr: str
    value: IRNode


@dataclass(slots=True)
class IRReturn(IRNode):
    """返回值"""
    value: Optional[IRNode] = None


@dataclass(slots=True)
class IRIf(IRNode):
    """条件判断"""
    cond: IRNode
    then_body: List[IRNode] = field(default_factory=list)
    else_body: List[IRNode] = field(default_factory=list)


@dataclass(slots=True)
class IRFor(IRNode):
    """循环"""
    target: str
    iterable: IRNode
    body: List[IRNode] = field(default_factory=list)


@dataclass(slots=True)
class IRWhile(IRNode):
    """While循环"""
    cond: IRNode
    body: List[IRNode] = field(default_factory=list)


@dataclass(slots=True)
class IRFunctionDef(IRNode):
    """函数定义（嵌套）"""
    name: str
    parameters: List[str] = field(default_factory=list)
    body: List[IRNode] = field(default_factory=list)
    returns: IRType = ANY


@dataclass(slots=True)
class IRClassDef(IRNode):
    """类定义（嵌套）"""
    name: str
    methods: List[IRFunctionDef] = field(default_factory=list)


# ============================================================
# Module-level
# ============================================================

@dataclass(slots=True)
class IRModuleNode(IRNode):
    """顶层模块"""
    name: str
    version: str
    body: List[IRNode] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
