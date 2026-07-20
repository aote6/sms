"""DependencyResolver - 依赖解析"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple


class DependencyResolver:
    def __init__(self, repository):
        self.repository = repository

    def dependencies(self, package: str, version: str) -> List[dict]:
        """获取包的所有依赖"""
        manifest = self.repository.manifest(package, version)

        abi = None
        for artifact in manifest.get("artifacts", []):
            if artifact["kind"] == "abi":
                abi_path = (
                    self.repository.package_dir(package, version)
                    / Path(artifact["path"]).name
                )
                if abi_path.exists():
                    abi = abi_path
                break

        if abi is None:
            return []

        data = json.loads(abi.read_text(encoding="utf-8"))
        return data.get("imports", [])

    def resolve(self, package: str, version: str) -> List[Tuple[str, str]]:
        """解析所有依赖，返回拓扑排序的依赖列表"""
        visited = set()
        order = []

        def dfs(name: str, ver: str):
            key = (name, ver)
            if key in visited:
                return
            visited.add(key)

            for dep in self.dependencies(name, ver):
                dep_name = dep.get("module", dep.get("name", ""))
                dep_version = dep.get("version", "1.0.0")
                if dep_name:
                    dfs(dep_name, dep_version)

            order.append(key)

        dfs(package, version)
        return order

    def resolve_with_versions(self, package: str, version: str) -> List[dict]:
        """解析依赖，返回包含版本信息的完整列表"""
        order = self.resolve(package, version)
        return [
            {"module": name, "version": ver}
            for name, ver in order
        ]
