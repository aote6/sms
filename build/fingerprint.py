"""Fingerprint - 生成对象指纹"""

from __future__ import annotations

import hashlib
import json


class Fingerprint:
    @staticmethod
    def object(obj) -> str:
        data = json.dumps(
            obj,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        ).encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def module(module) -> str:
        """生成模块指纹"""
        caps = []
        for c in module.capabilities:
            caps.append({
                "name": c.name,
                "parameters": c.parameters if hasattr(c, 'parameters') else [],
                "implementation": c.implementation if hasattr(c, 'implementation') else "",
            })

        return Fingerprint.object({
            "name": module.name,
            "version": module.version,
            "state": module.state if hasattr(module, 'state') else "draft",
            "capabilities": caps,
        })
