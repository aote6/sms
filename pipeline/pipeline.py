class Pipeline:
    def __init__(self):
        self.stages = []

    def add(self, stage):
        self.stages.append(stage)
        return self

    def run(self, context):
        print()
        print("=" * 60)
        print("SMS Pipeline")
        print("=" * 60)
        for stage in self.stages:
            print(f"▶ {stage.name}")
            stage.run(context)
        print()
        print("✅ Pipeline Finished")
