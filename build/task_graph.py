"""TaskGraph - 从 BuildGraph 生成任务图"""

from build.task import BuildTask


class TaskGraph:
    def __init__(self):
        self.tasks: dict[str, BuildTask] = {}

    def from_build_graph(self, graph):
        self.tasks.clear()

        # 创建任务
        for name, node in graph.nodes.items():
            task = BuildTask(
                name=name,
                node=node,
                deps=0,
            )
            self.tasks[name] = task

        # 建立依赖关系（只统计 dirty 依赖）
        for name, node in graph.nodes.items():
            task = self.tasks[name]
            for dep_name in node.deps:
                dep_node = graph.nodes.get(dep_name)
                if dep_node and dep_node.dirty:
                    task.deps += 1
                if dep_name in self.tasks:
                    self.tasks[dep_name].users.append(task)

        return self

    def ready(self) -> list[BuildTask]:
        return [
            task
            for task in self.tasks.values()
            if task.ready()
            and task.node.dirty
            and task.state.value == 0  # WAITING
        ]

    def all_tasks(self) -> list[BuildTask]:
        return list(self.tasks.values())

    def unfinished_dirty(self) -> list[str]:
        return [
            task.name
            for task in self.tasks.values()
            if task.node.dirty and task.state.value != 2  # not DONE
        ]

    def summary(self):
        print()
        print("=" * 50)
        print("Task Graph")
        print("=" * 50)
        for task in self.tasks.values():
            users = [u.name for u in task.users]
            print(f"  {task.name} (state={task.state}, deps={task.deps})")
            if users:
                print(f"    users: {', '.join(users)}")
        print("=" * 50)
