"""IR 构建器 - 使用 SSAValue + 控制流 + 外部调用"""

from .instruction import Store, Load, Return, BinaryOp, Call, Const
from .value import Constant, Variable, Binary, Unary
from compiler.value_factory import ValueFactory
from compiler.instructions import Compare, Branch, Jump, CallExtern


class IRBuilder:
    def __init__(self, block):
        self.block = block
        self._current_block = block
        self._factory = ValueFactory()

    def set_block(self, block):
        self._current_block = block
        self.block = block
        self._factory.reset()

    def load(self, name: str) -> SSAValue:
        result = self._factory.create("load")
        self._current_block.append(Load(result, name))
        return result

    def store(self, target: str, value: SSAValue):
        self._current_block.append(Store(target, value))

    def add(self, left: SSAValue, right: SSAValue) -> SSAValue:
        result = self._factory.create("add")
        self._current_block.append(BinaryOp(result, "+", left, right))
        return result

    def sub(self, left: SSAValue, right: SSAValue) -> SSAValue:
        result = self._factory.create("sub")
        self._current_block.append(BinaryOp(result, "-", left, right))
        return result

    def mul(self, left: SSAValue, right: SSAValue) -> SSAValue:
        result = self._factory.create("mul")
        self._current_block.append(BinaryOp(result, "*", left, right))
        return result

    def div(self, left: SSAValue, right: SSAValue) -> SSAValue:
        result = self._factory.create("div")
        self._current_block.append(BinaryOp(result, "/", left, right))
        return result

    def ret(self, value: SSAValue = None):
        self._current_block.append(Return(value))

    def call(self, fn_name: str, args: List[SSAValue] = None) -> SSAValue:
        if args is None:
            args = []
        result = self._factory.create("call")
        self._current_block.append(Call(result, fn_name, args))
        return result

    def call_extern(self, module: str, function: str, *args) -> SSAValue:
        result = self._factory.create("extern")
        self._current_block.append(CallExtern(
            result=result,
            module=module,
            function=function,
            args=list(args)
        ))
        return result

    def branch(self, cond: SSAValue, true_block, false_block):
        self._current_block.append(Branch(cond, true_block.name, false_block.name))

    def jump(self, target):
        self._current_block.append(Jump(target.name))

    def const(self, value) -> SSAValue:
        result = self._factory.create("const")
        self._current_block.append(Const(result, value))
        return result

    def cmp_gt(self, a: SSAValue, b: SSAValue) -> SSAValue:
        result = self._factory.create("cmp")
        self._current_block.append(Compare(">", a, b, result))
        return result

    def cmp_lt(self, a: SSAValue, b: SSAValue) -> SSAValue:
        result = self._factory.create("cmp")
        self._current_block.append(Compare("<", a, b, result))
        return result

    def cmp_eq(self, a: SSAValue, b: SSAValue) -> SSAValue:
        result = self._factory.create("cmp")
        self._current_block.append(Compare("==", a, b, result))
        return result
