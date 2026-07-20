"""ABI Repository - 扫描和管理 ABI 文件"""

from pathlib import Path
from .loader import ABILoader
from compiler.abi import ModuleABI


class ABIRepository:
    def __init__(self):
        self.loader = ABILoader()
        self.modules: dict[str, ModuleABI] = {}

    def scan(self, directory):
        """扫描目录下的所有 *.abi.json 文件"""
        self.modules.clear()
        for file in Path(directory).glob("*.abi.json"):
            try:
                abi = self.loader.load(file)
                self.modules[abi.module] = abi
                print(f"  📦 发现模块: {abi.module} v{abi.version}")
            except Exception as e:
                print(f"  ⚠️ 加载失败: {file} - {e}")

    def get(self, name) -> ModuleABI | None:
        return self.modules.get(name)

    def all(self):
        return list(self.modules.values())

    def summary(self):
        print()
        print("=" * 50)
        print("ABI Repository")
        print("=" * 50)
        if not self.modules:
            print("  (空)")
        else:
            for name, abi in self.modules.items():
                exports = [e.name for e in abi.exports]
                imports = [i.name for i in abi.imports]
                print(f"  {name} v{abi.version}")
                print(f"    exports: {', '.join(exports) if exports else '(无)'}")
                print(f"    imports: {', '.join(imports) if imports else '(无)'}")
        print("=" * 50)
