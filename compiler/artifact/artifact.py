"""IR Artifact - 编译产物"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class IRArtifact:
    """编译产物，包含 IR 及其分析结果"""
    module: Any = None  # IRModule
    cfg: Dict[str, Any] = field(default_factory=dict)
    dominator: Dict[str, Any] = field(default_factory=dict)
    frontier: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    verified: bool = False
    optimized: bool = False
    ssa: bool = False

    def summary(self):
        print()
        print("=" * 60)
        print("IR ARTIFACT")
        print("=" * 60)
        if self.module:
            print(f"module : {self.module.name}")
            print(f"version: {self.module.version}")
            print(f"runtime: {self.module.runtime}")
        else:
            print("module : None")
        print(f"ssa    : {self.ssa}")
        print(f"verify : {self.verified}")
        print(f"opt    : {self.optimized}")
        if "passes" in self.metadata:
            print(f"passes : {', '.join(self.metadata['passes'])}")
        print("=" * 60)

    def get_function(self, name: str):
        if self.module:
            for fn in self.module.functions:
                if fn.name == name:
                    return fn
        return None

    def functions(self):
        if self.module:
            return self.module.functions
        return []
