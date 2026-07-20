"""CacheStage - 缓存检查阶段"""

from pipeline.stage_base import PipelineStage


class CacheStage(PipelineStage):
    name = "Cache"

    def run(self, ctx):
        print(f"▶ {self.name}")
        cache = ctx.cache
        modules = ctx.modules

        if cache and modules:
            hits = 0
            for module in modules:
                entry = cache.get(module.name)
                if entry:
                    hits += 1
            print(f"  ✅ {self.name} 完成: {hits} 命中")
        else:
            print(f"  ⏭ {self.name} 跳过")
