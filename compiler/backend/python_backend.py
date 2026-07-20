"""Python 后端 - Artifact → Python 源码"""

from pathlib import Path
from compiler.artifact import Artifact
from compiler.python_ast import PythonASTCompiler


class PythonBackend:
    def __init__(self, output_dir: Path = Path("./build")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.ast_compiler = PythonASTCompiler()

    def emit(self, artifact: Artifact) -> Artifact:
        """从 Artifact 生成 Python 源码"""
        if artifact.ir is None:
            raise ValueError(f"Artifact {artifact.name} 没有 IR")

        source = self.ast_compiler.emit(artifact.ir)
        artifact.source = source

        # 写入文件
        filename = self.output_dir / f"{artifact.name.lower().replace(' ', '_')}.py"
        filename.write_text(source, encoding="utf-8")

        artifact.metadata["output_file"] = str(filename)
        artifact.metadata["language"] = "python"

        print(f"🔨 生成: {filename}")
        return artifact
