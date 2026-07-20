from dataclasses import dataclass, field, asdict
from typing import List, Optional

@dataclass
class IRFunction:
    name: str
    inputs: List[str] = field(default_factory=list)
    output: str = "any"
    body: List[str] = field(default_factory=list)
    doc: str = ""
    
    def to_dict(self):
        return asdict(self)

@dataclass
class IRModule:
    name: str
    version: str
    runtime: str
    functions: List[IRFunction] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "name": self.name,
            "version": self.version,
            "runtime": self.runtime,
            "functions": [f.to_dict() for f in self.functions],
            "imports": self.imports,
            "metadata": self.metadata,
        }
