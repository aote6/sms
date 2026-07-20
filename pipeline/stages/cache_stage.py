"""CacheStage - 缓存检查"""

from pipeline.stage import Stage
from build.fingerprint import Fingerprint


class CacheStage(Stage):
    name = "Cache"

    def run(self, context):
        cache = context.cache
        session = context.session
        module = context.module

        if not cache or not module:
            context.skip_build = False
            print("  (跳过缓存)")
            return

        fp = Fingerprint.module(module)
        old = cache.get(module.name)

        if old == fp:
            session.cache_hits += 1
            context.skip_build = True
            print(f"  HIT  {module.name}")
        else:
            session.cache_misses += 1
            context.skip_build = False
            cache.put(module.name, fp)
            print(f"  MISS {module.name}")
