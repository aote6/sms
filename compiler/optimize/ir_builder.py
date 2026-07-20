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
        # 从 metadata 中获取原始模块信息
        original_name = artifact.metadata.get("original_module", "Unknown")
        version = artifact.metadata.get("version", "1.0.0")
        capabilities = artifact.metadata.get("capabilities", [])

        # 需要重新构建 Module 对象来获取 capabilities
        # 但由于 ModuleParser 没有传递完整 Module，我们需要重建
        # 这里简化：从 metadata 重建
        ir = IRModule(
            name=original_name,
            version=version,
            runtime="python"
        )

        # 从 metadata 重建 capabilities
        # 注意：这里需要从 artifact.metadata 中获取完整的 capability 信息
        # 暂时跳过，因为实际 flow 中 artifact 应该包含原始 Module

        # 在真实流程中，artifact 应该包含原始 module
        # 这里为了演示，直接创建空 IR
        artifact.module = ir
        artifact.metadata["ir_functions"] = [f.name for f in ir.functions]

        return artifact

    def run_with_passes(self, artifact: IRArtifact, pipeline: PassPipeline) -> IRArtifact:
        artifact = self.run(artifact)
        if artifact.module:
            artifact.module = pipeline.run(artifact.module)
        return artifact
