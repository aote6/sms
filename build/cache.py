"""BuildCache - 构建缓存"""

import json
import os
from pathlib import Path


class BuildCache:
    def __init__(self, filename=".smscache"):
        self.filename = filename
        self.data = {}
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

    def get(self, key):
        return self.data.get(key)

    def put(self, key, value):
        self.data[key] = value

    def clear(self):
        self.data = {}

    def has(self, key):
        return key in self.data
