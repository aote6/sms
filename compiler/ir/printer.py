from .instruction import Store, Load, Return, BinaryOp, Call, Branch, Jump, Const
from .value import Constant, Variable, Binary, Unary


class IRPrinter:
    """IR 打印器 - 用于调试"""

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
        print(f"function {fn.name}(")
        if fn.parameters:
            for p in fn.parameters:
                print(f"    {p},")
        print(")")

        for block in fn.blocks:
            self.print_block(block)

    def print_block(self, block):
        print()
        print(f"  {block.name}:")
        for inst in block.instructions:
            print(f"    {self.inst_repr(inst)}")

    def inst_repr(self, inst):
        if isinstance(inst, Store):
            return f"store {inst.value} -> {inst.target}"
        elif isinstance(inst, Load):
            return f"load {inst.name}"
        elif isinstance(inst, Return):
            return f"return {self.value_repr(inst.value)}"
        elif isinstance(inst, BinaryOp):
            return f"{inst.target} = {self.value_repr(inst.left)} {inst.op} {self.value_repr(inst.right)}"
        elif isinstance(inst, Call):
            return f"{inst.target} = call {inst.args}"
        elif isinstance(inst, Branch):
            return f"branch {inst.condition} -> {inst.true_block} : {inst.false_block}"
        elif isinstance(inst, Jump):
            return f"jump {inst.target}"
        elif isinstance(inst, Const):
            return f"const {inst.value}"
        else:
            return repr(inst)

    def value_repr(self, value):
        if value is None:
            return "None"
        elif isinstance(value, Constant):
            return repr(value.value)
        elif isinstance(value, Variable):
            return value.name
        elif isinstance(value, Binary):
            return f"({self.value_repr(value.left)} {value.op} {self.value_repr(value.right)})"
        elif isinstance(value, Unary):
            return f"({value.op} {self.value_repr(value.operand)})"
        else:
            return repr(value)
