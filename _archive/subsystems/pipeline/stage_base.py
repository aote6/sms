"""PipelineStage - 流水线阶段基类"""

from abc import ABC, abstractmethod
from pipeline.context import PipelineContext


class PipelineStage(ABC):
    name: str = "unknown"

    @abstractmethod
    def run(self, ctx: PipelineContext):
        """执行阶段，使用 PipelineContext"""
        pass

    def __repr__(self):
        return f"PipelineStage(name={self.name})"
