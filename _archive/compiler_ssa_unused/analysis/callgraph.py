"""Call Graph - 调用图"""


class CallGraph:
    def __init__(self):
        self.graph = {}  # caller -> set(callees)

    def build(self, module):
        self.graph = {}

        for fn in module.functions:
            self.graph[fn.name] = set()

            for block in fn.blocks:
                for inst in block.instructions:
                    if type(inst).__name__ == "Call":
                        self.graph[fn.name].add(inst.fn_name)
                    elif type(inst).__name__ == "CallExtern":
                        # 外部调用标记为 extern
                        self.graph[fn.name].add(f"extern:{inst.module}.{inst.function}")

        return self

    def get_callers(self, fn_name):
        """获取所有调用 fn_name 的函数"""
        result = []
        for caller, callees in self.graph.items():
            if fn_name in callees:
                result.append(caller)
        return result

    def get_callees(self, fn_name):
        """获取 fn_name 调用的所有函数"""
        return list(self.graph.get(fn_name, set()))

    def print_graph(self):
        print()
        print("=" * 50)
        print("Call Graph")
        print("=" * 50)

        for caller in sorted(self.graph.keys()):
            callees = sorted(self.graph[caller])
            if callees:
                print(f"  {caller}:")
                for callee in callees:
                    print(f"    └── {callee}")
            else:
                print(f"  {caller}: (无调用)")

        print("=" * 50)
