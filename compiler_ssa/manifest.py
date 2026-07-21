"""Manifest - 产物清单"""

import json
from compiler_ssa.artifact import Artifact


class ManifestBuilder:
    def build(self, module, artifacts: list[Artifact]) -> Artifact:
        manifest = {
            "module": module.name,
            "version": module.version,
            "runtime": module.runtime,
            "artifacts": [],
        }

        for a in artifacts:
            manifest["artifacts"].append({
                "kind": a.kind,
                "path": a.path,
                "sha256": a.sha256,
            })

        return Artifact(
            kind="manifest",
            extension=".manifest.json",
            source=json.dumps(manifest, indent=2, ensure_ascii=False),
        )
