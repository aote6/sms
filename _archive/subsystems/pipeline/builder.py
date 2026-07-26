"""BuildPipeline - 构建流水线"""

from pipeline.session import BuildSession
from pipeline.pipeline import Pipeline
from pipeline.context import PipelineContext
import time


class BuildPipeline:
    def __init__(self):
        self.pipeline = Pipeline()
        self.session = BuildSession()

    def add_stage(self, stage):
        self.pipeline.add(stage)
        return self

    def build(self, session: BuildSession = None) -> BuildSession:
        if session is None:
            session = self.session
        else:
            self.session = session

        session.status = "running"
        session.start_time = time.time()

        ctx = PipelineContext()
        ctx.set("session", session)
        ctx.set("graph", session.graph)
        ctx.set("build_context", session.build_context)
        ctx.set("module_registry", session.module_registry)

        try:
            self.pipeline.run(ctx)

            session.plan = ctx.get("plan", [])
            session.selected_decision = ctx.get("selected_decision")
            session.modules = ctx.get("modules", [])
            session.ir_modules = ctx.get("ir_modules", [])
            session.artifacts = ctx.get("artifacts", [])
            session.packages = ctx.get("packages", [])

            session.finish("success")
        except Exception as e:
            session.add_diagnostic(str(e))
            session.finish("failed")
            raise

        session.save()

        return session
