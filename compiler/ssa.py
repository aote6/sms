"""SSA Value - 静态单赋值值"""

from dataclasses import dataclass, field
from typing import Optional, List, Any


@dataclass(frozen=True)
class SSAValue:
    """SSA 值，每个值只被赋值一次"""
    id: int

    def __str__(self):
        return f"%{self.id}"

    def __repr__(self):
        return f"%{self.id}"


class SSAValueGenerator:
    """SSA 值生成器"""
    def __init__(self, start=0):
        self._next = start

    def next(self) -> SSAValue:
        v = SSAValue(self._next)
        self._next += 1
        return v

    def reset(self):
        self._next = 0
