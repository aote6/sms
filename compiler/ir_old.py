"""旧 IR 兼容层 - 用于过渡"""
from dataclasses import dataclass, field
from typing import List, Dict, Any as AnyType, Optional
from compiler.types import IRType, ANY, VOID, Parameter


@dataclass(slots=True)
class IRCapability:
    name: str
    description: str = ""
    function: Optional[object] = None


@dataclass(slots=True)
class IRContract:
    runtime: str = "python"
    thread_safe: bool = False
    deterministic: bool = True
    metadata: Dict[str, AnyType] = field(default_factory=dict)
