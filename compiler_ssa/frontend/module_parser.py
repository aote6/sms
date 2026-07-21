"""Module -> Artifact 解析器"""
from module import Module
from compiler_ssa.artifact import IRArtifact
from compiler_ssa.ir.module import IRModule


class ModuleParser:
    def parse(self, module: Module) -> IRArtifact:
        caps_info = []
        for c in module.capabilities:
            caps_info.append({
                "name": c.name,
                "description": c.description,
                "parameters": c.parameters if hasattr(c, 'parameters') else [],
                "implementation": c.implementation if hasattr(c, 'implementation') else "",
                "input_type": c.input_type if hasattr(c, 'input_type') else "any",
                "output_type": c.output_type if hasattr(c, 'output_type') else "any",
            })

        ir_module = IRModule(
            name=module.name,
            version=module.version,
            runtime="python",
            metadata={
                "state": module.state if hasattr(module, 'state') else module.quality_state,
                "capabilities": caps_info,
                "original_module": module.name,
                "contract": module.contract,
            }
        )

        return IRArtifact(
            module=ir_module,
            metadata=ir_module.metadata,
            verified=False,
            optimized=False,
            ssa=False,
        )
