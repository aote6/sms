"""PipelineRunner - 流水线执行器"""

from typing import List
from pipeline.stage_base import PipelineStage
from pipeline.context import PipelineContext


class PipelineRunner:
    def __init__(self, stages: List[PipelineStage] = None):
        self.stages = stages or []

    def add(self, stage: PipelineStage):
        self.stages.append(stage)
        return self

    def run(self, ctx: PipelineContext):
        print()
        print("=" * 60)
        print("SMS Pipeline")
        print("=" * 60)

        for stage in self.stages:
            try:
                stage.run(ctx)
            except Exception as e:
                print(f"  ❌ {stage.name} 失败: {e}")
                raise

        print()
        print("✅ Pipeline 完成")
        print("=" * 60)
        return ctx
