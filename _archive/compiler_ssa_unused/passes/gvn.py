"""GVN - Global Value Numbering 全局值编号"""

from dataclasses import dataclass
from compiler.passes.base import Pass


@dataclass(frozen=True)
class ValueKey:
    op: str
    lhs: object
    rhs: object


class GVN(Pass):
    name = "GVN"

    def run(self, module):
        print(f"⚙ Pass: {self.name}")

        for fn in module.functions:
            table = {}
            replace = {}
            removed = 0

            for block in fn.blocks:
                new_instructions = []

                for inst in block.instructions:
                    # 处理 Return 的 value
                    if type(inst).__name__ == "Return":
                        if inst.value in replace:
                            inst.value = replace[inst.value]
                        new_instructions.append(inst)
                        continue

                    # 处理 BinaryOp
                    if type(inst).__name__ != "BinaryOp":
                        new_instructions.append(inst)
                        continue

                    lhs = replace.get(inst.left, inst.left)
                    rhs = replace.get(inst.right, inst.right)

                    key = ValueKey(inst.op, lhs, rhs)

                    if key in table:
                        replace[inst.result] = table[key]
                        removed += 1
                        continue

                    table[key] = inst.result
                    new_instructions.append(inst)

                block.instructions = new_instructions

            print(f"  删除重复表达式: {removed}")

        return module
