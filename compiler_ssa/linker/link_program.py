"""Link Program - 基于 ABI 的链接"""

from compiler_ssa.abi import ModuleABI, ABIFunction


class LinkProgram:
    def __init__(self):
        self.modules: list[ModuleABI] = []
        self.exports: dict[str, ABIFunction] = {}
        self.imports: dict[str, list[ABIFunction]] = {}
        self.errors: list[str] = []

    def add_module(self, abi: ModuleABI):
        self.modules.append(abi)

    def link(self):
        """执行链接，检查导出/导入匹配"""
        self.exports.clear()
        self.imports.clear()
        self.errors.clear()

        # 收集所有导出
        for abi in self.modules:
            for fn in abi.exports:
                key = f"{abi.module}.{fn.name}"
                if key in self.exports:
                    self.errors.append(f"重复导出: {key}")
                self.exports[key] = fn

        # 收集所有导入
        for abi in self.modules:
            for fn in abi.imports:
                key = f"{abi.module}.{fn.name}"
                if key not in self.imports:
                    self.imports[key] = []
                self.imports[key].append(fn)

        # 验证所有导入都能找到对应的导出
        for abi in self.modules:
            for fn in abi.imports:
                key = f"{abi.module}.{fn.name}"
                # 导入的查找：在导出中查找同名函数
                found = False
                for export_key, export_fn in self.exports.items():
                    if export_fn.name == fn.name:
                        found = True
                        break
                if not found:
                    self.errors.append(f"未找到导入: {fn.name} (来自 {abi.module})")

        return len(self.errors) == 0

    def show(self):
        print()
        print("=" * 50)
        print("Link Program")
        print("=" * 50)

        if self.errors:
            print("❌ 链接失败:")
            for err in self.errors:
                print(f"  ✗ {err}")
        else:
            print("✅ 链接成功")
            print(f"  模块: {[m.module for m in self.modules]}")
            print(f"  导出: {list(self.exports.keys())}")

        print("=" * 50)
