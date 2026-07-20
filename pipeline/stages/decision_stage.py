from pipeline.stage import Stage

class DecisionStage(Stage):
    name = "Decision"

    def run(self, context):
        resolver = context.get("resolver")
        decision = context.get("decision")
        build_context = context.get("build_context")

        if resolver and decision and build_context:
            result = resolver.resolve(decision, build_context)
            context.set("selected_decision", result)
            print(f"  selected : {result.name}")
        else:
            print("  (跳过)")
