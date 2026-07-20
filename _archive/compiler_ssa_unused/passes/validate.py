from .base import Pass

class ValidatePass(Pass):
    name = "Validate"

    def run(self, module):
        names = set()
        for fn in module.functions:
            if fn.name in names:
                raise ValueError(f"duplicate function: {fn.name}")
            names.add(fn.name)

        # 检查参数
        for fn in module.functions:
            param_names = set()
            for p in fn.parameters:
                if p.name in param_names:
                    raise ValueError(f"duplicate parameter: {p.name} in {fn.name}")
                param_names.add(p.name)

        return module
