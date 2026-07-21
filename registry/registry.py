from module import Module
from typing import Optional, List
import json
from pathlib import Path


"""
模块升级状态机（Status Contract）
=================================

upgrade_module() 和 force_upgrade() 的返回值中，status 字段遵循以下约定：

状态              | 触发条件                     | 数据是否变更 | 副作用
------------------|------------------------------|-------------|----------
blocked           | 存在破坏性变更，未确认       | 否          | 无
blocked (dry_run) | 同上，且 dry_run=True        | 否          | 无（显式声明仅预览）
upgraded_forced   | 破坏性变更，已通过 force 确认 | 是          | 模块已写入，依赖模块标记为需重新验证
warning           | 仅有兼容变更（新增能力等）    | 是          | 模块已写入

破坏性变更判定标准：
- 能力被删除（removed）
- 能力接口变更（input_type/output_type 改变）

兼容变更判定标准：
- 新增能力（added）
- （未来可扩展：deprecated 标记等）

消费者约定：
- AI/调用方应先以 dry_run=True 预览影响，再决定是否提交
- 不得仅凭 status == "warning" 跳过人工确认——warning 表示升级已自动生效，
  调用方应至少记录日志或通知依赖方
- force_upgrade 仅在有明确意图（如"我确认删除 remember"）时使用，
  不应成为绕过检查的默认路径
"""

class ModuleRegistry:
    def __init__(self, storage_path: str = "./dist/registry.json"):
        self.modules: dict[str, Module] = {}
        self.versions: dict[str, list[Module]] = {}
        self.storage_path = Path(storage_path)
        self._force_upgrade = False

    def register(self, module: Module):
        if module.name not in self.versions:
            self.versions[module.name] = []
        existing = [m for m in self.versions[module.name] if m.version == module.version]
        if not existing:
            self.versions[module.name].append(module)
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
        m1 = self.get(name, v1)
        m2 = self.get(name, v2)
        if not m1 or not m2:
            return {"error": "版本不存在"}
        return self._diff_modules(m1, m2, v1, v2)

    def _diff_modules(self, m1: Module, m2: Module, v1: str = "", v2: str = "") -> dict:
        caps1 = {c.name: {"input_type": c.input_type, "output_type": c.output_type} for c in m1.capabilities}
        caps2 = {c.name: {"input_type": c.input_type, "output_type": c.output_type} for c in m2.capabilities}

        added = [n for n in caps2 if n not in caps1]
        removed = [n for n in caps1 if n not in caps2]
        changed = []
        for n in caps1:
            if n in caps2 and caps1[n] != caps2[n]:
                changed.append({"name": n, "old": caps1[n], "new": caps2[n]})

        return {
            "name": m1.name, "v1": v1 or m1.version, "v2": v2 or m2.version,
            "added": added, "removed": removed, "changed": changed,
            "breaking": len(removed) > 0 or len(changed) > 0,
        }

    def upgrade_module(self, module_name: str, new_module: Module, dry_run: bool = False) -> dict:
        old_module = self.get(module_name)
        if not old_module:
            raise ValueError(f"模块 {module_name} 不存在，无法升级")

        diff_result = self._diff_modules(old_module, new_module, old_module.version, new_module.version)
        affected = self._find_dependents(module_name)

        diffs = []
        for cap_name in diff_result.get("removed", []):
            diffs.append({
                "severity": "breaking",
                "type": "removed",
                "capability": cap_name,
                "description": f"能力 {cap_name} 被删除"
            })
        for change in diff_result.get("changed", []):
            diffs.append({
                "severity": "breaking",
                "type": "changed",
                "capability": change["name"],
                "old": change["old"],
                "new": change["new"],
                "description": f"能力 {change['name']} 接口变更: {change['old']} -> {change['new']}"
            })
        for cap_name in diff_result.get("added", []):
            diffs.append({
                "severity": "compatible",
                "type": "added",
                "capability": cap_name,
                "description": f"新增能力 {cap_name}（不影响旧依赖）"
            })

        hard_blocks = []
        soft_warnings = []
        for d in diffs:
            if d["severity"] == "breaking":
                hard_blocks.append({
                    "change": d,
                    "affected_modules": affected,
                    "message": f"{d['description']} —— 影响 {len(affected)} 个依赖模块: {', '.join(affected) if affected else '无'}"
                })
            else:
                soft_warnings.append({
                    "change": d,
                    "message": d["description"]
                })

        # dry_run：只分析不执行
        if dry_run:
            return {
                "status": "blocked" if hard_blocks else ("warning" if soft_warnings else "ok"),
                "diffs": diffs,
                "affected": affected,
                "hard_blocks": hard_blocks,
                "soft_warnings": soft_warnings,
            }

        # 有硬阻断，且不是强制模式 → 拒绝
        if hard_blocks and not self._force_upgrade:
            return {
                "status": "blocked",
                "diffs": diffs,
                "affected": affected,
                "hard_blocks": hard_blocks,
                "soft_warnings": soft_warnings,
                "message": "存在破坏性变更，使用 force_upgrade() 强制升级或先处理依赖",
            }

        # 执行升级
        self.register(new_module)
        for dep in affected:
            self._invalidate_module(dep)

        # 根据实际执行路径设置正确的 status
        if hard_blocks and self._force_upgrade:
            actual_status = "upgraded_forced"
        elif hard_blocks:
            actual_status = "blocked"
        elif soft_warnings:
            actual_status = "upgraded"
        else:
            actual_status = "upgraded"

        return {
            "status": actual_status,
            "diffs": diffs,
            "affected": affected,
            "hard_blocks": hard_blocks,
            "soft_warnings": soft_warnings,
        }

    def force_upgrade(self, module_name: str, new_module: Module) -> dict:
        self._force_upgrade = True
        result = self.upgrade_module(module_name, new_module, dry_run=False)
        self._force_upgrade = False
        return result

    def _find_dependents(self, module_name: str) -> List[str]:
        dependents = []
        for name, mod in self.modules.items():
            if name == module_name:
                continue
            if hasattr(mod, 'submodules') and module_name in (mod.submodules or []):
                dependents.append(name)
            if hasattr(mod, 'contract'):
                deps = getattr(mod.contract, 'dependencies', [])
                if module_name in deps:
                    dependents.append(name)
        return list(set(dependents))

    def _invalidate_module(self, module_name: str) -> None:
        mod = self.modules.get(module_name)
        if mod and hasattr(mod, 'validate'):
            mod._validation_valid = False

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
            if self.versions[name]:
                self.modules[name] = self.versions[name][-1]
