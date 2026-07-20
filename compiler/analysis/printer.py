"""分析结果打印器"""


class AnalysisPrinter:
    @staticmethod
    def dominator(dom):
        print()
        print("Dominator Tree")
        print("-" * 40)
        for node in sorted(dom):
            print(f"{node:10} ← {sorted(dom[node])}")

    @staticmethod
    def idom(idom):
        print()
        print("Immediate Dominator")
        print("-" * 40)
        for node in sorted(idom):
            parent = idom[node]
            print(f"{node:10} ← {parent}")

    @staticmethod
    def cfg(graph):
        print()
        print("Control Flow Graph")
        print("-" * 40)
        for node in sorted(graph.nodes):
            succ = sorted(graph.successors(node))
            print(f"{node:10} -> {succ}")
