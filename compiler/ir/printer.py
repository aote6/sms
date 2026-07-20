"""IR 打印器 - 支持类型"""

from .instruction import Store, Load, Return, BinaryOp, Call, Const
from compiler.instructions import Branch, Jump, Compare
from compiler.ssa_core import SSAValue


class IRPrinter:
    def print_module(self, module):
        print()
        print("=" * 60)
        print(f"IRModule: {module.name} v{module.version}")
        print(f"runtime: {module.runtime}")
        print("=" * 60)

        for fn in module.functions:
            self.print_function(fn)

    def print_function(self, fn):
        print()
        param_str = ", ".join([f"{p.name}:{p.type}" for p in fn.parameters])
        print(f"function {fn.name}({param_str})")

        for block in fn.blocks:
            self.print_block(block)

    def print_block(self, block):
        print()
        print(f"  {block.name}:")
        for inst in block.instructions:
            print(f"    {self.inst_repr(inst)}")

    def _value_repr(self, value):
        if value is None:
            return "None"
        if isinstance(value, SSAValue):
            return str(value)
        return str(value)

    def _type_repr(self, t):
        if t is None:
            return "Any"
        return str(t)

    def inst_repr(self, inst):
        if isinstance(inst, Load):
            return f"{self._value_repr(inst.result)}:{self._type_repr(inst.result_type)} = load {inst.source}"
        elif isinstance(inst, Store):
            return f"store {self._value_repr(inst.value)}:{self._type_repr(inst.value_type)} -> {inst.target}"
        elif isinstance(inst, Return):
            if inst.value is None:
                return "return"
            return f"return {self._value_repr(inst.value)}:{self._type_repr(inst.value_type)}"
        elif isinstance(inst, BinaryOp):
            return f"{self._value_repr(inst.result)}:{self._type_repr(inst.result_type)} = {inst.op} {self._value_repr(inst.left)}:{self._type_repr(inst.left_type)}, {self._value_repr(inst.right)}:{self._type_repr(inst.right_type)}"
        elif isinstance(inst, Call):
            args = ", ".join([self._value_repr(a) for a in inst.args])
            return f"{self._value_repr(inst.result)}:{self._type_repr(inst.result_type)} = call {inst.fn_name}({args})"
        elif isinstance(inst, Branch):
            return f"branch {self._value_repr(inst.condition)} -> {inst.true_block} : {inst.false_block}"
        elif isinstance(inst, Jump):
            return f"jump {inst.target}"
        elif isinstance(inst, Const):
            return f"{self._value_repr(inst.result)}:{self._type_repr(inst.result_type)} = const {inst.value}"
        elif isinstance(inst, Compare):
            return f"{self._value_repr(inst.result)} = cmp {self._value_repr(inst.left)} {inst.op} {self._value_repr(inst.right)}"
        else:
            return repr(inst)
