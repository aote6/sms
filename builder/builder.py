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
        if not input_type or input_type in ("none", "any", ""):
            return 0
        parts = [p.strip() for p in input_type.split(",") if p.strip()]
        return len(parts)

    def _parse_expected_types(self, input_type: str) -> dict:
        result = {}
        if not input_type or input_type in ("none", "any", ""):
            return result
        for part in input_type.split(","):
            part = part.strip()
            if ":" in part:
                name, typ = part.split(":", 1)
                result[name.strip()] = typ.strip()
            else:
                result[part] = "Any"
        return result

    def _gen_test_args(self, count: int) -> str:
        if count == 0:
            return ""
        elif count == 1:
            return '"test_input"'
        elif count == 2:
            return '"test_key", "test_value"'
        else:
            return ", ".join([f'"arg{i}"' for i in range(count)])

    def _get_return_fields(self, cap) -> list:
        """根据 Capability 名称推断必须返回字段"""
        name = cap.name.lower()
        if "toolcode" in name or "tool_code" in name:
            return ["status", "output"]
        elif "memory" in name or "shortterm" in name:
            return ["status"]
        elif "planner" in name or "sequential" in name:
            return ["status", "steps"]
        elif "file" in name:
            return ["status"]
        elif "react" in name:
            return ["status", "action"]
        elif "invoker" in name or "dispatch" in name:
            return ["status"]
        elif "protocol" in name or "request" in name or "message" in name:
            return ["status", "response"]
        elif "debate" in name:
            return ["status", "consensus"]
        else:
            return ["status"]

    def _merge_ir(self, product_name: str, ir_modules: List[IRModule], main_module: Module) -> IRModule:
        merged = IRModule(
            name=product_name, version="1.0.0", runtime="python",
            imports=["from typing import Any, get_type_hints", "import inspect"],
            metadata={"product": product_name, "modules": [ir.name for ir in ir_modules]}
        )

        fn_params = {}
        fn_behaviors = {}  # 记录每个函数对应的 behavior
        for ir in ir_modules:
            prefix = ir.name.lower().replace(' ', '_')
            for fn in ir.functions:
                new_name = f"{prefix}_{fn.name}"
                fn.name = new_name
                fn_params[new_name] = fn.inputs[0] if fn.inputs else ""
                merged.functions.append(fn)

        # 从 main_module 的 capabilities 里读 behavior 信息
        for mod in [main_module] if main_module else []:
            if hasattr(mod, 'capabilities'):
                for cap in mod.capabilities:
                    for fn_name in fn_params:
                        if cap.name.lower() in fn_name.lower():
                            fn_behaviors[fn_name] = self._get_return_fields(cap)

        # 生成 validate 方法
        validate_body = [
            "print(\"🔍 运行时自检...\")",
            "errors = []",
        ]
        for fn_name, input_type in fn_params.items():
            expected_count = self._count_params(input_type)
            expected_types = self._parse_expected_types(input_type)
            required_return_fields = fn_behaviors.get(fn_name, ["status"])

            # 参数个数
            validate_body.append(f"sig = inspect.signature(self.{fn_name})")
            validate_body.append(f"params = [p for p in sig.parameters if p != 'self']")
            validate_body.append(f"if len(params) != {expected_count}:")
            validate_body.append(f"    errors.append(f\"❌ {fn_name}: 期望{expected_count}个参数，实际{{len(params)}}个\")")
            validate_body.append(f"else:")
            validate_body.append(f"    print(f\"  ✅ {fn_name}: {{len(params)}}个参数 OK\")")

            # 参数类型
            if expected_types:
                validate_body.append(f"    hints = get_type_hints(self.{fn_name})")
                for pn, et in expected_types.items():
                    validate_body.append(f"    if '{pn}' in hints:")
                    validate_body.append(f"        at = hints['{pn}'].__name__ if hasattr(hints['{pn}'], '__name__') else str(hints['{pn}'])")
                    validate_body.append(f"        if at.lower() != '{et}'.lower() and '{et}'.lower() != 'any':")
                    validate_body.append(f"            errors.append(f\"⚠️ {fn_name}.{pn}: 类型{{at}}，期望{et}\")")
                    validate_body.append(f"        else:")
                    validate_body.append(f"            print(f\"    ✅ {pn}: {{at}}\")")

            # 返回结构检查：跑一次函数，检查返回值字段
            count = self._count_params(input_type)
            args = self._gen_test_args(count)
            validate_body.append(f"    try:")
            validate_body.append(f"        _result = self.{fn_name}({args})")
            validate_body.append(f"        if not isinstance(_result, dict):")
            validate_body.append(f"            errors.append(f\"❌ {fn_name}: 返回值不是dict，是{{type(_result).__name__}}\")")
            validate_body.append(f"        else:")
            for field in required_return_fields:
                validate_body.append(f'            if "{field}" not in _result:')
                validate_body.append(f'                errors.append("❌ {fn_name}: 返回值缺少必须字段 \\\"{field}\\\"")')
            validate_body.append(f"            else:")
            validate_body.append(f"                print(f\"    ✅ 返回结构 OK (字段: {required_return_fields})\")")
            validate_body.append(f"    except Exception as e:")
            validate_body.append(f"        errors.append(f\"❌ {fn_name}: 调用失败 - {{e}}\")")

        validate_body.append("if errors:")
        validate_body.append("    print('\\n'.join(errors))")
        validate_body.append("    return False")
        validate_body.append("print('  ✅ 全部验证通过')")
        validate_body.append("return True")

        merged.functions.append(IRFunction(
            name="validate", inputs=[], output="bool",
            doc="运行时自检：参数个数+类型+返回结构",
            body=validate_body
        ))

        # main
        module_names = [ir.name for ir in ir_modules]
        main_body = [
            f"print(\"产品: {product_name}\")",
            f"print(\"包含模块: {module_names}\")",
            "",
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

        main_body.append("")
        main_body.append("print(f\"\\n所有能力已执行: {len(results)} 个\")")
        main_body.append("return results")

        merged.functions.append(IRFunction(
            name="main", inputs=[], output="dict",
            doc=f"产品入口: {product_name}", body=main_body
        ))

        return merged
