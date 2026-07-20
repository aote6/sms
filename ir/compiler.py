from module import Module
from .ir import IRModule, IRFunction

class IRCompiler:
    def compile(self, module: Module) -> IRModule:
        ir = IRModule(
            name=module.name,
            version=module.version,
            runtime=module.contract.runtime if module.contract else "unknown",
            imports=["from typing import Any"],
            metadata={
                "state": module.state,
                "capabilities": [c.name for c in module.capabilities]
            }
        )
        
        for cap in module.capabilities:
            fn = IRFunction(
                name=cap.name,
                inputs=[cap.input_type],
                output=cap.output_type,
                doc=cap.description,
                body=[
                    f"# TODO: 实现 {cap.name}",
                    f"# 输入: {cap.input_type}",
                    f"# 输出: {cap.output_type}",
                    "return None"
                ]
            )
            ir.functions.append(fn)
        
        return ir
    
    def compile_all(self, modules: list[Module]) -> list[IRModule]:
        return [self.compile(m) for m in modules]
