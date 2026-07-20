"""BuildQueue - 任务队列"""

from collections import deque
from build.task import BuildTask


class BuildQueue:
    def __init__(self):
        self.queue: deque[BuildTask] = deque()

    def push(self, task: BuildTask):
        task.state = "waiting"
        self.queue.append(task)

    def pop(self) -> BuildTask:
        return self.queue.popleft()

    def empty(self) -> bool:
        return len(self.queue) == 0

    def size(self) -> int:
        return len(self.queue)

    def clear(self):
        self.queue.clear()
