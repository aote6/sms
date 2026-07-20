"""IR Compiler with Pass Pipeline
Module → IRModule → PassPipeline → IRModule
"""

from compiler.ir import (
    IRModule, IRFunction, IRBlock,
    IRBuilder, IRPrinter,
    Constant, Variable,
)
from compiler.passes import PassPipeline, ValidatePass, ConstantFoldPass, DeadCodePass


class IRCompiler:
    def __init__(self, debug=False):
        self.pipeline = PassPipeline()
        self.pipeline.add(ValidatePass())
        self.pipeline.add(ConstantFoldPass())
        self.pipeline.add(DeadCodePass())
        self.debug = debug

    def compile(self, module) -> IRModule:
        ir = IRModule(
            name=module.name,
            version=module.version,
            runtime=module.contract.runtime if module.contract else "python"
        )

        for cap in module.capabilities:
            fn = IRFunction(
                name=cap.name,
                returns="Any",
            )

            entry = fn.entry()
            builder = IRBuilder(entry)

            # 使用 builder 生成代码
            # 简单返回 None
            builder.ret(Constant(None))

            ir.add_function(fn)

        if self.debug:
            printer = IRPrinter()
            printer.print_module(ir)

        return self.pipeline.run(ir)
