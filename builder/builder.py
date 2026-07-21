from pathlib import Path
from typing import List, Optional
from module import Module
from ir.compiler import IRCompiler
from ir.ir import IRModule, IRFunction
from backend.python_backend import PythonBackend


class Builder:
    def __init__(self, output_dir: str = "./dist", concept_registry=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.compiler = IRCompiler(concept_registry=concept_registry)
        self.backend = PythonBackend(output_dir=self.output_dir)

    def build_product(self, name: str, modules: List[Module], main_module: Module = None) -> Path:
        if main_module is None:
            main_module = modules[0]

        ir_modules = [self.compiler.compile(m) for m in modules]
        merged_ir = self._merge_ir(name, ir_modules, main_module)
        artifact = self.backend.emit(merged_ir)
        return artifact.path

    def _merge_ir(self, product_name: str, ir_modules: List[IRModule], main_module: Module) -> IRModule:
        merged = IRModule(
            name=product_name,
            version="1.0.0",
            runtime="python",
            imports=["from typing import Any"],
            metadata={
                "product": product_name,
                "modules": [ir.name for ir in ir_modules]
            }
        )

        for ir in ir_modules:
            prefix = ir.name.lower().replace(' ', '_')
            for fn in ir.functions:
                fn.name = f"{prefix}_{fn.name}"
                merged.functions.append(fn)

        module_names = [ir.name for ir in ir_modules]
        main_body = [
            f"print(\"产品: {product_name}\")",
            f"print(\"包含模块: {module_names}\")",
            "",
            f"results = {{}}",
        ]
        for ir in ir_modules:
            for fn in ir.functions:
                main_body.append(f"# 调用 {ir.name}.{fn.name}")
                main_body.append(f"results[\"{fn.name}\"] = self.{fn.name}(\"test_input\")")
                main_body.append(f"print(f\"  {{results['{fn.name}']}}\")")

        main_body.append("")
        main_body.append("print(f\"\\n所有能力已执行: {len(results)} 个\")")
        main_body.append("return results")

        merged.functions.append(IRFunction(
            name="main",
            inputs=[],
            output="dict",
            doc=f"产品入口: {product_name}",
            body=main_body
        ))

        return merged
