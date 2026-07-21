"""ABI Builder - 从 IR 构建 ABI 接口定义"""
from compiler_ssa.abi import ModuleABI, ABIFunction


class ABIBuilder:
    def build(self, ir) -> ModuleABI:
        functions = []
        # IRModuleNode 用 body, 其他可能用 functions
        fn_list = getattr(ir, 'functions', None) or getattr(ir, 'body', [])
        for node in fn_list:
            if hasattr(node, 'name'):
                fn_abi = ABIFunction(
                    name=node.name,
                    inputs=getattr(node, 'params', []),
                    outputs=getattr(node, 'returns', []),
                )
                functions.append(fn_abi)
        return ModuleABI(
            module=ir.name,
            version=ir.version,
            exports=functions
        )

    def build_from_artifact(self, artifact):
        return self.build(artifact.module)

    def build_from_snapshot(self, module_name, version, functions):
        fn_abis = []
        for fn in functions:
            fn_abis.append(ABIFunction(
                name=fn.get('name', 'unknown'),
                inputs=fn.get('inputs', []),
                outputs=fn.get('outputs', []),
            ))
        return ModuleABI(module=module_name, version=version, exports=fn_abis)
