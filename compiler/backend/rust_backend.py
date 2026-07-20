"""Rust Backend - 生成 Rust 代码"""

from .base import Backend


class RustBackend(Backend):
    name = "rust"
    extension = ".rs"

    def emit_module(self, module) -> str:
        out = []

        out.append(f"pub struct {module.name} {{}}")
        out.append("")

        out.append(f"impl {module.name} {{")
        out.append("    pub fn new() -> Self {")
        out.append("        Self {}")
        out.append("    }")

        for fn in module.functions:
            params = []
            for p in fn.parameters:
                params.append(f"{p.name}: i32")
            sig = ", ".join(params)

            out.append("")
            out.append(f"    pub fn {fn.name}(&self, {sig}) -> i32 {{")
            out.append("        0")
            out.append("    }")

        out.append("}")

        return "\n".join(out)
