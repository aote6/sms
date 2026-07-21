"""SMS IR 类型系统"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    name: str

    def __str__(self):
        return self.name


# 基本类型
VOID = Type("void")
BOOL = Type("bool")
INT = Type("int")
FLOAT = Type("float")
STRING = Type("str")
ANY = Type("Any")


def infer_type(left: Type, right: Type, op: str) -> Type:
    """推导二元运算的结果类型"""
    if left == INT and right == INT:
        return INT

    if left == FLOAT or right == FLOAT:
        return FLOAT

    if op == "+" and (left == STRING or right == STRING):
        return STRING

    return ANY
