from pathlib import Path
from typing import List
from module import Module
from ir.compiler import IRCompiler
from ir.ir import IRModule, IRFunction
from backend.python_backend import PythonBackend


class Builder:
    """将多个标准模块组合构建为完整产品"""

    def __init__(self, output_dir: str = "./build"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.compiler = IRCompiler()
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
            for fn in ir.functions:
                merged.functions.append(fn)

        main_class = main_module.name.replace(' ', '')
        module_names = [ir.name for ir in ir_modules]
        merged.functions.append(IRFunction(
            name="main",
            inputs=[],
            output="None",
            doc=f"产品入口: {product_name}",
            body=[
                f"print(\"产品: {product_name}\")",
                f"print(\"包含模块: {module_names}\")",
                f"instance = {main_class}()",
                f"print(f\"入口模块: {{instance.__class__.__name__}} v{{instance.version}}\")"
            ]
        ))

        return merged
