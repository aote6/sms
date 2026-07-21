"""SSA Value - 静态单赋值值"""

from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class SSAValue:
    """SSA 值，每个值只被赋值一次"""
    id: int
    name: str = "v"

    def __repr__(self):
        return f"%{self.id}"

    def __str__(self):
        return f"%{self.id}"
