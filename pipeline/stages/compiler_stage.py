"""CompilerStage - 编译阶段"""

from pipeline.stage_base import PipelineStage


class CompilerStage(PipelineStage):
    name = "Compiler"

    def run(self, ctx):
        print(f"▶ {self.name}")
        compiler = ctx.compiler
        modules = ctx.modules

        if compiler and modules:
            compiled = 0
            for module in modules:
                ir = compiler.compile(module)
                ctx.add_ir(ir)
                compiled += 1
            print(f"  ✅ {self.name} 完成: {compiled} 个模块")
        else:
            print(f"  ⏭ {self.name} 跳过")
