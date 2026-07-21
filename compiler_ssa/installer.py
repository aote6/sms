"""Installer - 安装 .smspkg 包"""

from zipfile import ZipFile
from pathlib import Path
import tempfile
import hashlib
import json
from compiler_ssa.repository import PackageRepository


class Installer:
    def __init__(self, repo=None):
        self.repo = repo or PackageRepository()

    def install(self, filename: str, version: str = "1.0.0") -> Path:
        filename = Path(filename)

        if not filename.exists():
            raise FileNotFoundError(f"包文件不存在: {filename}")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # 解包
            with ZipFile(filename, 'r') as z:
                z.extractall(tmp_path)

            # 读取 manifest
            manifest_file = tmp_path / "manifest.json"
            if not manifest_file.exists():
                raise RuntimeError("包中没有 manifest.json")

            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

            # 校验 SHA256
            for f in manifest.get("files", []):
                file_path = tmp_path / f["file"]
                if not file_path.exists():
                    continue
                sha = hashlib.sha256(file_path.read_bytes()).hexdigest()
                if sha != f["sha256"]:
                    raise RuntimeError(f"校验失败: {f['file']}")

            # 获取包名
            package_name = manifest.get("package", "unknown")

            # 安装到仓库
            return self.repo.install(package_name, version, tmp_path)

    def install_package(self, filename: str, version: str = "1.0.0") -> Path:
        """别名"""
        return self.install(filename, version)
