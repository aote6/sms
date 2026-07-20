"""Artifact → IR 构建器 (SSA 版本)"""

from compiler.artifact import IRArtifact
from compiler.ir import IRModule, IRFunction, IRBuilder, Parameter
from compiler.types import ANY
from compiler.passes import PassPipeline


class IRBuilderPass:
    def __init__(self, debug=False):
        self.debug = debug

    def run(self, artifact: IRArtifact) -> IRArtifact:
        """从 artifact 中提取原始模块信息，构建 IR"""
        caps_info = artifact.metadata.get("capabilities", [])
        original_name = artifact.metadata.get("original_module", "Unknown")
        version = artifact.metadata.get("version", "1.0.0")

        ir = IRModule(
            name=original_name,
            version=version,
            runtime="python"
        )

        for cap_info in caps_info:
            cap_name = cap_info.get("name", "unknown")
            params = cap_info.get("parameters", [])
            impl = cap_info.get("implementation", "")

            # 构建 IRFunction
            fn = IRFunction(
                name=cap_name,
                returns=ANY,
            )

            # 添加参数
            for p in params:
                if isinstance(p, tuple):
                    fn.parameters.append(Parameter(p[0], p[1] if len(p) > 1 else ANY))
                else:
                    fn.parameters.append(Parameter(p, ANY))

            # 如果没有参数，添加默认 data 参数
            if not fn.parameters:
                fn.parameters.append(Parameter("data", ANY))

            # 编译函数体
            entry = fn.entry()
            builder = IRBuilder(entry)

            if impl == "add":
                self._compile_add(builder, fn.parameters, fn)
            elif impl == "max":
                self._compile_max(builder, fn.parameters, fn)
            elif impl == "return":
                self._compile_return(builder, fn.parameters)
            else:
                self._compile_default(builder, fn.parameters)

            ir.add_function(fn)

        artifact.module = ir
        artifact.metadata["ir_functions"] = [f.name for f in ir.functions]

        return artifact

    def _compile_add(self, builder, params, fn):
        if len(params) >= 2:
            a = builder.load(params[0].name)
            b = builder.load(params[1].name)
            c = builder.add(a, b)
            builder.ret(c)
        else:
            builder.ret(builder.const(None))

    def _compile_max(self, builder, params, fn):
        if len(params) >= 2:
            a = builder.load(params[0].name)
            b = builder.load(params[1].name)

            yes = fn.add_block("yes")
            no = fn.add_block("no")
            exit_block = fn.add_block("exit")

            cond = builder.cmp_gt(a, b)
            builder.branch(cond, yes, no)

            builder = IRBuilder(yes)
            builder.store("result", a)
            builder.jump(exit_block)

            builder = IRBuilder(no)
            builder.store("result", b)
            builder.jump(exit_block)

            builder = IRBuilder(exit_block)
            result = builder.load("result")
            builder.ret(result)
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
