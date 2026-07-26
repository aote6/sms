"""PipelineContext - 流水线上下文"""

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class PipelineContext:
    """统一流水线上下文，所有 Stage 共享"""
    # Session
    session: Any = None

    # 核心组件
    planner: Any = None
    cache: Any = None
    compiler: Any = None
    backend: Any = None
    packager: Any = None
    runtime: Any = None

    # 数据
    modules: List[Any] = field(default_factory=list)
    ir_modules: List[Any] = field(default_factory=list)
    artifacts: List[Any] = field(default_factory=list)
    packages: List[Any] = field(default_factory=list)
    plan: List[Any] = field(default_factory=list)

    # 元数据
    metadata: dict = field(default_factory=dict)

    def add_module(self, module):
        self.modules.append(module)

    def add_ir(self, ir):
        self.ir_modules.append(ir)

    def add_artifact(self, artifact):
        self.artifacts.append(artifact)

    def add_package(self, package):
        self.packages.append(package)

    def summary(self):
        print()
        print("=" * 60)
        print("Pipeline Context")
        print("=" * 60)
        print(f"  modules   : {len(self.modules)}")
        print(f"  ir_modules: {len(self.ir_modules)}")
        print(f"  artifacts : {len(self.artifacts)}")
        print(f"  packages  : {len(self.packages)}")
        print("=" * 60)
