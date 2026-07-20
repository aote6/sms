"""BuildTask - 构建任务（线程安全）"""

from dataclasses import dataclass, field
from typing import List, Any
from build.task_state import TaskState
from threading import Lock


@dataclass
class BuildTask:
    name: str
    node: Any = None
    deps: int = 0
    state: TaskState = TaskState.WAITING
    users: List['BuildTask'] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock, repr=False)

    def try_schedule(self) -> bool:
        with self._lock:
            if self.state != TaskState.WAITING:
                return False
            if self.deps != 0:
                return False
            self.state = TaskState.RUNNING
            return True

    def finish(self):
        with self._lock:
            self.state = TaskState.DONE

    def fail(self):
        with self._lock:
            self.state = TaskState.FAILED

    def skip(self):
        with self._lock:
            self.state = TaskState.SKIPPED

    def dependency_done(self) -> bool:
        with self._lock:
            self.deps -= 1
            return self.deps == 0 and self.state == TaskState.WAITING

    def ready(self) -> bool:
        return self.deps == 0 and self.state == TaskState.WAITING

    def finish_and_release(self, ready_queue):
        """完成并释放依赖"""
        self.finish()
        self.node.built = True
        for user in self.users:
            if user.dependency_done() and user.node.dirty:
                ready_queue.append(user)

    def __repr__(self):
        return f"BuildTask(name={self.name}, deps={self.deps}, state={self.state})"
