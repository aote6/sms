"""Dominance Frontier - 支配边界计算"""


class DominanceFrontier:
    def __init__(self, function):
        self.function = function
        self.df = {}  # block_name -> set(block_names)

    def build(self):
        dom = self.function.dominator
        if dom is None:
            raise ValueError("DominatorTree 未构建")

        # 初始化
        for b in self.function.blocks:
            self.df[b.name] = set()

        cfg = self.function.dominator.cfg

        for block in self.function.blocks:
            # 获取 block 的所有前驱
            preds = cfg.predecessors(block.name)
            pred_blocks = [self._get_block_by_name(p) for p in preds]

            if len(pred_blocks) < 2:
                continue

            for pred in pred_blocks:
                runner = pred
                while runner is not None and runner.name != dom.idom.get(block.name):
                    self.df[runner.name].add(block.name)
                    parent_name = dom.idom.get(runner.name)
                    runner = dom.get_block_by_name(parent_name) if parent_name else None

        return self

    def _get_block_by_name(self, name):
        for b in self.function.blocks:
            if b.name == name:
                return b
        return None

    def get_frontier(self, block_name: str):
        """获取 block 的支配边界"""
        return self.df.get(block_name, set())

    def get_frontier_by_block(self, block):
        """通过 IRBlock 获取支配边界"""
        return self.df.get(block.name, set())

    def print_frontier(self):
        """打印支配边界"""
        print()
        print("=" * 60)
        print("Dominance Frontier")
        print("=" * 60)
        for block in self.function.blocks:
            frontier = sorted(self.df.get(block.name, set()))
            print(f"  {block.name:10} -> {frontier}")
        print("=" * 60)
