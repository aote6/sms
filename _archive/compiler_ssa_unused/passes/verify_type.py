"""VerifyType - 类型验证"""

from compiler.passes.base import Pass


class VerifyType(Pass):
    name = "VerifyType"

    def run(self, module):
        print(f"⚙ Pass: {self.name}")

        for fn in module.functions:
            for block in fn.blocks:
                for inst in block.instructions:
                    # 检查所有带 result_type 的指令
                    if hasattr(inst, "result_type"):
                        if inst.result_type is None:
                            raise ValueError(
                                f"{fn.name}: {type(inst).__name__} result_type is None"
                            )
                    # 检查 BinaryOp 的 left_type 和 right_type
                    if hasattr(inst, "left_type") and inst.left_type is None:
                        raise ValueError(
                            f"{fn.name}: {type(inst).__name__} left_type is None"
                        )
                    if hasattr(inst, "right_type") and inst.right_type is None:
                        raise ValueError(
                            f"{fn.name}: {type(inst).__name__} right_type is None"
                        )
                    # 检查 Store 的 value_type
                    if hasattr(inst, "value_type") and inst.value_type is None:
                        raise ValueError(
                            f"{fn.name}: {type(inst).__name__} value_type is None"
                        )
                    # 检查 Return 的 value_type
                    if hasattr(inst, "value_type") and inst.value_type is None:
                        raise ValueError(
                            f"{fn.name}: {type(inst).__name__} value_type is None"
                        )

        return module
