"""Mem2Reg Pass - 将 Load/Store 提升为 SSA 值"""

from compiler.passes.base import Pass


class Mem2RegPass(Pass):
    name = "Mem2Reg"

    def run(self, module):
        for fn in module.functions:
            used = set()

            for block in fn.blocks:
                new_instructions = []

                for inst in block.instructions:
                    # 检查是否是 Load 指令
                    if type(inst).__name__ == "Load":
                        # 记录使用的变量
                        used.add(inst.source)
                        new_instructions.append(inst)
                    else:
                        new_instructions.append(inst)

                block.instructions = new_instructions

        return module
