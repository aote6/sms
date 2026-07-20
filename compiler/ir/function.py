from dataclasses import dataclass, field
from typing import List, Any, Optional
from .block import IRBlock


@dataclass
class IRFunction:
    name: str
    returns: Any
    parameters: List[Any] = field(default_factory=list)
    blocks: List[IRBlock] = field(default_factory=list)
    doc: str = ""  # 添加 doc 属性

    def entry(self):
        if not self.blocks:
            self.blocks.append(IRBlock("entry"))
        return self.blocks[0]

    def add_block(self, name: str) -> IRBlock:
        block = IRBlock(name)
        self.blocks.append(block)
        return block

    def get_block(self, name: str) -> Optional[IRBlock]:
        for b in self.blocks:
            if b.name == name:
                return b
        return None

    def __repr__(self):
        return f"IRFunction(name='{self.name}', blocks={len(self.blocks)})"
