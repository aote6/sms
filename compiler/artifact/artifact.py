"""Artifact - 编译产物"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from module import Module


@dataclass
class Artifact:
    module: Module
    ir: Optional[Any] = None
    source: Optional[str] = None
    binary: Optional[bytes] = None
    runtime: str = "python"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.module.name

    @property
    def version(self) -> str:
        return self.module.version

    def ready(self) -> bool:
        return self.module.ready()
