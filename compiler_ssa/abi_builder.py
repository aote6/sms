"""ABI Builder - 从 IR 导出 ABI"""

from compiler_ssa.abi import ModuleABI, ABIFunction, ABIParameter


class ABIBuilder:
    def build(self, ir) -> ModuleABI:
        """从 IRModule 构建 ABI"""
        abi = ModuleABI(
            module=ir.name,
            version=ir.version,
        )

        for fn in ir.functions:
            params = []
            for p in fn.parameters:
                p_type = str(p.type) if hasattr(p, 'type') and p.type else "Any"
                params.append(ABIParameter(
                    name=p.name,
                    type=p_type,
                ))

            returns = str(fn.returns) if hasattr(fn, 'returns') and fn.returns else "void"

            abi.exports.append(
                ABIFunction(
                    name=fn.name,
                    params=params,
                    returns=returns,
                )
            )

        for imp in getattr(ir, 'imports', []):
            abi.imports.append(
                ABIFunction(
                    name=imp.function if hasattr(imp, 'function') else str(imp),
                    params=[],
                    returns="Any",
                )
            )

        return abi

    def build_from_artifact(self, artifact) -> ModuleABI:
        """从 IRArtifact 构建 ABI"""
        if artifact.module is None:
            return ModuleABI(
                module=artifact.metadata.get("original_module", "Unknown"),
                version=artifact.metadata.get("version", "1.0.0"),
            )
        return self.build(artifact.module)

    def build_from_snapshot(self, module_name: str, version: str, functions: list) -> ModuleABI:
        """从函数快照构建 ABI（用于 Pass 后 module 丢失的情况）"""
        abi = ModuleABI(
            module=module_name,
            version=version,
        )

        for fn_info in functions:
            params = []
            for p in fn_info.get("params", []):
                params.append(ABIParameter(
                    name=p.get("name", ""),
                    type=p.get("type", "Any"),
                ))

            abi.exports.append(
                ABIFunction(
                    name=fn_info.get("name", ""),
                    params=params,
                    returns=fn_info.get("returns", "void"),
                )
            )

        return abi
