"""构建管线适配器

BuildExecutor（build/executor.py）期待的接口:
  - backend.emit(ir) -> 带 .path 属性的 Artifact
  - packager.build(module_name, [artifact]) -> 打包产物路径

但现有实现是:
  - PythonBuilder.build(ir) -> 返回文件路径字符串（不是 Artifact，方法名也不同）
  - 项目里没有任何 packager 实现

这两个 adapter 只做接口适配，不改变底层生成逻辑。
SimplePackager 目前是占位实现（直接返回 artifact 路径，不生成真实
.smspkg 打包格式）——如果以后需要真实打包，在这里扩展，
不要去动 PythonBuilder 或 BuildExecutor。
"""

from build.artifact import Artifact


class BackendAdapter:
    def __init__(self, python_builder):
        self._builder = python_builder

    def emit(self, ir):
        filename = self._builder.build(ir)
        return Artifact.create(
            module=ir.name,
            version=ir.version,
            language="python",
            path=filename,
        )


class SimplePackager:
    """占位打包器：TODO 需要真实 .smspkg 格式时在此扩展"""

    def build(self, name, artifacts):
        if not artifacts:
            return None
        return str(artifacts[0].path)
