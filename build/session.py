"""BuildSession - 统一构建会话"""

from dataclasses import dataclass, field
from time import perf_counter
from typing import List
import uuid


@dataclass
class BuildSession:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    start_time: float = field(default_factory=perf_counter)
    end_time: float = 0.0
    status: str = "running"
    modules: int = 0
    ir_modules: int = 0
    artifacts: int = 0
    packages: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def finish(self, status: str = "success"):
        self.status = status
        self.end_time = perf_counter()

    @property
    def duration(self) -> float:
        if self.end_time == 0:
            return perf_counter() - self.start_time
        return self.end_time - self.start_time

    @property
    def duration_ms(self) -> int:
        return int(self.duration * 1000)

    def add_error(self, msg: str):
        self.errors.append(msg)
        self.status = "failed"

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def summary(self):
        print()
        print("=" * 60)
        print("Build Session Summary")
        print("=" * 60)
        print(f"  session_id  : {self.session_id}")
        print(f"  duration    : {self.duration_ms}ms")
        print(f"  status      : {self.status}")
        print(f"  modules     : {self.modules}")
        print(f"  ir_modules  : {self.ir_modules}")
        print(f"  artifacts   : {self.artifacts}")
        print(f"  packages    : {self.packages}")
        print(f"  cache_hits  : {self.cache_hits}")
        print(f"  cache_misses: {self.cache_misses}")
        print(f"  succeeded   : {self.succeeded}")
        print(f"  failed      : {self.failed}")
        print(f"  skipped     : {self.skipped}")
        if self.errors:
            print(f"  errors      : {len(self.errors)}")
        if self.warnings:
            print(f"  warnings    : {len(self.warnings)}")
        print("=" * 60)
