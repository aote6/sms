"""Runtime Loader - 从安装的包加载模块"""

import importlib.util
from pathlib import Path
from typing import Any


class RuntimeLoader:
    def load(self, directory: Path, module: str) -> Any:
        """从目录加载 Python 模块"""
        path = Path(directory) / f"{module.lower()}.py"

        if not path.exists():
            raise FileNotFoundError(f"模块文件不存在: {path}")

        spec = importlib.util.spec_from_file_location(module, path)
        if spec is None:
            raise ImportError(f"无法加载模块: {module}")

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # 尝试调用 create() 工厂函数
        if hasattr(mod, "create"):
            return mod.create()

        # 尝试直接返回模块
        return mod

    def load_from_repo(self, repo, package: str, version: str) -> Any:
        """从仓库加载模块"""
        pkg_path = repo.get_package_path(package, version)
        return self.load(pkg_path, package)
