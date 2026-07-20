"""Reporters - 事件报告器"""

from build.events import (
    ModuleCompiled, ArtifactGenerated, PackageBuilt,
    CacheHit, CacheMiss, ModuleStart,
    SessionStart, SessionFinish, BuildError, BuildWarning
)


class SessionReporter:
    """将事件记录到 BuildSession"""

    def __init__(self, session):
        self.session = session

    def on_module_start(self, event):
        pass  # 不修改计数器，只是开始

    def on_module_compiled(self, event):
        self.session.modules += 1
        self.session.ir_modules += 1

    def on_artifact_generated(self, event):
        self.session.artifacts += 1

    def on_package_built(self, event):
        self.session.packages += 1

    def on_cache_hit(self, event):
        self.session.cache_hits += 1

    def on_cache_miss(self, event):
        self.session.cache_misses += 1

    def on_build_error(self, event):
        self.session.add_error(event.message)

    def on_build_warning(self, event):
        self.session.add_warning(event.message)


class ConsoleReporter:
    """控制台输出报告器"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self._module_count = 0

    def on_session_start(self, event):
        print()
        print("=" * 60)
        print("Build Session Started")
        print("=" * 60)

    def on_session_finish(self, event):
        print()
        print("=" * 60)
        print("Build Session Finished")
        print("=" * 60)

    def on_module_start(self, event):
        self._module_count += 1
        print(f"  [{self._module_count}] 🔨 {event.module}")

    def on_module_compiled(self, event):
        print(f"      ✅ {event.module} 编译完成")

    def on_artifact_generated(self, event):
        print(f"      📦 artifact: {event.path}")

    def on_package_built(self, event):
        print(f"      📦 package: {event.path}")

    def on_cache_hit(self, event):
        print(f"      ⏭ {event.module} (缓存命中)")

    def on_cache_miss(self, event):
        print(f"      🔄 {event.module} (缓存未命中)")

    def on_build_error(self, event):
        print(f"      ❌ {event.message}")

    def on_build_warning(self, event):
        print(f"      ⚠️ {event.message}")
