"""Artifact Builder - 从 IR 构建多后端产物"""

import json
from compiler_ssa.artifact import Artifact


class ArtifactBuilder:
    def __init__(self, backend_registry):
        self.registry = backend_registry

    def build(self, ir_module):
        artifacts = []

        # 为每个后端生成代码
        for backend in self.registry.backends.values():
            source = backend.emit_module(ir_module)
            ext_map = {
                "python": ".py",
                "cpp": ".cpp",
                "rust": ".rs",
            }
            ext = ext_map.get(backend.name, ".txt")

            artifacts.append(
                Artifact(
                    kind=backend.name,
                    extension=ext,
                    source=source,
                )
            )

        # 生成 ABI
        abi = {
            "module": ir_module.name,
            "version": ir_module.version,
            "runtime": ir_module.runtime,
            "exports": [
                {
                    "name": fn.name,
                    "params": [{"name": p.name, "type": str(p.type) if p.type else "Any"} for p in fn.parameters],
                    "returns": str(fn.returns) if fn.returns else "void",
                }
                for fn in ir_module.functions
            ],
        }

        artifacts.append(
            Artifact(
                kind="abi",
                extension=".abi.json",
                source=json.dumps(abi, indent=2, ensure_ascii=False),
            )
        )

        return artifacts
