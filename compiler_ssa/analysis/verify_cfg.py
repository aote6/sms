"""CFG 验证器 - 检查控制流图结构"""

from compiler_ssa.analysis.cfg import ControlFlowGraph


class CFGVerifier:
    def __init__(self, function):
        self.function = function
        self.cfg = ControlFlowGraph().build(function)

    def verify(self):
        print()
        print("=" * 60)
        print("CFG VERIFY")
        print("=" * 60)

        for block in self.function.blocks:
            succ_names = self.cfg.successors(block.name)
            pred_names = self.cfg.predecessors(block.name)

            succ_blocks = [self._get_block_by_name(n) for n in succ_names]
            pred_blocks = [self._get_block_by_name(n) for n in pred_names]

            print(f"  {block.name:10}")
            print(f"    pred : {[b.name for b in pred_blocks if b]}")
            print(f"    succ : {[b.name for b in succ_blocks if b]}")

        print("=" * 60)

        # 检查入口块是否有前驱
        entry = self.function.entry()
        entry_preds = self.cfg.predecessors(entry.name)
        if entry_preds:
            print(f"⚠️ 入口块 '{entry.name}' 有前驱: {entry_preds}")

        # 检查是否有无法到达的块
        reachable = self._get_reachable(entry.name)
        all_blocks = [b.name for b in self.function.blocks]
        unreachable = set(all_blocks) - reachable
        if unreachable:
            print(f"⚠️ 不可达块: {unreachable}")

        print("=" * 60)
        return self.cfg

    def _get_block_by_name(self, name):
        for b in self.function.blocks:
            if b.name == name:
                return b
        return None

    def _get_reachable(self, start):
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for succ in self.cfg.successors(node):
                if succ not in visited:
                    stack.append(succ)
        return visited
