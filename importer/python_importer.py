import ast
import os
from pathlib import Path
from module import Module, PackageType, Origin
from module.capability import Capability
from module.contract import Contract
from module.evidence import Evidence


class PythonImporter:
    """将 Python 源文件导入为 Standard Module"""

    def import_file(self, filepath: str) -> Module:
        path = Path(filepath)
        with open(path) as f:
            source = f.read()

        tree = ast.parse(source)

        module = Module(
            name=path.stem,
            version="0.1.0",
            package_type=PackageType.IMPORTED,
            origin=Origin.IMPORTED,
            author=self._extract_author(path),
            capabilities=self._extract_capabilities(tree),
            contract=self._extract_contract(tree),
            evidence=Evidence()
        )

        return module

    def _extract_capabilities(self, tree: ast.AST) -> list:
        """提取所有函数和类作为能力"""
        caps = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('_') and node.name != '__init__':
                    continue
                caps.append(Capability(
                    name=node.name,
                    description=ast.get_docstring(node) or f"函数: {node.name}",
                    input_type=self._extract_type(node, "input"),
                    output_type=self._extract_type(node, "output")
                ))
            elif isinstance(node, ast.ClassDef):
                caps.append(Capability(
                    name=node.name,
                    description=ast.get_docstring(node) or f"类: {node.name}",
                    input_type="any",
                    output_type="instance"
                ))

        return caps

    def _extract_contract(self, tree: ast.AST) -> Contract:
        """提取模块契约"""
        imports = []
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        return Contract(
            inputs=functions,
            outputs=classes if classes else functions,
            constraints=[],
            runtime="python"
        )

    def _extract_type(self, node, kind: str) -> str:
        """从函数签名提取类型信息"""
        if isinstance(node, ast.FunctionDef):
            if kind == "input":
                args = [a.arg for a in node.args.args if a.arg != 'self']
                return ", ".join(args) if args else "none"
            elif kind == "output":
                if node.returns:
                    return ast.unparse(node.returns)
                return "any"
        return "any"

    def _extract_author(self, path: Path) -> str:
        """尝试从文件获取作者信息"""
        try:
            stat = path.stat()
            import pwd
            return pwd.getpwuid(stat.st_uid).pw_name
        except:
            return "unknown"
