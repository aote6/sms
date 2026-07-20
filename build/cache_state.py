"""CacheState - 缓存状态"""

from enum import Enum


class CacheState(Enum):
    HIT = "hit"           # 工件可直接复用
    MISS = "miss"         # 没有缓存
    STALE = "stale"       # 指纹变化，需要重建
    INVALID = "invalid"   # 工件损坏或缺失

    def __str__(self):
        return self.value

    def is_usable(self) -> bool:
        return self == CacheState.HIT

    def needs_build(self) -> bool:
        return self in (CacheState.MISS, CacheState.STALE, CacheState.INVALID)
