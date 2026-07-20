"""IR Verifier - 检查 IR 合法性"""

from compiler.ir.instruction import (
    Load, Store, BinaryOp, Return, Call, Const
)
from compiler.instructions import Branch, Jump, Compare
from compiler.ssa_core import SSAValue


class IRVerifier:
    def verify_function(self, fn):
        defined = set()

        # 参数被视为已定义
        for p in fn.parameters:
            defined.add(p.name)

        for block in fn.blocks:
            for inst in block.instructions:
                if isinstance(inst, Compare):
                    defined.add(inst.result)
                    if not self._is_defined(inst.left, defined):
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.left}' in compare in block '{block.name}'"
                        )
                    if not self._is_defined(inst.right, defined):
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.right}' in compare in block '{block.name}'"
                        )
                    continue

                elif isinstance(inst, Branch):
                    if not self._is_defined(inst.condition, defined):
                        raise ValueError(
                            f"{fn.name}: undefined condition '{inst.condition}' in branch"
                        )
                    continue

                elif isinstance(inst, Jump):
                    continue

                if isinstance(inst, Load):
                    defined.add(inst.result)

                elif isinstance(inst, BinaryOp):
                    if not self._is_defined(inst.left, defined):
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.left}' in block '{block.name}'"
                        )
                    if not self._is_defined(inst.right, defined):
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.right}' in block '{block.name}'"
                        )
                    defined.add(inst.result)

                elif isinstance(inst, Store):
                    if not self._is_defined(inst.value, defined):
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.value}' in store"
                        )

                elif isinstance(inst, Return):
                    if inst.value is not None and not self._is_defined(inst.value, defined):
                        raise ValueError(
                            f"{fn.name}: undefined value '{inst.value}' in return"
                        )

                elif isinstance(inst, Call):
                    defined.add(inst.result)

                elif isinstance(inst, Const):
                    defined.add(inst.result)

        return True

    def _is_defined(self, value, defined):
        if value is None:
            return True
        if isinstance(value, SSAValue):
            return value in defined
        if isinstance(value, str):
            return value in defined
        return False

    def verify_module(self, module):
        for fn in module.functions:
            self.verify_function(fn)
        return True
