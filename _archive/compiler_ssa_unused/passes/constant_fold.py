from .base import Pass

class ConstantFoldPass(Pass):
    name = "ConstantFold"

    def run(self, module):
        # 占位实现，后续会添加真正的常量折叠
        # 例如: 1 + 2 → 3
        return module
