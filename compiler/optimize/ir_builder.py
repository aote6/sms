"""Artifact → IR 构建器 (SSA 版本)"""

from compiler.artifact import Artifact
from compiler.ir import IRModule, IRFunction, IRBuilder, Parameter
from compiler.types import ANY
from compiler.passes import PassPipeline, ValidatePass, ConstantFoldPass, DeadCodePass


class IRBuilderPass:
    def __init__(self, debug=False):
        self.debug = debug
        self.pipeline = PassPipeline()
        self.pipeline.add(ValidatePass())
        self.pipeline.add(ConstantFoldPass())
        self.pipeline.add(DeadCodePass())

    def run(self, artifact: Artifact) -> Artifact:
        module = artifact.module

        ir = IRModule(
            name=module.name,
            version=module.version,
            runtime=artifact.runtime
        )

        for cap in module.capabilities:
            fn = self._compile_capability(cap)
            ir.add_function(fn)

        ir = self.pipeline.run(ir)

        artifact.ir = ir
        artifact.metadata["ir_functions"] = [f.name for f in ir.functions]

        return artifact

    def _compile_capability(self, cap):
        params = []
        if hasattr(cap, 'parameters') and cap.parameters:
            for p in cap.parameters:
                if isinstance(p, tuple):
                    params.append(Parameter(p[0], p[1] if len(p) > 1 else ANY))
                else:
                    params.append(Parameter(p, ANY))
        else:
            params = [Parameter("data", ANY)]

        fn = IRFunction(
            name=cap.name,
            returns=ANY,
            parameters=params,
            doc=cap.description if hasattr(cap, 'description') else ""
        )

        entry = fn.entry()
        builder = IRBuilder(entry)

        impl = getattr(cap, 'implementation', '')
        if impl == "add":
            self._compile_add(builder, params, fn)
        elif impl == "max":
            self._compile_max(builder, params, fn)
        elif impl == "return":
            self._compile_return(builder, params)
        else:
            self._compile_default(builder, params)

        return fn

    def _compile_add(self, builder, params, fn):
        if len(params) >= 2:
            a = builder.load(params[0].name)
            b = builder.load(params[1].name)
            c = builder.add(a, b)
            builder.ret(c)
        else:
            builder.ret(builder.const(None))

    def _compile_max(self, builder, params, fn):
        """编译 max 函数：if a > b then a else b"""
        if len(params) >= 2:
            a = builder.load(params[0].name)
            b = builder.load(params[1].name)

            yes = fn.add_block("yes")
            no = fn.add_block("no")

            cond = builder.cmp_gt(a, b)
            builder.branch(cond, yes, no)

            builder = IRBuilder(yes)
            builder.ret(a)

            builder = IRBuilder(no)
            builder.ret(b)
        else:
            builder.ret(builder.const(None))

    def _compile_return(self, builder, params):
        if params:
            value = builder.load(params[0].name)
            builder.ret(value)
        else:
            builder.ret(builder.const(None))

    def _compile_default(self, builder, params):
        if params:
            value = builder.load(params[0].name)
            builder.ret(value)
        else:
            builder.ret(builder.const(None))
