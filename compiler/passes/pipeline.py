class PassPipeline:
    def __init__(self):
        self._passes = []

    def add(self, ir_pass):
        self._passes.append(ir_pass)

    def run(self, module):
        current = module
        for p in self._passes:
            print(f"⚙ Pass: {p.name}")
            current = p.run(current)
        return current
