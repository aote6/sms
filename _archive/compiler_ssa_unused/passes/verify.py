from compiler.pass_manager import IRPass


class VerifyPass(IRPass):
    name = "verify"

    def run(self, module):
        names = set()
        for fn in module.functions:
            if fn.name in names:
                raise ValueError(f"重复函数: {fn.name}")
            names.add(fn.name)

        # 检查参数是否有重复名称
        for fn in module.functions:
            param_names = set()
            for p in fn.parameters:
                if p.name in param_names:
                    raise ValueError(f"函数 {fn.name} 有重复参数: {p.name}")
                param_names.add(p.name)

        return module
