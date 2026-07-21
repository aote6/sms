"""ABI Loader - 从 JSON 文件加载 ABI"""

import json
from pathlib import Path
from compiler_ssa.abi import ModuleABI, ABIFunction, ABIParameter


class ABILoader:
    def load(self, path) -> ModuleABI:
        data = json.loads(Path(path).read_text(encoding="utf-8"))

        abi = ModuleABI(
            module=data["module"],
            version=data["version"],
        )

        for fn in data.get("exports", []):
            abi.exports.append(
                ABIFunction(
                    name=fn["name"],
                    params=[
                        ABIParameter(
                            p["name"],
                            p["type"]
                        )
                        for p in fn.get("params", [])
                    ],
                    returns=fn.get("returns", "void")
                )
            )

        for fn in data.get("imports", []):
            abi.imports.append(
                ABIFunction(
                    name=fn["name"],
                    params=[
                        ABIParameter(
                            p["name"],
                            p["type"]
                        )
                        for p in fn.get("params", [])
                    ],
                    returns=fn.get("returns", "void")
                )
            )

        return abi
