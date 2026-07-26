"""RuntimeStage - 运行时阶段"""

from pipeline.stage_base import PipelineStage


class RuntimeStage(PipelineStage):
    name = "Runtime"

    def run(self, ctx):
        print(f"▶ {self.name}")
        runtime = ctx.runtime
        packages = ctx.packages

        if runtime and packages:
            for package in packages:
                runtime.load(package)
            print(f"  ✅ {self.name} 完成: {len(packages)} 个包加载")
        else:
            print(f"  ⏭ {self.name} 跳过")
