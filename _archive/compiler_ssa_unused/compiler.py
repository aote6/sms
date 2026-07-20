"""SMS 编译器主入口（带 Profile，简洁输出）"""

from compiler.frontend import ModuleParser
from compiler.optimize.ir_builder import IRBuilderPass
from compiler.artifact import IRArtifact
from compiler.abi_builder import ABIBuilder
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
from compiler.profiler import CompilerProfiler
from compiler.logging import normal, verbose, debug, LogLevel
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
        module_name = abi.module.lower()

        abi_file = self.output_dir / f"{module_name}.abi.json"
        abi_file.write_text(abi.to_json(), encoding="utf-8")
        artifact.metadata["abi_file"] = str(abi_file)

        py_file = self.output_dir / f"{module_name}.py"
        if "source" in artifact.metadata:
            py_file.write_text(artifact.metadata["source"], encoding="utf-8")
            artifact.metadata["py_file"] = str(py_file)

        if self._profiler:
            self._profiler.end_phase()
            # 更新统计
            if artifact.module:
                total_inst = sum(len(b.instructions) for f in artifact.module.functions for b in f.blocks)
                total_blocks = sum(len(f.blocks) for f in artifact.module.functions)
                self._profiler.update_stats(
                    modules=1,
                    functions=len(artifact.module.functions),
                    basic_blocks=total_blocks,
                    instructions=total_inst,
                )
            self._profiler.summary()

        return artifact

    def compile_to_ir(self, module) -> IRArtifact:
        if self._profiler:
            self._profiler.start_phase("Parse")
        artifact = self.frontend.parse(module)
        if self._profiler:
            self._profiler.end_phase()

        if self._profiler:
            self._profiler.start_phase("IR Build")
        artifact = self.builder.run(artifact)
        if self._profiler:
            self._profiler.end_phase()

        if artifact.module:
            if self._profiler:
                self._profiler.start_phase("Validate")
            snapshot = []
            for fn in artifact.module.functions:
                snapshot.append({
                    "name": fn.name,
                    "params": [{"name": p.name, "type": str(p.type) if p.type else "Any"} for p in fn.parameters],
                    "returns": str(fn.returns) if fn.returns else "void",
                })
            artifact.metadata["function_snapshot"] = snapshot
            if self._profiler:
                self._profiler.end_phase()

            if self._profiler:
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

    def _run_pipeline_with_profile(self, module):
        current = module
        for p in self.pipeline._passes:
            start = time.perf_counter()
            current = p.run(current)
            duration = (time.perf_counter() - start) * 1000
            if self._profiler:
                self._profiler.record_pass(
                    name=p.name,
                    duration_ms=duration,
                    before=0,
                    after=0
                )
        return current
