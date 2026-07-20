"""BuildPlanner - 构建计划器（缓存检查前置）"""

from build.cache_state import CacheState
from build.fingerprint import Fingerprint


class BuildPlanner:
    def __init__(self, cache, registry):
        self.cache = cache
        self.registry = registry
        self._fingerprints = {}

    def plan(self, tasks):
        """检查每个任务的缓存状态，返回 (ready, cached, state_map)"""
        ready = []
        cached = []
        state_map = {}

        for task in tasks:
            module = self.registry.get(task.name)
            if module is None:
                # 无模块，跳过
                state_map[task.name] = CacheState.MISS
                ready.append(task)
                continue

            fp = Fingerprint.module(module)
            self._fingerprints[task.name] = fp

            entry = self.cache.get(task.name) if self.cache else None

            if entry and entry.fingerprint == fp:
                # 缓存命中
                state_map[task.name] = CacheState.HIT
                cached.append(task)
            else:
                # 缓存未命中或指纹不匹配
                state_map[task.name] = CacheState.MISS
                ready.append(task)

        return ready, cached, state_map

    def get_fingerprint(self, module_name: str) -> str | None:
        return self._fingerprints.get(module_name)
