"""StageNode - 流水线阶段节点"""

from typing import List, Set
from pipeline.stage_base import PipelineStage


class StageNode:
    def __init__(self, stage: PipelineStage):
        self.stage = stage
        self.deps: List['StageNode'] = []
        self.users: List['StageNode'] = []
        self.done: bool = False
        self.running: bool = False

    @property
    def name(self) -> str:
        return self.stage.name

    def depends_on(self, *nodes: 'StageNode'):
        for node in nodes:
            self.deps.append(node)
            node.users.append(self)

    def ready(self) -> bool:
        return not self.done and not self.running and all(d.done for d in self.deps)

    def __repr__(self):
        dep_names = [d.name for d in self.deps]
        return f"StageNode(name={self.name}, deps={dep_names})"
