"""Dominator Tree - 支配树构建"""

from compiler_ssa.analysis.cfg import ControlFlowGraph


class DominatorTree:
    def __init__(self, function):
        self.function = function
        self.cfg = ControlFlowGraph().build(function)
        self.dom = {}  # block_name -> set(block_names)
        self.idom = {}  # block_name -> block_name or None

    def build(self):
        blocks = self.function.blocks
        entry = self.function.entry()
        entry_name = entry.name

        # 初始化：entry 只支配自己，其他支配所有
        block_names = [b.name for b in blocks]
        for b in blocks:
            if b == entry:
                self.dom[b.name] = {b.name}
            else:
                self.dom[b.name] = set(block_names)

        changed = True
        while changed:
            changed = False

            for block in blocks:
                if block == entry:
                    continue

                preds = self.cfg.predecessors(block.name)
                if not preds:
                    continue

                # 交集：所有前驱支配集的交集
                pred_doms = [self.dom[p] for p in preds if p in self.dom]
                if not pred_doms:
                    continue

                new = set(pred_doms[0])
                for d in pred_doms[1:]:
                    new &= d

                new.add(block.name)

                if new != self.dom[block.name]:
                    self.dom[block.name] = new
                    changed = True

        self._compute_idom()
        return self

    def _compute_idom(self):
        """计算立即支配者 (IDom)"""
        entry = self.function.entry()
        entry_name = entry.name

        for block in self.function.blocks:
            block_name = block.name
            if block == entry:
                self.idom[block_name] = None
                continue

            candidates = self.dom[block_name] - {block_name}
            if not candidates:
                self.idom[block_name] = None
                continue

            # 找到最近支配者：在 candidates 中，不被其他 candidate 支配的
            parent = None
            for d in candidates:
                ok = True
                for other in candidates:
                    if other == d:
                        continue
                    if d in self.dom.get(other, set()):
                        ok = False
                        break
                if ok:
                    parent = d
                    break

            self.idom[block_name] = parent

    def dominates(self, a: str, b: str) -> bool:
        """检查 a 是否支配 b"""
        if a not in self.dom:
            return False
        return a in self.dom.get(b, set())

    def get_dominators(self, block_name: str) -> set:
        """获取 block 的所有支配者"""
        return self.dom.get(block_name, set())

    def get_idom(self, block_name: str):
        """获取 block 的立即支配者"""
        return self.idom.get(block_name)

    def get_block_by_name(self, name: str):
        for b in self.function.blocks:
            if b.name == name:
                return b
        return None

    def print_tree(self):
        """打印支配树"""
        print()
        print("=" * 50)
        print("Dominator Tree")
        print("=" * 50)
        for block in self.function.blocks:
            idom_name = self.idom.get(block.name)
            dom_names = sorted(self.dom.get(block.name, set()))
            print(f"  {block.name:10} idom={str(idom_name):10} dom={dom_names}")
        print("=" * 50)
