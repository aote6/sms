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

    def add_function(self, fn: IRFunction):
        self.functions.append(fn)

    def get_function(self, name: str) -> Optional[IRFunction]:
        for fn in self.functions:
            if fn.name == name:
                return fn
        return None

    def __repr__(self):
        return f"IRModule(name='{name}', functions={len(self.functions)})"
