from pathlib import Path
from typing import List, Optional
from module import Module
from ir.compiler import IRCompiler
from ir.ir import IRModule, IRFunction
from backend.python_backend import PythonBackend
from .param_checker import check_params


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
        if not input_type or input_type in ("none", "any", ""):
            return 0
        parts = [p.strip() for p in input_type.split(",") if p.strip()]
        return len(parts)

    def _gen_test_args(self, count: int) -> str:
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
            name=product_name, version="1.0.0", runtime="python",
            imports=["from typing import Any", "import inspect"],
            metadata={"product": product_name, "modules": [ir.name for ir in ir_modules]}
        )

        fn_params = {}
        for ir in ir_modules:
            prefix = ir.name.lower().replace(' ', '_')
            for fn in ir.functions:
                new_name = f"{prefix}_{fn.name}"
                fn.name = new_name
                fn_params[new_name] = fn.inputs[0] if fn.inputs else ""
                merged.functions.append(fn)

        # 生成 validate 方法 —— 运行时自检
        validate_body = [
            "print(\"🔍 运行时自检...\")",
            "errors = []",
        ]
        for fn_name, input_type in fn_params.items():
            expected = self._count_params(input_type)
            validate_body.append(f"sig = inspect.signature(self.{fn_name})")
            validate_body.append(f"params = [p for p in sig.parameters if p != 'self']")
            validate_body.append(f"if len(params) != {expected}:")
            validate_body.append(f"    errors.append(f\"❌ {fn_name}: 期望{expected}个参数，实际{{len(params)}}个 → 必崩\")")
            validate_body.append(f"else:")
            validate_body.append(f"    print(f\"  ✅ {fn_name}: {{len(params)}}个参数 OK\")")

        validate_body.append("if errors:")
        validate_body.append("    print('\\n'.join(errors))")
        validate_body.append("    return False")
        validate_body.append("print('  ✅ 全部参数验证通过')")
        validate_body.append("return True")

        merged.functions.append(IRFunction(
            name="validate", inputs=[], output="bool",
            doc="运行时自检：验证所有能力函数的参数签名",
            body=validate_body
        ))

        # 生成 main
        module_names = [ir.name for ir in ir_modules]
        main_body = [
            f"print(\"产品: {product_name}\")",
            f"print(\"包含模块: {module_names}\")",
            "",
            "# 先跑自检",
            "if not self.validate():",
            "    print(\"\\n❌ 自检失败，中止运行\")",
            "    return {\"status\": \"validation_failed\"}",
            "",
            "results = {}",
        ]
        for fn_name, input_type in fn_params.items():
            count = self._count_params(input_type)
            args = self._gen_test_args(count)
            main_body.append(f"results[\"{fn_name}\"] = self.{fn_name}({args})")
            main_body.append(f"print(f\"  {{results['{fn_name}']}}\")")

        main_body.append("")
        main_body.append("print(f\"\\n所有能力已执行: {len(results)} 个\")")
        main_body.append("return results")

        merged.functions.append(IRFunction(
            name="main", inputs=[], output="dict",
            doc=f"产品入口: {product_name}", body=main_body
        ))

        return merged
