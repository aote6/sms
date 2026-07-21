"""SMS 编译器主入口"""
from compiler_ssa.frontend import ModuleParser
from compiler_ssa.optimize.ir_builder import IRBuilderPass
from compiler_ssa.artifact import IRArtifact
from compiler_ssa.abi_builder import ABIBuilder
from compiler_ssa.passes import (
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
from compiler_ssa.passes.contract_verify import ContractVerify
from compiler_ssa.analysis.dominator import DominatorTree
from compiler_ssa.analysis.frontier import DominanceFrontier
from compiler_ssa.analysis.verify_cfg import CFGVerifier
from compiler_ssa.analysis.callgraph import CallGraph
from compiler_ssa.ssa import SSABuilder
from compiler_ssa.profiler import CompilerProfiler
from compiler_ssa.logging import normal, verbose, debug, LogLevel
from pathlib import Path
import time


class Compiler:
    def __init__(self, debug=False, output_dir="./build", profile=False):
        self.debug = debug
        self.profile = profile
        self.frontend = ModuleParser()
        self.builder = IRBuilderPass(debug=debug)
        self.output_dir = Path(output_dir)
        self.abi_builder = ABIBuilder()
        self._profiler = CompilerProfiler() if profile else None

        self.pipeline = PassPipeline()
        self.pipeline.add(ValidatePass())
        self.pipeline.add(VerifyType())
        self.pipeline.add(ContractVerify())  # 新增：Contract 验证
        self.pipeline.add(ConstantFoldPass())
        self.pipeline.add(DeadCodePass())
        self.pipeline.add(Mem2RegPass())
        self.pipeline.add(CopyPropagationPass())
        self.pipeline.add(VerifySSA())
        self.pipeline.add(GVN())
        self.pipeline.add(Inline())

        self.pass_names = [
            "Validate", "VerifyType", "ContractVerify",
            "ConstantFold", "DeadCode", "Mem2Reg",
            "CopyPropagation", "VerifySSA", "GVN", "Inline",
        ]

    def compile(self, module) -> IRArtifact:
        if self._profiler:
            self._profiler.start_phase("Total")

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

        if self._profiler:
            self._profiler.end_phase()
            self._profiler.start_phase("Optimize")
            artifact.module = self._run_pipeline_with_profile(artifact.module)
            self._profiler.end_phase()
        else:
            artifact.module = self.pipeline.run(artifact.module)

        artifact.verified = True
        artifact.optimized = True
        artifact.metadata["passes"] = self.pass_names

        if self._profiler:
            self._profiler.start_phase("Analysis")

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

        if self._profiler:
            self._profiler.end_phase()

        artifact.ssa = True
        return artifact

    def compile_to_ir(self, module) -> IRArtifact:
        # 保存 Contract 信息到 artifact metadata
        artifact = self.frontend.parse(module)
        if hasattr(module, 'contract') and module.contract:
            artifact.metadata['contract'] = module.contract
        return artifact

    def _run_pipeline_with_profile(self, module):
        current = module
        for p in self.pipeline._passes:
            start = time.perf_counter()
            current = p.run(current)
            duration = (time.perf_counter() - start) * 1000
            if self._profiler:
                self._profiler.record_pass(
                    name=p.name, duration_ms=duration, before=0, after=0
                )
        return current
