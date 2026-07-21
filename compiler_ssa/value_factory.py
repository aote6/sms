"""SSA Value Factory - 生成唯一 SSA 值"""

from compiler_ssa.value import SSAValue


class ValueFactory:
    def __init__(self):
        self.next_id = 0

    def create(self, hint: str = "v") -> SSAValue:
        value = SSAValue(id=self.next_id, name=hint)
        self.next_id += 1
        return value

    def reset(self):
        self.next_id = 0
