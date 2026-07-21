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

    def _count_params(self, input_type: str) -> int:
        """根据 input_type 字符串估算参数个数"""
        if not input_type or input_type in ("none", "any", ""):
            return 0
        # "key: str, value: Any" -> 2
        # "code: str" -> 1
        parts = [p.strip() for p in input_type.split(",") if p.strip()]
        return len(parts)

    def _gen_test_args(self, count: int) -> str:
        """生成测试参数"""
        if count == 0:
            return ""
        elif count == 1:
            return '"test_input"'
        elif count == 2:
            return '"test_key", "test_value"'
        else:
            return ", ".join([f'"arg{i}"' for i in range(count)])

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

        # 记录每个函数的参数个数，用于 main 调用
        fn_params = {}
        for ir in ir_modules:
            prefix = ir.name.lower().replace(' ', '_')
            for fn in ir.functions:
                new_name = f"{prefix}_{fn.name}"
                fn.name = new_name
                fn_params[new_name] = self._count_params(fn.inputs[0] if fn.inputs else "")
                merged.functions.append(fn)

        module_names = [ir.name for ir in ir_modules]
        main_body = [
            f"print(\"产品: {product_name}\")",
            f"print(\"包含模块: {module_names}\")",
            "",
            f"results = {{}}",
        ]
        for fn_name, param_count in fn_params.items():
            args = self._gen_test_args(param_count)
            main_body.append(f"# 调用 {fn_name}({args})")
            main_body.append(f"results[\"{fn_name}\"] = self.{fn_name}({args})")
            main_body.append(f"print(f\"  {{results['{fn_name}']}}\")")

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
