"""BuildSession - 统一构建会话"""

from dataclasses import dataclass, field
from typing import Any, List, Dict
import time
import uuid


@dataclass
class BuildSession:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    started: float = field(default_factory=time.time)
    modules: List[Any] = field(default_factory=list)
    ir_modules: List[Any] = field(default_factory=list)
    artifacts: List[Any] = field(default_factory=list)
    packages: List[Any] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    cache_hits: int = 0
    cache_misses: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_module(self, module):
        self.modules.append(module)

    def add_ir(self, ir):
        self.ir_modules.append(ir)

    def add_artifact(self, artifact):
        self.artifacts.append(artifact)

    def add_package(self, package):
        self.packages.append(package)

    def add_diagnostic(self, msg: str):
        self.diagnostics.append(msg)

    @property
    def duration(self):
        return int((time.time() - self.started) * 1000)

    def summary(self):
        print()
        print("=" * 60)
        print("Build Session")
        print("=" * 60)
        print(f"  session_id : {self.session_id}")
        print(f"  modules    : {len(self.modules)}")
        print(f"  ir_modules : {len(self.ir_modules)}")
        print(f"  artifacts  : {len(self.artifacts)}")
        print(f"  packages   : {len(self.packages)}")
        print(f"  cache_hits : {self.cache_hits}")
        print(f"  cache_miss : {self.cache_misses}")
        print(f"  duration   : {self.duration}ms")
        if self.diagnostics:
            print(f"  diagnostics: {len(self.diagnostics)}")
        print("=" * 60)
