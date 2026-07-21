from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Concept:
    """能力概念（借鉴电子元器件型号目录）"""
    concept_id: str
    name: str
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
