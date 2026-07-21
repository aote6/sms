from dataclasses import dataclass, field
from typing import List


@dataclass
class Evidence:
    """模块的检测证据（借鉴元器件质检报告）"""
    test_pass: bool = False
    coverage: float = 0.0
    benchmark: float = 0.0
    signed: bool = False
    test_count: int = 0
    fail_count: int = 0
    test_results: List[dict] = field(default_factory=list)
    checked_at: float = 0.0
    checked_by: str = ""
