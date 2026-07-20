"""Package Builder - 将 Artifacts 打包成 .smspkg"""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json


class PackageBuilder:
    FORMAT_VERSION = "1.0"

    def build(self, package_name, artifacts, output_dir="build"):
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        pkg = output_dir / f"{package_name.lower()}.smspkg"

        manifest = {
            "format": self.FORMAT_VERSION,
            "package": package_name,
            "files": []
        }

        with ZipFile(pkg, "w", ZIP_DEFLATED) as z:
            for artifact in artifacts:
                path = Path(artifact.path)
                if not path.exists():
                    continue

                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                manifest["files"].append({
                    "kind": artifact.kind,
                    "file": path.name,
                    "sha256": digest
                })
                z.write(path, arcname=path.name)

            manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
            z.writestr("manifest.json", manifest_json)

        return pkg
