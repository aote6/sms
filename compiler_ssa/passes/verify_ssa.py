"""SSA 验证器 - 检查每个值只被定义一次"""

from compiler_ssa.passes.base import Pass


class VerifySSA(Pass):
    name = "VerifySSA"

    def run(self, module):
        seen = set()

        for fn in module.functions:
            for block in fn.blocks:
                # 检查 Phi 节点
                for phi in self._get_phis(block):
                    if phi.result in seen:
                        raise ValueError(f"SSA 违规: {phi.result} 被重复定义")
                    seen.add(phi.result)

                # 检查普通指令
                for inst in block.instructions:
                    if self._is_phi(inst):
                        continue
                    if hasattr(inst, "target"):
                        if inst.target in seen:
                            raise ValueError(f"SSA 违规: {inst.target} 被重复定义")
                        seen.add(inst.target)

        print(f"⚙ Pass: {self.name}")
        return module

    def _get_phis(self, block):
        from compiler_ssa.ssa_core import Phi
        return [inst for inst in block.instructions if isinstance(inst, Phi)]

    def _is_phi(self, inst):
        from compiler_ssa.ssa_core import Phi
        return isinstance(inst, Phi)
