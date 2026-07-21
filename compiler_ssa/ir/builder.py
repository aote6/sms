"""IR 构建器 - 使用 SSAValue + 控制流 + 外部调用 + 类型"""

from .instruction import Store, Load, Return, BinaryOp, Call, Const
from .value import Constant, Variable, Binary, Unary
from compiler_ssa.value_factory import ValueFactory
from compiler_ssa.instructions import Compare, Branch, Jump, CallExtern
from compiler_ssa.typesystem import INT, FLOAT, STRING, ANY, infer_type


class IRBuilder:
    def __init__(self, block):
        self.block = block
        self._current_block = block
        self._factory = ValueFactory()

    def set_block(self, block):
        self._current_block = block
        self.block = block
        self._factory.reset()

    def load(self, name: str, type_hint=ANY):
        result = self._factory.create("load")
        self._current_block.append(Load(result, name, type_hint))
        return result

    def store(self, target: str, value, value_type=ANY):
        self._current_block.append(Store(target, value, value_type))

    def add(self, left, right, left_type=ANY, right_type=ANY):
        result = self._factory.create("add")
        result_type = infer_type(left_type, right_type, "+")
        self._current_block.append(BinaryOp(result, "+", left, right, result_type, left_type, right_type))
        return result

    def sub(self, left, right, left_type=ANY, right_type=ANY):
        result = self._factory.create("sub")
        result_type = infer_type(left_type, right_type, "-")
        self._current_block.append(BinaryOp(result, "-", left, right, result_type, left_type, right_type))
        return result

    def mul(self, left, right, left_type=ANY, right_type=ANY):
        result = self._factory.create("mul")
        result_type = infer_type(left_type, right_type, "*")
        self._current_block.append(BinaryOp(result, "*", left, right, result_type, left_type, right_type))
        return result

    def div(self, left, right, left_type=ANY, right_type=ANY):
        result = self._factory.create("div")
        result_type = infer_type(left_type, right_type, "/")
        self._current_block.append(BinaryOp(result, "/", left, right, result_type, left_type, right_type))
        return result

    def ret(self, value=None, value_type=ANY):
        self._current_block.append(Return(value, value_type))

    def call(self, fn_name: str, args=None, result_type=ANY, arg_types=None):
        if args is None:
            args = []
        if arg_types is None:
            arg_types = [ANY] * len(args)
        result = self._factory.create("call")
        self._current_block.append(Call(result, fn_name, args, result_type, arg_types))
        return result

    def call_extern(self, module: str, function: str, *args):
        result = self._factory.create("extern")
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

    def const(self, value, type_hint=ANY):
        result = self._factory.create("const")
        self._current_block.append(Const(result, value, type_hint))
        return result

    def cmp_gt(self, a, b):
        result = self._factory.create("cmp")
        self._current_block.append(Compare(">", a, b, result))
        return result

    def cmp_lt(self, a, b):
        result = self._factory.create("cmp")
        self._current_block.append(Compare("<", a, b, result))
        return result

    def cmp_eq(self, a, b):
        result = self._factory.create("cmp")
        self._current_block.append(Compare("==", a, b, result))
        return result
