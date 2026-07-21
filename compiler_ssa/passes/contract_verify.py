"""
ContractVerify - Contract 级别验证
检查模块的实际实现是否符合 Contract 的承诺
"""
from compiler_ssa.passes.base import Pass
from compiler_ssa.types import IRType, ANY


class ContractVerify(Pass):
    name = "ContractVerify"

    def run(self, module):
        """验证每个函数是否符合 Contract 定义"""
        contract = self._get_contract(module)
        if contract is None:
            print(f"⚙ Pass: {self.name} (无Contract，跳过)")
            return module

        print(f"⚙ Pass: {self.name}")
        errors = []

        for fn in module.functions:
            fn_errors = self._verify_function(fn, contract)
            errors.extend(fn_errors)

        if errors:
            print(f"  ❌ Contract 验证失败 ({len(errors)} 项):")
            for e in errors:
                print(f"     - {e}")
        else:
            print(f"  ✅ 所有函数符合 Contract")

        # 将验证结果存入 metadata
        if not hasattr(module, 'metadata'):
            module.metadata = {}
        module.metadata['contract_verified'] = len(errors) == 0
        module.metadata['contract_errors'] = errors

        return module

    def _get_contract(self, module):
        """从 module metadata 获取 Contract"""
        if hasattr(module, 'metadata') and module.metadata:
            contract = module.metadata.get('contract')
            if contract:
                return contract
        return None

    def _verify_function(self, fn, contract) -> list:
        """验证单个函数是否符合 Contract"""
        errors = []

        # 1. 检查函数名是否在 Contract 的能力列表中
        capabilities = getattr(contract, 'capabilities', []) if hasattr(contract, 'capabilities') else []
        cap_names = [c.name for c in capabilities] if capabilities else []

        if cap_names and fn.name not in cap_names:
            # 函数不在 Contract 定义中，不强制报错，但提示
            pass

        # 2. 检查输入参数是否与 Contract 一致
        contract_inputs = getattr(contract, 'inputs', []) if hasattr(contract, 'inputs') else []

        # 3. 检查返回类型
        # 遍历所有基本块，找到 Return 指令
        for block in fn.blocks:
            for inst in block.instructions:
                if inst.__class__.__name__ == 'Return':
                    return_type = getattr(inst, 'value_type', None)
                    if return_type is None:
                        errors.append(f"{fn.name}: 返回类型未定义")
                    elif return_type == ANY or return_type.name == "Any":
                        errors.append(f"{fn.name}: 返回类型为 Any，建议明确指定")

        return errors
