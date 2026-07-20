"""TaskResult - 任务执行结果"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskResult:
    task: str
    success: bool
    duration: float
    artifact: Optional[str] = None
    artifact_hash: Optional[str] = None
    error: Optional[Exception] = None

    def __repr__(self):
        status = "✅" if self.success else "❌"
        return f"TaskResult(task={self.task}, {status}, duration={self.duration:.2f}s)"
