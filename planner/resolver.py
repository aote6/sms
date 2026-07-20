"""DecisionResolver - 决策解析器（多目标评分）"""

from planner.node import PlanNode
from planner.context import BuildContext
from planner.decision import DecisionOption
from planner.module_graph import ModuleGraph
from planner.scoring import Score
from planner.weights import Weights


class DecisionResolver:
    def __init__(self, module_graph: ModuleGraph):
        self.module_graph = module_graph
        self.weights = Weights()

    def resolve(self, node: PlanNode, context: BuildContext) -> DecisionOption:
        if not hasattr(node, 'options') or not node.options:
            raise RuntimeError(f"决策节点 '{node.name}' 没有可用的选项")

        best = None
        best_score = None
        candidates = []

        for option in node.options:
            if not option.available(context):
                continue

            module = self.module_graph.get(option.module.name)
            if module is None:
                continue

            score = self._score_option(option, module)
            option.score = score
            candidates.append((option, module, score))

            if best is None or score.total > best_score.total:
                best = option
                best_score = score

        self._print_candidates(candidates)

        if best is None:
            raise RuntimeError(
                f"决策 '{node.name}' 没有满足约束的可用方案"
            )

        return best

    def _score_option(self, option: DecisionOption, module) -> Score:
        """计算选项的综合评分"""
        s = Score()

        # 1. 优先级
        s.add("priority", option.priority * self.weights.get("priority"))

        # 2. 模块状态
        if hasattr(module, 'state'):
            state_score = self.weights.get(module.state, 0)
            s.add("state", state_score)

        # 3. 测试覆盖率
        if hasattr(module, 'evidence') and module.evidence:
            coverage = getattr(module.evidence, 'coverage', 0)
            s.add("coverage", coverage * self.weights.get("coverage"))

            # 4. 性能基准
            benchmark = getattr(module.evidence, 'benchmark', 0)
            s.add("performance", benchmark * self.weights.get("performance"))

        # 5. 内存占用
        if hasattr(module, 'memory'):
            s.add("memory", module.memory * self.weights.get("memory"))

        # 6. 体积
        if hasattr(module, 'size'):
            s.add("size", module.size * self.weights.get("size"))

        return s

    def _print_candidates(self, candidates):
        """打印候选信息"""
        print()
        print("=" * 50)
        print("Decision Resolver")
        print("=" * 50)

        for option, module, score in sorted(candidates, key=lambda x: x[2].total, reverse=True):
            state = module.state if hasattr(module, 'state') else "unknown"
            print(f"\n  📦 {option.name}")
            print(f"      module : {module.name}")
            print(f"      state  : {state}")

            # 打印各项评分
            for name, value in sorted(score.items.items(), key=lambda x: x[1], reverse=True):
                sign = "+" if value >= 0 else ""
                print(f"      {name:12} {sign}{value:.2f}")

            print(f"      {'TOTAL':12} {score.total:.2f}")

        print()
        print("=" * 50)

    def resolve_all(self, graph, context: BuildContext) -> dict:
        """解析图中所有决策节点"""
        results = {}
        for node in graph.all():
            if node.kind == "decision" and hasattr(node, 'options'):
                try:
                    selected = self.resolve(node, context)
                    node.selected = selected
                    results[node.id] = selected
                except RuntimeError as e:
                    print(f"⚠️ 决策 '{node.name}' 解析失败: {e}")
        return results
