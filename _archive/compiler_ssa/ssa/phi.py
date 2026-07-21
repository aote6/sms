"""Phi 节点插入 (Cytron 算法)"""

from compiler_ssa.ssa_core import Phi
from compiler_ssa.value_factory import ValueFactory


class PhiInserter:
    def insert(self, fn):
        frontier = fn.frontier.df
        variables = self.collect_variables(fn)

        for var, defs in variables.items():
            work = list(defs)
            visited = set()

            while work:
                block_name = work.pop()

                for y_name in frontier.get(block_name, set()):
                    key = (y_name, var)
                    if key in visited:
                        continue
                    visited.add(key)

                    # 创建 Phi 节点
                    result = ValueFactory().create(f"{var}.phi")
                    phi = Phi(result=result)

                    y_block = self._get_block_by_name(fn, y_name)
                    if y_block:
                        preds = fn.dominator.cfg.predecessors(y_name)
                        for pred in preds:
                            # 为每个前驱创建临时 SSAValue
                            temp_val = ValueFactory().create(f"{var}.{pred}")
                            phi.add(pred, temp_val)

                    if y_block:
                        y_block.instructions.insert(0, phi)

                    if y_name not in defs:
                        work.append(y_name)

    def collect_variables(self, fn):
        result = {}

        for block in fn.blocks:
            for inst in block.instructions:
                if type(inst).__name__ == "Store":
                    target = inst.target
                    if target not in result:
                        result[target] = set()
                    result[target].add(block.name)

        return result

    def _get_block_by_name(self, fn, name):
        for b in fn.blocks:
            if b.name == name:
                return b
        return None
