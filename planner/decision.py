"""Decision - 决策选项"""

from dataclasses import dataclass, field
from typing import List
from planner.constraint import Constraint
from planner.module_ref import ModuleRef


@dataclass
class DecisionOption:
    name: str
    module: ModuleRef
    constraints: List[Constraint] = field(default_factory=list)
    priority: int = 0
    cost: int = 0
    score: int = 0
    metadata: dict = field(default_factory=dict)

    def available(self, context) -> bool:
        for c in self.constraints:
            if not c.match(context):
                return False
        return True

    def __repr__(self):
        return f"DecisionOption(name={self.name}, module={self.module}, priority={self.priority})"
