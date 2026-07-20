"""TaskState - 任务状态枚举"""

from enum import Enum, auto


class TaskState(Enum):
    WAITING = auto()
    READY = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()
    SKIPPED = auto()

    def __str__(self):
        return self.name
