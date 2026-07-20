"""IR 打印器 - 支持 SSA 值"""

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
        param_str = ", ".join([p.name for p in fn.parameters])
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

    def inst_repr(self, inst):
        if isinstance(inst, Load):
            return f"{self._value_repr(inst.result)} = load {inst.source}"
        elif isinstance(inst, Store):
            return f"store {self._value_repr(inst.value)} -> {inst.target}"
        elif isinstance(inst, Return):
            return f"return {self._value_repr(inst.value)}"
        elif isinstance(inst, BinaryOp):
            return f"{self._value_repr(inst.result)} = {inst.op} {self._value_repr(inst.left)}, {self._value_repr(inst.right)}"
        elif isinstance(inst, Call):
            args = ", ".join([self._value_repr(a) for a in inst.args])
            return f"{self._value_repr(inst.result)} = call {inst.fn_name}({args})"
        elif isinstance(inst, Branch):
            return f"branch {self._value_repr(inst.condition)} -> {inst.true_block} : {inst.false_block}"
        elif isinstance(inst, Jump):
            return f"jump {inst.target}"
        elif isinstance(inst, Const):
            return f"{self._value_repr(inst.result)} = const {inst.value}"
        elif isinstance(inst, Compare):
            return f"{self._value_repr(inst.result)} = cmp {self._value_repr(inst.left)} {inst.op} {self._value_repr(inst.right)}"
        else:
            return repr(inst)
