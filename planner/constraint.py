"""Constraint - 约束条件"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Constraint:
    key: str
    value: object

    def match(self, context) -> bool:
        return context.get(self.key) == self.value

    def __repr__(self):
        return f"Constraint({self.key}={self.value})"
