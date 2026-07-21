from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class IRBlock:
    name: str
    instructions: List[Any] = field(default_factory=list)

    def append(self, inst):
        self.instructions.append(inst)

    def __iter__(self):
        return iter(self.instructions)

    def __len__(self):
        return len(self.instructions)

    def __repr__(self):
        return f"IRBlock(name='{self.name}', len={len(self)})"
