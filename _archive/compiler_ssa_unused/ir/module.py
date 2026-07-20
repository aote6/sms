from dataclasses import dataclass, field
from typing import List, Any, Optional
from .function import IRFunction


@dataclass
class IRModule:
    name: str
    version: str
    functions: List[IRFunction] = field(default_factory=list)
    runtime: str = "python"
    metadata: dict = field(default_factory=dict)
    imports: List[Any] = field(default_factory=list)  # IRImport 列表

    def add_function(self, fn: IRFunction):
        self.functions.append(fn)

    def get_function(self, name: str) -> Optional[IRFunction]:
        for fn in self.functions:
            if fn.name == name:
                return fn
        return None

    def add_import(self, imp):
        self.imports.append(imp)

    def __repr__(self):
        return f"IRModule(name='{self.name}', functions={len(self.functions)}, imports={len(self.imports)})"
