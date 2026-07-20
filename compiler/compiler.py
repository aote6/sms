"""SMS 编译器主入口"""

from compiler.frontend import ModuleParser
from compiler.optimize.ir_builder import IRBuilderPass
from compiler.backend.python_backend import PythonBackend
from compiler.artifact import Artifact
from compiler.linker import Linker
from compiler.symbol import IRImport


class Compiler:
    def __init__(self, debug=False):
        self.debug = debug
        self.frontend = ModuleParser()
        self.middle = IRBuilderPass(debug=debug)
        self.backend = PythonBackend()
        self.linker = Linker()

    def compile(self, module) -> Artifact:
        artifact = self.frontend.parse(module)
        artifact = self.middle.run(artifact)
        artifact = self.backend.emit(artifact)
        return artifact

    def compile_to_ir(self, module) -> Artifact:
        artifact = self.frontend.parse(module)
        artifact = self.middle.run(artifact)
        return artifact

    def compile_and_link(self, modules):
        """编译多个模块并链接"""
        artifacts = []
        for m in modules:
            artifact = self.compile_to_ir(m)
            artifacts.append(artifact)

        # 收集所有 IR
        ir_modules = [a.ir for a in artifacts if a.ir is not None]

        # 链接
        program = self.linker.link(ir_modules)

        # 检查链接状态
        if not program.is_linked():
            print(f"❌ 链接失败，未定义: {program.undefined}")
            return None

        print(f"✅ 链接成功: {len(program.modules)} 模块, {len(program.exports)} 导出")

        # 使用第一个模块的 backend 生成代码（简化）
        if artifacts:
            artifact = artifacts[0]
            artifact.metadata["linked"] = True
            artifact.metadata["modules"] = list(program.modules.keys())
            return artifact

        return None
