"""文件哈希工具"""

import hashlib
from pathlib import Path


def sha256(path) -> str:
    """计算文件的 SHA256 哈希值"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sha256_str(content: str) -> str:
    """计算字符串的 SHA256 哈希值"""
    return hashlib.sha256(content.encode()).hexdigest()
