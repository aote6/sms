from module import Module
from typing import Optional, List


class ModuleRegistry:
    def __init__(self):
        self.modules: dict[str, Module] = {}

    def register(self, module: Module):
        self.modules[module.name] = module

    def get(self, name: str) -> Optional[Module]:
        return self.modules.get(name)

    def ready_modules(self) -> List[Module]:
        """获取所有合格的模块"""
        return [m for m in self.modules.values() if m.ready()]

    def by_state(self, quality_state: str) -> List[Module]:
        """按质量状态筛选"""
        return [m for m in self.modules.values() if m.quality_state == quality_state]

    def by_type(self, package_type: str) -> List[Module]:
        """按封装类型筛选"""
        return [m for m in self.modules.values() if m.package_type == package_type]

    def by_origin(self, origin: str) -> List[Module]:
        """按产地筛选"""
        return [m for m in self.modules.values() if m.origin == origin]

    def list_all(self):
        for name, module in self.modules.items():
            status = "✓" if module.ready() else "○"
            print(f"  {status} {name} v{module.version} [{module.quality_state}]")
