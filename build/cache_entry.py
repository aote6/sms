"""CacheEntry - 缓存条目"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CacheEntry:
    module: str
    fingerprint: str
    artifact: str
    abi: str
    package: str
    timestamp: float
    version: str = "1.0.0"
    runtime: str = "python"

    def to_dict(self) -> dict:
        return {
            "module": self.module,
            "fingerprint": self.fingerprint,
            "artifact": self.artifact,
            "abi": self.abi,
            "package": self.package,
            "timestamp": self.timestamp,
            "version": self.version,
            "runtime": self.runtime,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CacheEntry':
        return cls(
            module=data["module"],
            fingerprint=data["fingerprint"],
            artifact=data["artifact"],
            abi=data["abi"],
            package=data["package"],
            timestamp=data["timestamp"],
            version=data.get("version", "1.0.0"),
            runtime=data.get("runtime", "python"),
        )
