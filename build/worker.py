"""BuildWorker - 执行构建任务"""

import time
from build.task import BuildTask
from build.task_state import TaskState
from build.result import TaskResult


class BuildWorker:
    def __init__(self, executor, worker_id: int = 1):
        self.executor = executor
        self.worker_id = worker_id

    def __call__(self, task: BuildTask):
        print(f"  Worker-{self.worker_id} 🔨 {task.name}")
        start = time.perf_counter()

        try:
            result = self.executor.build(task.node)
            task.finish()
            task.node.built = True
            duration = time.perf_counter() - start

            artifact_path = None
            artifact_hash = None
            if result and isinstance(result, dict):
                artifact_path = result.get("artifact")
                artifact_hash = result.get("hash")

            return TaskResult(
                task=task.name,
                success=True,
                duration=duration,
                artifact=artifact_path,
                artifact_hash=artifact_hash,
            )
        except Exception as e:
            task.fail()
            duration = time.perf_counter() - start
            print(f"  Worker-{self.worker_id} ❌ {task.name} 失败: {e}")
            return TaskResult(
                task=task.name,
                success=False,
                duration=duration,
                error=e,
            )

    def run(self, task: BuildTask):
        return self.__call__(task)
