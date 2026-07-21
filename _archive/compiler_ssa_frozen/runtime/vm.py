"""IR 虚拟机 - 支持控制流 + 跨模块调用"""

from compiler_ssa.ir import IRModule, IRFunction, IRBlock
from compiler_ssa.ir.instruction import Load, Store, Return, BinaryOp, Call, Const
from compiler_ssa.instructions import Branch, Jump, Compare, CallExtern
from compiler_ssa.ssa import SSAValue


class IRVM:
    def __init__(self, debug=False, program=None):
        self.debug = debug
        self._registers = {}
        self.program = program

    def register_program(self, program):
        self.program = program

    def call(self, ir: IRModule, fn_name: str, *args) -> any:
        if isinstance(ir, str):
            # 如果传入的是模块名，从 program 中获取
            if self.program and ir in self.program.modules:
                ir = self.program.modules[ir]
            else:
                raise ValueError(f"模块 {ir} 不存在")

        fn = None
        for f in ir.functions:
            if f.name == fn_name:
                fn = f
                break

        if fn is None:
            raise ValueError(f"函数 {fn_name} 不存在于模块 {ir.name}")

        self._registers = {}

        for i, p in enumerate(fn.parameters):
            value = args[i] if i < len(args) else None
            self._registers[p.name] = value

        if self.debug:
            print(f"📦 调用: {ir.name}.{fn_name} {args}")

        blocks = {b.name: b for b in fn.blocks}
        current = fn.blocks[0] if fn.blocks else None

        ip = 0
        while current and ip < len(current.instructions):
            inst = current.instructions[ip]
            result = self._execute_instruction(inst, current, blocks, fn)

            if isinstance(result, tuple) and result[0] == "return":
                return result[1]
            elif result == "jump":
                ip = -1
            elif isinstance(result, tuple) and result[0] == "branch":
                current = result[1]
                ip = -1

            ip += 1

        return None

    def _get_value(self, value):
        if value is None:
            return None
        if isinstance(value, SSAValue):
            return self._registers.get(value.id)
        if isinstance(value, str):
            if value in self._registers:
                return self._registers[value]
            try:
                id_val = int(value)
                return self._registers.get(id_val)
            except (ValueError, TypeError):
                pass
        return None

    def _set_register(self, key, value):
        if isinstance(key, SSAValue):
            self._registers[key.id] = value
        else:
            self._registers[key] = value

    def _execute_instruction(self, inst, current_block, blocks, fn):
        if isinstance(inst, Load):
            val = self._get_value(inst.source)
            if self.debug:
                print(f"   load {inst.source} -> %{inst.result.id} = {val}")
            self._set_register(inst.result, val)

        elif isinstance(inst, Store):
            val = self._get_value(inst.value)
            self._set_register(inst.target, val)

        elif isinstance(inst, BinaryOp):
            left = self._get_value(inst.left)
            right = self._get_value(inst.right)
            if self.debug:
                print(f"   {inst.op} {left} {right}")
            if inst.op == "+":
                self._set_register(inst.result, left + right)
            elif inst.op == "-":
                self._set_register(inst.result, left - right)
            elif inst.op == "*":
                self._set_register(inst.result, left * right)
            elif inst.op == "/":
                self._set_register(inst.result, left / right if right != 0 else 0)
            else:
                self._set_register(inst.result, None)

        elif isinstance(inst, Const):
            self._set_register(inst.result, inst.value)

        elif isinstance(inst, Return):
            if inst.value is None:
                return ("return", None)
            result = self._get_value(inst.value)
            if self.debug:
                print(f"   return {result}")
            return ("return", result)

        elif isinstance(inst, Call):
            self._set_register(inst.result, None)

        elif isinstance(inst, CallExtern):
            args = []
            for arg in inst.args:
                args.append(self._get_value(arg))

            key = f"{inst.module}.{inst.function}"

            if self.program is None:
                raise RuntimeError("VM 未注册 Program，无法调用外部函数")

            if key not in self.program.exports:
                raise RuntimeError(f"未找到导出函数: {key}")

            symbol = self.program.exports[key]

            if self.debug:
                print(f"   call {key}{tuple(args)}")

            # 从 program 中获取模块
            if symbol.module not in self.program.modules:
                raise RuntimeError(f"模块 {symbol.module} 不存在")

            target_ir = self.program.modules[symbol.module]

            # 递归调用
            value = self.call(target_ir, symbol.name, *args)

            if self.debug:
                print(f"   call {key} -> {value}")

            self._set_register(inst.result, value)

        elif isinstance(inst, Compare):
            left = self._get_value(inst.left)
            right = self._get_value(inst.right)
            if self.debug:
                print(f"   cmp {inst.left} {inst.op} {inst.right} -> left={left}, right={right}")
            if inst.op == ">":
                self._set_register(inst.result, left > right)
            elif inst.op == "<":
                self._set_register(inst.result, left < right)
            elif inst.op == "==":
                self._set_register(inst.result, left == right)
            else:
                self._set_register(inst.result, False)

        elif isinstance(inst, Branch):
            cond = self._get_value(inst.condition)
            if self.debug:
                print(f"   branch {inst.condition} ({cond}) -> {inst.true_block} : {inst.false_block}")
            if cond:
                target = blocks.get(inst.true_block)
            else:
                target = blocks.get(inst.false_block)
            if target:
                return ("branch", target)
            else:
                raise ValueError(f"分支目标不存在")

        elif isinstance(inst, Jump):
            if self.debug:
                print(f"   jump {inst.target}")
            return "jump"

        return None
