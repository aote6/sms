"""IR Verifier - 检查 IR 合法性"""

from compiler.ir.instruction import (
    Load, Store, BinaryOp, Return, Call, Const
)
from compiler.instructions import Branch, Jump, Compare


class IRVerifier:
    def verify_function(self, fn):
        """验证单个函数"""
        defined = set()

        for block in fn.blocks:
            for inst in block.instructions:
                # 处理控制流指令
                if isinstance(inst, Compare):
                    defined.add(inst.result)
                    if inst.left not in defined:
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.left}' in compare in block '{block.name}'"
                        )
                    if inst.right not in defined:
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.right}' in compare in block '{block.name}'"
                        )
                    continue

                elif isinstance(inst, Branch):
                    if inst.condition not in defined:
                        raise ValueError(
                            f"{fn.name}: undefined condition '{inst.condition}' in branch"
                        )
                    continue

                elif isinstance(inst, Jump):
                    continue

                # 原有指令验证
                if isinstance(inst, Load):
                    defined.add(inst.result)

                elif isinstance(inst, BinaryOp):
                    if inst.left not in defined:
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.left}' in block '{block.name}'"
                        )
                    if inst.right not in defined:
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.right}' in block '{block.name}'"
                        )
                    defined.add(inst.result)

                elif isinstance(inst, Store):
                    if inst.value not in defined:
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.value}' in store"
                        )

                elif isinstance(inst, Return):
                    if inst.value is not None and inst.value not in defined:
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.value}' in return"
                        )

                elif isinstance(inst, Call):
                    defined.add(inst.result)

                elif isinstance(inst, Const):
                    defined.add(inst.result)

        return True

    def verify_module(self, module):
        for fn in module.functions:
            self.verify_function(fn)
        return True
