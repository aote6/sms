"""PlannerStage - 规划阶段"""

from pipeline.stage_base import PipelineStage


class PlannerStage(PipelineStage):
    name = "Planner"

    def run(self, session):
        print(f"▶ {self.name}")
        # 从 session 获取 graph 和 planner
        graph = getattr(session, 'graph', None)
        planner = getattr(session, 'planner', None)

        if graph and planner:
            plan = planner.create(graph)
            session.plan = plan
            print(f"  ✅ {self.name} 完成")
        else:
            print(f"  ⏭ {self.name} 跳过")
