"""CompilerStage - 编译模块"""

from pipeline.stage import Stage


class CompilerStage(Stage):
    name = "Compiler"

    def run(self, context):
        if context.skip_build:
            print("  skip compile")
            return

        session = context.session
        compiler = context.compiler
        module = context.module

        if compiler and module:
            ir = compiler.compile(module)
            context.ir = ir
            session.add_module(module)
            session.add_ir(ir)
            print(f"  compile {module.name}")
        else:
            print("  (跳过)")
