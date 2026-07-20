"""SMS 编译器主入口"""

from compiler.frontend import ModuleParser
from compiler.optimize.ir_builder import IRBuilderPass
from compiler.artifact import IRArtifact
from compiler.linker import Linker
from compiler.passes import (
    PassPipeline,
    ValidatePass,
    ConstantFoldPass,
    DeadCodePass,
    Mem2RegPass,
    CopyPropagationPass,
    VerifySSA,
    GVN,
    Inline,
)
from compiler.analysis.dominator import DominatorTree
from compiler.analysis.frontier import DominanceFrontier
from compiler.analysis.verify_cfg import CFGVerifier
from compiler.analysis.callgraph import CallGraph
from compiler.ssa import SSABuilder


class Compiler:
    def __init__(self, debug=False):
        self.debug = debug
        self.frontend = ModuleParser()
        self.builder = IRBuilderPass(debug=debug)
        self.linker = Linker()

        self.pipeline = PassPipeline()
        self.pipeline.add(ValidatePass())
        self.pipeline.add(ConstantFoldPass())
        self.pipeline.add(DeadCodePass())
        self.pipeline.add(Mem2RegPass())
        self.pipeline.add(CopyPropagationPass())
        self.pipeline.add(VerifySSA())
        self.pipeline.add(GVN())
        self.pipeline.add(Inline())

        self.pass_names = [
            "Validate",
            "ConstantFold",
            "DeadCode",
            "Mem2Reg",
            "CopyPropagation",
            "VerifySSA",
            "GVN",
            "Inline",
        ]

    def compile(self, module) -> IRArtifact:
        artifact = self.compile_to_ir(module)
        return artifact

    def compile_to_ir(self, module) -> IRArtifact:
        artifact = self.frontend.parse(module)
        artifact = self.builder.run(artifact)

        if artifact.module:
            artifact.module = self.pipeline.run(artifact.module)
            artifact.verified = True
            artifact.optimized = True
            artifact.metadata["passes"] = self.pass_names

            # Call Graph
            callgraph = CallGraph()
            callgraph.build(artifact.module)
            artifact.metadata["callgraph"] = callgraph
            callgraph.print_graph()

            for fn in artifact.module.functions:
                verifier = CFGVerifier(fn)
                verifier.verify()

                tree = DominatorTree(fn)
                tree.build()
                fn.dominator = tree

                frontier = DominanceFrontier(fn)
                frontier.build()
                fn.frontier = frontier
                frontier.print_frontier()

                ssa = SSABuilder()
                ssa.build(fn)

            artifact.ssa = True

        return artifact

    def compile_and_link(self, modules):
        artifacts = []
        for m in modules:
            artifact = self.compile_to_ir(m)
            artifacts.append(artifact)

        ir_modules = [a.module for a in artifacts if a.module is not None]
        program = self.linker.link(ir_modules)

        if not program.is_linked():
            print(f"❌ 链接失败，未定义: {program.undefined}")
            return None

        print(f"✅ 链接成功: {len(program.modules)} 模块, {len(program.exports)} 导出")

        if artifacts:
            artifact = artifacts[0]
            artifact.metadata["linked"] = True
            artifact.metadata["modules"] = list(program.modules.keys())
            return artifact

        return None
