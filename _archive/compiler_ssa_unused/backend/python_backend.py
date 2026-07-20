"""Python Backend - 生成合法的 Python 代码"""

from .base import Backend


class PythonBackend(Backend):
    name = "python"
    extension = ".py"

    def emit_module(self, module) -> str:
        out = []

        out.append(f"class {module.name}:")
        out.append("")
        out.append("    def __init__(self):")
        out.append(f"        self.version = '{module.version}'")
        out.append("")

        for fn in module.functions:
            params = ", ".join(["self"] + [p.name for p in fn.parameters])
            out.append(f"    def {fn.name}({params}):")

            if not fn.blocks:
                out.append("        pass")
                out.append("")
                continue

            # 收集所有指令并生成合法的 Python 代码
            for block in fn.blocks:
                for inst in block.instructions:
                    text = self._emit_instruction(inst)
                    if text:
                        out.append(f"        {text}")
                out.append("")

        out.append("")
        out.append("def create():")
        out.append(f"    return {module.name}()")

        return "\n".join(out)

    def _emit_instruction(self, inst) -> str:
        """将 IR 指令转换为合法的 Python 代码"""
        from compiler.ir.instruction import Load, Store, BinaryOp, Return, Call, Const
        from compiler.instructions import Branch, Jump, Compare

        if isinstance(inst, Load):
            # Load: %0 = a → 变量名
            return f"v{inst.result.id} = {inst.source}"
        elif isinstance(inst, BinaryOp):
            # BinaryOp: %2 = + %0 %1 → v2 = v0 + v1
            left = f"v{inst.left.id}" if hasattr(inst.left, 'id') else str(inst.left)
            right = f"v{inst.right.id}" if hasattr(inst.right, 'id') else str(inst.right)
            return f"v{inst.result.id} = {left} {inst.op} {right}"
        elif isinstance(inst, Return):
            if inst.value:
                if hasattr(inst.value, 'id'):
                    return f"return v{inst.value.id}"
                return f"return {inst.value}"
            return "return None"
        elif isinstance(inst, Call):
            args = ", ".join([f"v{a.id}" if hasattr(a, 'id') else str(a) for a in inst.args])
            return f"v{inst.result.id} = {inst.fn_name}({args})"
        elif isinstance(inst, Const):
            return f"v{inst.result.id} = {inst.value}"
        elif isinstance(inst, Store):
            return f"{inst.target} = v{inst.value.id}"
        else:
            return None
