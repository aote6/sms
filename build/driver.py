"""BuildDriver - 并行任务驱动构建（支持失败恢复 + Journal）"""

from collections import deque
from build.task_graph import TaskGraph
from build.thread_pool import WorkerPool
from build.worker import BuildWorker
from build.scheduler import BuildScheduler
from build.task_state import TaskState
from build.result import TaskResult
from build.journal import BuildJournal, ModuleRecord


class BuildDriver:
    def __init__(self, scheduler: BuildScheduler, executor, workers: int = 4):
        self.scheduler = scheduler
        self.executor = executor
        self.workers = workers
        self.results = []
        self.journal = BuildJournal()

    def _has_failed_dep(self, task, failed, skipped):
        for dep_name in task.node.deps:
            if dep_name in failed or dep_name in skipped:
                return True
        return False

    def run(self, graph, journal_path: str = ".sms/journal.json"):
        print()
        print("=" * 50)
        print("Parallel Build (ReadyQueue)")
        print("=" * 50)

        tg = TaskGraph().from_build_graph(graph)
        dirty_tasks = [t for t in tg.all_tasks() if t.node.dirty]

        if not dirty_tasks:
            print("  (无需要构建的任务)")
            print("=" * 50)
            return []

        print(f"  任务: {len(dirty_tasks)} 个")
        print(f"  并行度: {self.workers}")
        print("=" * 50)

        failed = set()
        skipped = set()
        finished = set()
        built = []
        self.results = []
        self.journal = BuildJournal()

        ready_queue = deque()
        for task in tg.all_tasks():
            if task.ready() and task.node.dirty:
                ready_queue.append(task)

        workers = [BuildWorker(self.executor, i + 1) for i in range(self.workers)]

        with WorkerPool(self.workers) as pool:
            futures = []

            while ready_queue or futures:
                while ready_queue:
                    task = ready_queue.popleft()

                    if self._has_failed_dep(task, failed, skipped):
                        task.state = TaskState.SKIPPED
                        skipped.add(task.name)
                        self.journal.add(ModuleRecord(
                            name=task.name,
                            status="skipped",
                            error="依赖失败，跳过",
                        ))
                        self.results.append(TaskResult(
                            task=task.name,
                            success=False,
                            duration=0,
                            error=Exception("依赖失败，跳过"),
                        ))
                        print(f"  ⏭ {task.name} (依赖失败)")
                        continue

                    if task.try_schedule():
                        worker = workers[len(futures) % len(workers)]
                        future = pool.submit(worker, task)
                        futures.append(future)

                if not futures:
                    break

                done, _ = pool.wait(futures)

                for future in done:
                    futures.remove(future)
                    result = future.result()
                    self.results.append(result)

                    if result.success:
                        task_name = result.task
                        built.append(task_name)
                        finished.add(task_name)

                        self.journal.add(ModuleRecord(
                            name=task_name,
                            status="success",
                            duration=result.duration,
                            artifact=result.artifact,
                            hash=result.artifact_hash,
                        ))

                        task = None
                        for t in tg.all_tasks():
                            if t.name == task_name:
                                task = t
                                break

                        if task:
                            for user in task.users:
                                if user.dependency_done() and user.node.dirty:
                                    ready_queue.append(user)
                    else:
                        failed.add(result.task)
                        self.journal.add(ModuleRecord(
                            name=result.task,
                            status="failed",
                            error=str(result.error) if result.error else "未知错误",
                        ))

                if not ready_queue and futures:
                    continue

        # 最终处理：标记所有因依赖失败而跳过的任务
        for task in tg.all_tasks():
            if task.node.dirty and task.name not in built and task.name not in failed and task.name not in skipped:
                if self._has_failed_dep(task, failed, skipped):
                    task.state = TaskState.SKIPPED
                    skipped.add(task.name)
                    self.journal.add(ModuleRecord(
                        name=task.name,
                        status="skipped",
                        error="依赖失败，跳过",
                    ))
                    self.results.append(TaskResult(
                        task=task.name,
                        success=False,
                        duration=0,
                        error=Exception("依赖失败，跳过"),
                    ))
                    print(f"  ⏭ {task.name} (依赖失败)")

        # 更新 Journal 状态
        if failed:
            self.journal.finish("failed")
        else:
            self.journal.finish("success")

        # 保存 Journal
        self.journal.save(journal_path)

        print()
        print("=" * 50)
        print("Build Result")
        print("=" * 50)

        for task in tg.all_tasks():
            if task.node.dirty:
                if task.name in built:
                    print(f"  ✅ {task.name}")
                elif task.name in failed:
                    print(f"  ❌ {task.name}")
                elif task.name in skipped or task.state == TaskState.SKIPPED:
                    print(f"  ⏭ {task.name}")
                else:
                    print(f"  ? {task.name}")

        print("=" * 50)

        return built

    def run_serial(self, graph):
        self.workers = 1
        return self.run(graph)
