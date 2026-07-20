from .base import Pass

class DeadCodePass(Pass):
    name = "DeadCode"

    def run(self, module):
        # 过滤掉以 _dead 开头的函数
        new_functions = []
        for fn in module.functions:
            if fn.name.startswith("_dead"):
                continue
            new_functions.append(fn)

        module.functions = new_functions
        return module
