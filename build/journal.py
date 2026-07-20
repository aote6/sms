"""BuildJournal - 构建日志/数据库"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import json
import time
import uuid
from pathlib import Path


@dataclass
class ModuleRecord:
    name: str
    status: str  # success, failed, skipped
    duration: float = 0.0
    artifact: Optional[str] = None
    error: Optional[str] = None
    hash: Optional[str] = None


@dataclass
class BuildJournal:
    build_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: float = field(default_factory=time.time)
    status: str = "running"
    modules: Dict[str, ModuleRecord] = field(default_factory=dict)

    def add(self, record: ModuleRecord):
        self.modules[record.name] = record

    def finish(self, status: str = "success"):
        self.status = status
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "build_id": self.build_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "modules": {
                name: {
                    "status": record.status,
                    "duration": record.duration,
                    "artifact": record.artifact,
                    "error": record.error,
                    "hash": record.hash,
                }
                for name, record in self.modules.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BuildJournal':
        journal = cls(
            build_id=data.get("build_id", uuid.uuid4().hex[:8]),
            timestamp=data.get("timestamp", time.time()),
            status=data.get("status", "unknown"),
        )
        for name, record_data in data.get("modules", {}).items():
            journal.modules[name] = ModuleRecord(
                name=name,
                status=record_data.get("status", "unknown"),
                duration=record_data.get("duration", 0.0),
                artifact=record_data.get("artifact"),
                error=record_data.get("error"),
                hash=record_data.get("hash"),
            )
        return journal

    def save(self, path: str = ".sms/journal.json"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str = ".sms/journal.json") -> Optional['BuildJournal']:
        if not Path(path).exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def summary(self):
        print()
        print("=" * 60)
        print("Build Journal")
        print("=" * 60)
        print(f"  build_id  : {self.build_id}")
        print(f"  timestamp : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))}")
        print(f"  status    : {self.status}")
        print(f"  modules   : {len(self.modules)}")

        # 统计
        success = sum(1 for m in self.modules.values() if m.status == "success")
        failed = sum(1 for m in self.modules.values() if m.status == "failed")
        skipped = sum(1 for m in self.modules.values() if m.status == "skipped")

        print(f"    success : {success}")
        print(f"    failed  : {failed}")
        print(f"    skipped : {skipped}")

        # 显示失败模块
        if failed > 0:
            print()
            print("  ❌ 失败模块:")
            for name, record in self.modules.items():
                if record.status == "failed":
                    print(f"    {name}: {record.error}")
        print("=" * 60)

    def failed_modules(self) -> list[str]:
        return [name for name, record in self.modules.items() if record.status == "failed"]

    def successful_modules(self) -> list[str]:
        return [name for name, record in self.modules.items() if record.status == "success"]

    def skipped_modules(self) -> list[str]:
        return [name for name, record in self.modules.items() if record.status == "skipped"]

    def has_failed(self) -> bool:
        return len(self.failed_modules()) > 0
