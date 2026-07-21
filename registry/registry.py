from module import Module
from typing import Optional, List
import json
from pathlib import Path


class ModuleRegistry:
    def __init__(self, storage_path: str = "./dist/registry.json"):
        self.modules: dict[str, Module] = {}
        self.versions: dict[str, list[Module]] = {}  # name -> [v1, v2, ...]
        self.storage_path = Path(storage_path)

    def register(self, module: Module):
        """注册模块，自动保存版本历史"""
        if module.name not in self.versions:
            self.versions[module.name] = []
        # 如果同版本已存在，跳过
        existing = [m for m in self.versions[module.name] if m.version == module.version]
        if not existing:
            self.versions[module.name].append(module)
        # 最新版本放在 modules 里
        self.modules[module.name] = module
        self.save()

    def get(self, name: str, version: str = None) -> Optional[Module]:
        if version:
            for m in self.versions.get(name, []):
                if m.version == version:
                    return m
            return None
        return self.modules.get(name)

    def get_versions(self, name: str) -> List[Module]:
        return self.versions.get(name, [])

    def get_latest(self, name: str) -> Optional[Module]:
        return self.modules.get(name)

    def diff(self, name: str, v1: str, v2: str) -> dict:
        """比较两个版本的接口差异"""
        m1 = self.get(name, v1)
        m2 = self.get(name, v2)
        if not m1 or not m2:
            return {"error": "版本不存在"}

        caps1 = {c.name: {"input_type": c.input_type, "output_type": c.output_type} for c in m1.capabilities}
        caps2 = {c.name: {"input_type": c.input_type, "output_type": c.output_type} for c in m2.capabilities}

        added = [n for n in caps2 if n not in caps1]
        removed = [n for n in caps1 if n not in caps2]
        changed = []
        for n in caps1:
            if n in caps2 and caps1[n] != caps2[n]:
                changed.append({"name": n, "old": caps1[n], "new": caps2[n]})

        return {
            "name": name, "v1": v1, "v2": v2,
            "added": added, "removed": removed, "changed": changed,
            "breaking": len(removed) > 0 or len(changed) > 0,
        }

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
            versions = self.get_versions(name)
            vlist = ", ".join([v.version for v in versions])
            status = "✓" if module.ready() else "○"
            print(f"  {status} {name} [{vlist}] [{module.quality_state}]")

    def save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for name, mods in self.versions.items():
            data[name] = []
            for m in mods:
                data[name].append({
                    "name": m.name,
                    "version": m.version,
                    "package_type": m.package_type,
                    "quality_state": m.quality_state,
                    "origin": m.origin,
                    "author": m.author,
                    "capabilities": [{"name": c.name, "description": c.description,
                                      "input_type": c.input_type, "output_type": c.output_type}
                                     for c in m.capabilities],
                    "submodules": m.submodules,
                })
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self):
        if not self.storage_path.exists():
            return
        with open(self.storage_path) as f:
            data = json.load(f)
        for name, versions in data.items():
            self.versions[name] = []
            for d in versions:
                m = Module(
                    name=d["name"], version=d["version"],
                    package_type=d.get("package_type", "atomic"),
                    quality_state=d.get("quality_state", "blank"),
                    origin=d.get("origin", "unknown"),
                    author=d.get("author", ""),
                )
                for cap_data in d.get("capabilities", []):
                    m.capabilities.append(
                        __import__('module.capability', fromlist=['Capability']).Capability(
                            name=cap_data["name"],
                            description=cap_data.get("description", ""),
                            input_type=cap_data.get("input_type", "any"),
                            output_type=cap_data.get("output_type", "any"),
                        )
                    )
                m.submodules = d.get("submodules", [])
                self.versions[name].append(m)
            # 最新版本
            if self.versions[name]:
                self.modules[name] = self.versions[name][-1]
