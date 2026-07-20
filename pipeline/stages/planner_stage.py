from pipeline.stage import Stage

class PlannerStage(Stage):
    name = "Planner"

    def run(self, context):
        planner = context.get("planner")
        graph = context.get("graph")

        if planner and graph:
            plan = planner.create(graph)
            context.set("plan", plan)
            print(f"  steps : {len(plan)}")
        else:
            print("  (跳过)")
