from dataclasses import dataclass


class IRValue:
    """IR 值基类"""
    pass


@dataclass
class Constant(IRValue):
    """常量值"""
    value: object

    def __repr__(self):
        return f"Constant({repr(self.value)})"


@dataclass
class Variable(IRValue):
    """变量引用"""
    name: str

    def __repr__(self):
        return f"Variable({self.name})"


@dataclass
class Binary(IRValue):
    """二元运算表达式"""
    op: str
    left: IRValue
    right: IRValue

    def __repr__(self):
        return f"Binary({self.op}, {self.left}, {self.right})"


@dataclass
class Unary(IRValue):
    """一元运算表达式"""
    op: str
    operand: IRValue

    def __repr__(self):
        return f"Unary({self.op}, {self.operand})"
