from compiler_ssa.analysis import IRVerifier

class PassPipeline:
    def __init__(self):
        self._passes = []
        self._verifier = IRVerifier()

    def add(self, ir_pass):
        self._passes.append(ir_pass)

    def run(self, module):
        # 初始验证
        self._verifier.verify_module(module)

        for p in self._passes:
            print(f"⚙ Pass: {p.name}")
            module = p.run(module)
            # 每个 Pass 后验证
            self._verifier.verify_module(module)

        return module
