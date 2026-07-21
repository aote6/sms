"""SSA Rename - 变量重命名"""

from collections import defaultdict


class SSARename:
    def __init__(self):
        self.version = defaultdict(int)
        self.stack = defaultdict(list)

    def run(self, fn):
        self.version.clear()
        self.stack.clear()
        self.block_map = {b.name: b for b in fn.blocks}
        self.fn = fn
        self._rename_block(fn.entry())

    def _rename_block(self, block):
        # 1. 先处理 Phi 节点
        created = []
        for phi in self._get_phis(block):
            old = phi.result
            new = self._new_name(old)
            phi.result = new
            self.stack[old].append(new)
            created.append(old)

        new_instructions = []

        for inst in list(block.instructions):
            if self._is_phi(inst):
                continue

            # 处理定义（Store）
            if hasattr(inst, "target"):
                old = inst.target
                new = self._new_name(old)
                inst.target = new
                self.stack[old].append(new)
                created.append(old)

            # 处理使用
            if hasattr(inst, "source") and inst.source:
                inst.source = self._lookup(inst.source)

            if hasattr(inst, "left"):
                inst.left = self._lookup(inst.left)

            if hasattr(inst, "right"):
                inst.right = self._lookup(inst.right)

            if hasattr(inst, "value") and inst.value:
                inst.value = self._lookup(inst.value)

            if hasattr(inst, "args"):
                inst.args = [self._lookup(a) for a in inst.args]

            if hasattr(inst, "condition"):
                inst.condition = self._lookup(inst.condition)

            new_instructions.append(inst)

        block.instructions = new_instructions

        # 2. 更新后继块的 Phi 输入
        for succ_name in self._get_successors(block):
            succ = self.block_map.get(succ_name)
            if succ:
                for phi in self._get_phis(succ):
                    # 使用当前栈顶版本
                    base = phi.result.split(".")[0] if "." in phi.result else phi.result
                    if base in self.stack and self.stack[base]:
                        phi.incomings[block.name] = self.stack[base][-1]

        # 3. 递归处理后继
        for succ_name in self._get_successors(block):
            succ = self.block_map.get(succ_name)
            if succ:
                self._rename_block(succ)

        # 4. 离开块时弹栈
        for old in reversed(created):
            if old in self.stack and self.stack[old]:
                self.stack[old].pop()

    def _new_name(self, name):
        n = self.version[name]
        self.version[name] += 1
        return f"{name}.{n}"

    def _lookup(self, value):
        if value is None:
            return None
        if not isinstance(value, str):
            return value

        base = value.split(".")[0] if "." in value else value
        if base not in self.stack:
            return value
        if not self.stack[base]:
            return value
        return self.stack[base][-1]

    def _get_successors(self, block):
        successors = []
        for inst in block.instructions:
            if hasattr(inst, "true_block"):
                successors.append(inst.true_block)
            if hasattr(inst, "false_block"):
                successors.append(inst.false_block)
            if inst.__class__.__name__ == "Jump":
                successors.append(inst.target)
        return successors

    def _get_phis(self, block):
        from compiler_ssa.ssa_core import Phi
        return [inst for inst in block.instructions if isinstance(inst, Phi)]

    def _is_phi(self, inst):
        from compiler_ssa.ssa_core import Phi
        return isinstance(inst, Phi)
