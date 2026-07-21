"""链接器 - 多模块链接 + 依赖解析"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from compiler_ssa.ir import IRModule
from compiler_ssa.symbol import Symbol, IRImport
from compiler_ssa.dependency import DependencyGraph


@dataclass
class LinkedProgram:
    modules: Dict[str, IRModule] = field(default_factory=dict)
    exports: Dict[str, Symbol] = field(default_factory=dict)
    imports: Dict[str, List[IRImport]] = field(default_factory=dict)
    undefined: Set[str] = field(default_factory=set)
    link_order: List[str] = field(default_factory=list)

    def add_module(self, module: IRModule):
        self.modules[module.name] = module

    def add_export(self, symbol: Symbol):
        self.exports[symbol.fullname] = symbol

    def add_import(self, module_name: str, imp: IRImport):
        if module_name not in self.imports:
            self.imports[module_name] = []
        self.imports[module_name].append(imp)

    def check_undefined(self) -> List[str]:
        undefined = []
        all_exports = set(self.exports.keys())

        for module_name, imports in self.imports.items():
            for imp in imports:
                fullname = imp.fullname
                if fullname not in all_exports:
                    undefined.append(fullname)

        self.undefined = set(undefined)
        return undefined

    def is_linked(self) -> bool:
        return len(self.check_undefined()) == 0

    def show(self):
        print("\n" + "=" * 60)
        print("LINKED PROGRAM")
        print("=" * 60)

        print(f"\n📦 模块 ({len(self.modules)}):")
        for name in self.link_order or list(self.modules.keys()):
            m = self.modules[name]
            print(f"    {name} v{m.version} ({len(m.functions)} functions)")

        print(f"\n🔗 导出 ({len(self.exports)}):")
        for fullname in sorted(self.exports.keys()):
            print(f"    {fullname}")

        print(f"\n📥 导入 ({len(self.imports)}):")
        for module_name, imports in self.imports.items():
            for imp in imports:
                print(f"    {module_name} -> {imp.fullname}")

        if self.undefined:
            print(f"\n❌ 未定义符号 ({len(self.undefined)}):")
            for sym in sorted(self.undefined):
                print(f"    {sym}")
        else:
            print("\n✅ 所有符号已解析")

        print("\n📋 链接顺序:")
        for i, name in enumerate(self.link_order or [], 1):
            print(f"    {i}. {name}")
        print("=" * 60)


class Linker:
    def __init__(self):
        self.program = LinkedProgram()
        self.dep_graph = DependencyGraph()

    def link(self, modules: List[IRModule]) -> LinkedProgram:
        """链接多个模块"""
        self.program = LinkedProgram()
        self.dep_graph = DependencyGraph()

        for m in modules:
            self.program.add_module(m)

            # 导出所有函数
            for fn in m.functions:
                symbol = Symbol(m.name, fn.name)
                if symbol.fullname in self.program.exports:
                    raise ValueError(f"duplicate symbol: {symbol.fullname}")
                self.program.add_export(symbol)

            # 收集导入
            for imp in m.imports:
                self.program.add_import(m.name, imp)
                # 添加到依赖图
                self.dep_graph.add(m.name, imp.module)

        # 拓扑排序
        try:
            self.program.link_order = self.dep_graph.topo_sort()
        except ValueError as e:
            print(f"❌ {e}")
            self.program.link_order = list(self.program.modules.keys())

        # 检查未定义符号
        self.program.check_undefined()

        return self.program

    def link_one(self, module: IRModule) -> LinkedProgram:
        return self.link([module])
