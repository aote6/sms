"""SSA 核心数据结构"""

from dataclasses import dataclass, field
from typing import Dict
from compiler_ssa.value import SSAValue as BaseSSAValue


# 重新导出 SSAValue
SSAValue = BaseSSAValue


class SSAValueGenerator:
    """SSA 值生成器，支持从指定 ID 开始"""
    def __init__(self, start=0):
        self._next = start

    def next(self) -> SSAValue:
        v = SSAValue(id=self._next)
        self._next += 1
        return v

    def reset(self):
        self._next = 0


@dataclass
class Phi:
    """Phi 节点 - 用于 SSA 中合并不同路径的值"""
    result: SSAValue
    incomings: Dict[str, SSAValue] = field(default_factory=dict)

    def add(self, block: str, value: SSAValue):
        self.incomings[block] = value

    def __str__(self):
        items = ", ".join(f"{k}:{v}" for k, v in self.incomings.items())
        return f"{self.result} = phi({items})"

    def __repr__(self):
        return self.__str__()
