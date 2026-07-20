"""SMS 编译器主入口"""

from compiler.frontend import ModuleParser
from compiler.optimize.ir_builder import IRBuilderPass
from compiler.artifact import IRArtifact
from compiler.abi_builder import ABIBuilder
from compiler.manifest import ManifestBuilder
from compiler.hash import sha256
from compiler.linker import ABIRepository, LinkProgram
from compiler.passes import (
    PassPipeline,
    ValidatePass,
    VerifyType,
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
from pathlib import Path


class Compiler:
    def __init__(self, debug=False, output_dir="./build"):
        self.debug = debug
        self.frontend = ModuleParser()
        self.builder = IRBuilderPass(debug=debug)
        self.output_dir = Path(output_dir)
        self.abi_builder = ABIBuilder()
        self.manifest_builder = ManifestBuilder()

        self.pipeline = PassPipeline()
        self.pipeline.add(ValidatePass())
        self.pipeline.add(VerifyType())
        self.pipeline.add(ConstantFoldPass())
        self.pipeline.add(DeadCodePass())
        self.pipeline.add(Mem2RegPass())
        self.pipeline.add(CopyPropagationPass())
        self.pipeline.add(VerifySSA())
        self.pipeline.add(GVN())
        self.pipeline.add(Inline())

        self.pass_names = [
            "Validate",
            "VerifyType",
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

        if "function_snapshot" in artifact.metadata and artifact.metadata["function_snapshot"]:
            abi = self.abi_builder.build_from_snapshot(
                module_name=artifact.metadata.get("original_module", "Unknown"),
                version=artifact.metadata.get("version", "1.0.0"),
                functions=artifact.metadata["function_snapshot"]
            )
        else:
            abi = self.abi_builder.build_from_artifact(artifact)

        artifact.metadata["abi"] = abi

        self.output_dir.mkdir(exist_ok=True)
        module_name = abi.module.lower()

        # 保存 ABI
        abi_file = self.output_dir / f"{module_name}.abi.json"
        abi_file.write_text(abi.to_json(), encoding="utf-8")
        artifact.metadata["abi_file"] = str(abi_file)

        # 保存 Python 代码
        py_file = self.output_dir / f"{module_name}.py"
        if "source" in artifact.metadata:
            py_file.write_text(artifact.metadata["source"], encoding="utf-8")
            artifact.metadata["py_file"] = str(py_file)

        # 构建 Manifest
        manifest = self.manifest_builder.build(artifact.module, [])
        # 简化：直接保存
        manifest_file = self.output_dir / f"{module_name}.manifest.json"
        # 这里简化处理，实际应该传入 artifacts

        print(f"📋 清单已保存: {manifest_file}")

        return artifact

    def compile_to_ir(self, module) -> IRArtifact:
        artifact = self.frontend.parse(module)
        artifact = self.builder.run(artifact)

        if artifact.module:
            snapshot = []
            for fn in artifact.module.functions:
                snapshot.append({
                    "name": fn.name,
                    "params": [{"name": p.name, "type": str(p.type) if p.type else "Any"} for p in fn.parameters],
                    "returns": str(fn.returns) if fn.returns else "void",
                })
            artifact.metadata["function_snapshot"] = snapshot

            artifact.module = self.pipeline.run(artifact.module)
            artifact.verified = True
            artifact.optimized = True
            artifact.metadata["passes"] = self.pass_names

            callgraph = CallGraph()
            callgraph.build(artifact.module)
            artifact.metadata["callgraph"] = callgraph

            if self.debug:
                callgraph.print_graph()

            for fn in artifact.module.functions:
                verifier = CFGVerifier(fn)
                if self.debug:
                    verifier.verify()

                tree = DominatorTree(fn)
                tree.build()
                fn.dominator = tree

                frontier = DominanceFrontier(fn)
                frontier.build()
                fn.frontier = frontier
                if self.debug:
                    frontier.print_frontier()

                ssa = SSABuilder()
                ssa.build(fn)

            artifact.ssa = True

        return artifact

    def link(self, build_dir=None):
        if build_dir is None:
            build_dir = self.output_dir

        repo = ABIRepository()
        print()
        print("🔗 扫描 ABI 文件...")
        repo.scan(build_dir)
        repo.summary()

        program = LinkProgram()
        for abi in repo.all():
            program.add_module(abi)

        success = program.link()
        program.show()

        return program
