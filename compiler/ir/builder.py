"""IR 构建器 - 使用 SSA 值 + 控制流 + 外部调用"""

from .instruction import Store, Load, Return, BinaryOp, Call, Const
from .value import Constant, Variable, Binary, Unary
from compiler.ssa import SSAValueGenerator
from compiler.instructions import Compare, Branch, Jump, CallExtern


class IRBuilder:
    def __init__(self, block):
        self.block = block
        self._current_block = block
        self._gen = SSAValueGenerator()

    def set_block(self, block):
        self._current_block = block
        self.block = block
        self._gen.reset()

    def load(self, name: str):
        result = self._gen.next()
        self._current_block.append(Load(result, name))
        return result

    def store(self, target: str, value):
        self._current_block.append(Store(target, value))

    def add(self, left, right):
        result = self._gen.next()
        self._current_block.append(BinaryOp(result, "+", left, right))
        return result

    def sub(self, left, right):
        result = self._gen.next()
        self._current_block.append(BinaryOp(result, "-", left, right))
        return result

    def mul(self, left, right):
        result = self._gen.next()
        self._current_block.append(BinaryOp(result, "*", left, right))
        return result

    def div(self, left, right):
        result = self._gen.next()
        self._current_block.append(BinaryOp(result, "/", left, right))
        return result

    def ret(self, value=None):
        self._current_block.append(Return(value))

    def call(self, fn_name: str, args=None):
        if args is None:
            args = []
        result = self._gen.next()
        self._current_block.append(Call(result, fn_name, args))
        return result

    def call_extern(self, module: str, function: str, *args):
        """调用外部模块的函数"""
        result = self._gen.next()
        self._current_block.append(CallExtern(
            result=result,
            module=module,
            function=function,
            args=list(args)
        ))
        return result

    def branch(self, cond, true_block, false_block):
        self._current_block.append(Branch(cond, true_block.name, false_block.name))

    def jump(self, target):
        self._current_block.append(Jump(target.name))

    def const(self, value):
        result = self._gen.next()
        self._current_block.append(Const(result, value))
        return result

    def cmp_gt(self, a, b):
        result = self._gen.next()
        self._current_block.append(Compare(">", a, b, result))
        return result

    def cmp_lt(self, a, b):
        result = self._gen.next()
        self._current_block.append(Compare("<", a, b, result))
        return result

    def cmp_eq(self, a, b):
        result = self._gen.next()
        self._current_block.append(Compare("==", a, b, result))
        return result
