from module import Module
from .ir import IRModule, IRFunction


class IRCompiler:
    def __init__(self, concept_registry=None):
        self.concepts = concept_registry

    def compile(self, module: Module) -> IRModule:
        ir = IRModule(
            name=module.name,
            version=module.version,
            runtime=module.contract.runtime if module.contract else "unknown",
            imports=self._gen_imports(module),
            metadata={
                "quality_state": module.quality_state,
                "package_type": module.package_type,
                "origin": module.origin,
                "capabilities": [c.name for c in module.capabilities]
            }
        )

        for cap in module.capabilities:
            fn = self._compile_capability(cap, module)
            ir.functions.append(fn)

        return ir

    def _compile_capability(self, cap, module) -> IRFunction:
        body = []
        doc = cap.description

        concept = None
        if self.concepts:
            concept = self.concepts.find(cap.name)

        if concept:
            doc = concept.description
            body.append(f"# 概念: {concept.concept_id}")
            body.append(f"# 标准输入: {concept.inputs}")
            body.append(f"# 标准输出: {concept.outputs}")
        else:
            body.append(f"# 能力: {cap.name}")
            body.append(f"# 描述: {cap.description}")
            body.append(f"# 概念: 未注册（建议注册到 Concept Registry）")

        body.append(f"# 输入类型: {cap.input_type}")
        body.append(f"# 输出类型: {cap.output_type}")

        if cap.parameters:
            body.append(f"# 参数: {cap.parameters}")

        if module.contract:
            body.append(f"# 契约约束: {module.contract.constraints}")

        body.append("pass  # TODO: 等待语义实现层填充")

        return IRFunction(
            name=cap.name,
            inputs=[cap.input_type],
            output=cap.output_type,
            doc=doc,
            body=body
        )

    def _gen_imports(self, module: Module) -> list[str]:
        imports = ["from typing import Any"]
        if module.contract and module.contract.runtime == "python":
            imports.append("import json")
        return imports

    def compile_all(self, modules: list[Module]) -> list[IRModule]:
        return [self.compile(m) for m in modules]
