"""Plan Node - 规划节点"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class PlanNode:
    id: str
    kind: str  # product, problem, decision, module
    name: str
    children: List['PlanNode'] = field(default_factory=list)
    parents: List['PlanNode'] = field(default_factory=list)
    solved: bool = False
    artifact: Any = None
    metadata: dict = field(default_factory=dict)
    options: List = field(default_factory=list)  # DecisionOption 列表
    selected: Any = None  # 选中的 DecisionOption

    def add(self, node: 'PlanNode'):
        self.children.append(node)
        node.parents.append(self)

    def option(self, opt):
        """添加决策选项"""
        self.options.append(opt)
        return opt

    def __repr__(self):
        return f"PlanNode(id={self.id}, kind={self.kind}, name={self.name})"
