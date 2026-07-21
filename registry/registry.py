from module import Module
from typing import Optional, List
import json
from pathlib import Path


class ModuleRegistry:
    def __init__(self, storage_path: str = "./dist/registry.json"):
        self.modules: dict[str, Module] = {}
        self.storage_path = Path(storage_path)

    def register(self, module: Module):
        self.modules[module.name] = module

    def get(self, name: str) -> Optional[Module]:
        return self.modules.get(name)

    def ready_modules(self) -> List[Module]:
        return [m for m in self.modules.values() if m.ready()]

    def by_state(self, quality_state: str) -> List[Module]:
        return [m for m in self.modules.values() if m.quality_state == quality_state]

    def by_type(self, package_type: str) -> List[Module]:
        return [m for m in self.modules.values() if m.package_type == package_type]

    def by_origin(self, origin: str) -> List[Module]:
        return [m for m in self.modules.values() if m.origin == origin]

    def list_all(self):
        for name, module in self.modules.items():
            status = "✓" if module.ready() else "○"
            print(f"  {status} {name} v{module.version} [{module.quality_state}]")

    def save(self):
        """持久化到 JSON"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for name, m in self.modules.items():
            data[name] = {
                "name": m.name,
                "version": m.version,
                "package_type": m.package_type,
                "quality_state": m.quality_state,
                "origin": m.origin,
                "author": m.author,
                "capabilities": [{"name": c.name, "description": c.description} for c in m.capabilities],
                "submodules": m.submodules,
            }
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Registry 已保存: {self.storage_path} ({len(data)} 模块)")

    def load(self):
        """从 JSON 恢复"""
        if not self.storage_path.exists():
            return
        with open(self.storage_path) as f:
            data = json.load(f)
        for name, d in data.items():
            m = Module(
                name=d["name"],
                version=d["version"],
                package_type=d.get("package_type", "atomic"),
                quality_state=d.get("quality_state", "blank"),
                origin=d.get("origin", "unknown"),
                author=d.get("author", ""),
            )
            self.modules[name] = m
        print(f"Registry 已加载: {len(self.modules)} 模块")
