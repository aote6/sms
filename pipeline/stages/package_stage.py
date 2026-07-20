"""PackageStage - 打包阶段"""

from pipeline.stage_base import PipelineStage


class PackageStage(PipelineStage):
    name = "Package"

    def run(self, ctx):
        print(f"▶ {self.name}")
        packager = ctx.packager
        artifacts = ctx.artifacts

        if packager and artifacts:
            for artifact in artifacts:
                # 从 artifact 获取模块名
                module_name = getattr(artifact, 'module', 'unknown')
                if hasattr(artifact, 'path'):
                    module_name = artifact.path.split('/')[-1].replace('.py', '')
                package = packager.build(module_name, [artifact])
                ctx.add_package(package)
            print(f"  ✅ {self.name} 完成: {len(artifacts)} 个包")
        else:
            print(f"  ⏭ {self.name} 跳过")
