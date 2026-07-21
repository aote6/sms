"""C++ Backend - 生成 C++ 代码"""

from .base import Backend


class CppBackend(Backend):
    name = "cpp"
    extension = ".cpp"

    def emit_module(self, module) -> str:
        out = []

        out.append(f"class {module.name}")
        out.append("{")
        out.append("public:")

        # 构造函数
        out.append(f"    {module.name}() {{}}")

        for fn in module.functions:
            params = []
            for p in fn.parameters:
                params.append(f"int {p.name}")
            sig = ", ".join(params)

            out.append(f"    int {fn.name}({sig})")
            out.append("    {")
            out.append("        return 0;")
            out.append("    }")
            out.append("")

        out.append("};")

        return "\n".join(out)
