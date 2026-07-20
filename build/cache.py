"""BuildCache - 构建缓存"""

import json
import os
from pathlib import Path
from build.cache_entry import CacheEntry


class BuildCache:
    def __init__(self, filename=".smscache"):
        self.filename = filename
        self.data: dict[str, dict] = {}
        self.load()

    def load(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, encoding="utf-8") as f:
                self.data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            self.data = {}

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key: str) -> CacheEntry | None:
        if key not in self.data:
            return None
        try:
            return CacheEntry.from_dict(self.data[key])
        except (KeyError, TypeError):
            return None

    def put(self, entry: CacheEntry):
        self.data[entry.module] = entry.to_dict()

    def has(self, key: str) -> bool:
        return key in self.data

    def clear(self):
        self.data = {}

    def get_fingerprint(self, module: str) -> str | None:
        entry = self.get(module)
        return entry.fingerprint if entry else None

    def summary(self):
        print()
        print("=" * 50)
        print("Build Cache")
        print("=" * 50)
        if not self.data:
            print("  (空)")
        else:
            for key, value in self.data.items():
                print(f"  {key}: {value.get('fingerprint', 'unknown')[:12]}...")
        print("=" * 50)
