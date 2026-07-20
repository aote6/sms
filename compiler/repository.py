"""Package Repository - 本地包仓库管理"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


class PackageRepository:
    def __init__(self, root=".smsrepo"):
        self.root = Path(root)
        self.root.mkdir(exist_ok=True)

    def package_dir(self, name: str, version: str) -> Path:
        return self.root / name / version

    def install(self, package_name: str, version: str, source_dir: Path) -> Path:
        dst = self.package_dir(package_name, version)

        if dst.exists():
            shutil.rmtree(dst)

        shutil.copytree(source_dir, dst)

        version_file = dst / ".version"
        version_file.write_text(version)

        return dst

    def installed(self) -> list[tuple[str, str]]:
        result = []
        for pkg in sorted(self.root.iterdir()):
            if not pkg.is_dir():
                continue
            for ver in sorted(pkg.iterdir()):
                if ver.is_dir():
                    result.append((pkg.name, ver.name))
        return result

    def manifest(self, package: str, version: str) -> dict:
        file = self.package_dir(package, version) / "manifest.json"
        if file.exists():
            return json.loads(file.read_text(encoding="utf-8"))
        return {}

    def get_package_path(self, package: str, version: str) -> Path:
        return self.package_dir(package, version)

    def summary(self):
        print()
        print("=" * 50)
        print("Package Repository")
        print("=" * 50)
        installed = self.installed()
        if not installed:
            print("  (空)")
        else:
            for pkg, ver in installed:
                print(f"  {pkg} v{ver}")
        print("=" * 50)
