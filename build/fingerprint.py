"""Fingerprint - 工件指纹"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class Fingerprint:
    @staticmethod
    def sha256_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha256_file(path: str | Path) -> str:
        return Fingerprint.sha256_bytes(
            Path(path).read_bytes()
        )

    @staticmethod
    def sha256_str(content: str) -> str:
        return Fingerprint.sha256_bytes(content.encode("utf-8"))

    @staticmethod
    def object(obj: Any) -> str:
        data = json.dumps(
            obj,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
        return Fingerprint.sha256_bytes(data)

    @staticmethod
    def module(module) -> str:
        """生成模块指纹"""
        caps = []
        for c in module.capabilities:
            caps.append({
                "name": c.name,
                "parameters": getattr(c, 'parameters', []),
                "implementation": getattr(c, 'implementation', ''),
            })

        payload = {
            "name": module.name,
            "version": module.version,
            "state": getattr(module, 'state', 'draft'),
            "runtime": module.contract.runtime if module.contract else "python",
            "capabilities": caps,
        }
        return Fingerprint.object(payload)

    @staticmethod
    def artifact(path: str | Path) -> str:
        """生成工件指纹"""
        return Fingerprint.sha256_file(path)
