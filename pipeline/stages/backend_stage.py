"""BackendStage - 后端生成阶段"""

from pipeline.stage_base import PipelineStage


class BackendStage(PipelineStage):
    name = "Backend"

    def run(self, ctx):
        print(f"▶ {self.name}")
        backend = ctx.backend
        ir_modules = ctx.ir_modules

        if backend and ir_modules:
            for ir in ir_modules:
                artifact = backend.emit(ir)
                ctx.add_artifact(artifact)
            print(f"  ✅ {self.name} 完成: {len(ir_modules)} 个产物")
        else:
            print(f"  ⏭ {self.name} 跳过")
