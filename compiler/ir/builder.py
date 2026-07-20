from .instruction import Store, Load, Return, BinaryOp, Call, Branch, Jump
from .value import Constant, Variable, Binary, Unary


class IRBuilder:
    """IR 构建器 - 所有 IR 生成必须通过此接口"""

    def __init__(self, block):
        self.block = block
        self._current_block = block

    def set_block(self, block):
        self._current_block = block
        self.block = block

    def store(self, target: str, value):
        self._current_block.append(Store(target, value))

    def load(self, name: str):
        self._current_block.append(Load(name))

    def ret(self, value=None):
        self._current_block.append(Return(value))

    def add(self, target: str, left, right):
        self._current_block.append(BinaryOp(target, "+", left, right))

    def sub(self, target: str, left, right):
        self._current_block.append(BinaryOp(target, "-", left, right))

    def mul(self, target: str, left, right):
        self._current_block.append(BinaryOp(target, "*", left, right))

    def div(self, target: str, left, right):
        self._current_block.append(BinaryOp(target, "/", left, right))

    def call(self, target: str, fn_name: str, args=None):
        if args is None:
            args = []
        self._current_block.append(Call(target, args))

    def branch(self, cond, true_block: str, false_block: str):
        """条件分支"""
        self._current_block.append(Branch(cond, true_block, false_block))

    def jump(self, target: str):
        """无条件跳转"""
        self._current_block.append(Jump(target))

    def const(self, value):
        return Constant(value)

    def var(self, name: str):
        return Variable(name)

    def binary(self, op: str, left, right):
        return Binary(op, left, right)
