"""CopyPropagation Pass - 传播 Load 的值"""

from compiler.passes.base import Pass
from compiler.ssa_core import SSAValue


class CopyPropagationPass(Pass):
    name = "CopyPropagation"

    def run(self, module):
        for fn in module.functions:
            replace = {}

            for block in fn.blocks:
                for inst in block.instructions:
                    if type(inst).__name__ == "Load":
                        replace[inst.result] = inst.source

            for block in fn.blocks:
                for inst in block.instructions:
                    if type(inst).__name__ == "BinaryOp":
                        if inst.left in replace:
                            inst.left = replace[inst.left]
                        if inst.right in replace:
                            inst.right = replace[inst.right]

                    if type(inst).__name__ == "Compare":
                        pass

                    if type(inst).__name__ == "Return":
                        pass

        return module
