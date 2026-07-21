"""Artifact - 编译产物"""

from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import json
from typing import Dict, Any


# ============================================================
# IRArtifact - 编译流程中的中间产物
# ============================================================

@dataclass
class IRArtifact:
    """编译产物，包含 IR 及其分析结果"""
    module: Any = None
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


# ============================================================
# Artifact - 最终输出产物（文件）
# ============================================================

@dataclass
class Artifact:
    kind: str
    extension: str
    source: str
    path: str = ""
    sha256: str = ""

    def write(self, outdir: str, module: str) -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        filename = module.lower().replace(' ', '_') + self.extension
        self.path = str(Path(outdir) / filename)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(self.source)
        self.sha256 = hashlib.sha256(
            self.source.encode("utf-8")
        ).hexdigest()
        return self.path

    def to_dict(self):
        return {
            "kind": self.kind,
            "path": self.path,
            "sha256": self.sha256,
        }
