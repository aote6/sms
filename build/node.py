"""BuildNode - 构建节点"""

from dataclasses import dataclass, field


@dataclass
class BuildNode:
    name: str
    deps: set = field(default_factory=set)   # 依赖的节点
    users: set = field(default_factory=set)  # 使用此节点的节点
    dirty: bool = False
    built: bool = False
    visited: bool = False
    metadata: dict = field(default_factory=dict)

    def __repr__(self):
        return f"BuildNode(name={self.name}, dirty={self.dirty})"
