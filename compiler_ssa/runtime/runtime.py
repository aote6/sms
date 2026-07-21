"""Runtime - 主运行时（带依赖解析）"""

from compiler_ssa.runtime.context import RuntimeContext
from compiler_ssa.runtime.service import RuntimeService
from compiler_ssa.runtime.container import Container
from compiler_ssa.runtime.events import EventBus
from compiler_ssa.runtime.dependency import DependencyResolver


class Runtime:
    def __init__(self, repository=None):
        self.context = RuntimeContext()
        self.service = RuntimeService(self.context)
        self.container = Container()
        self.events = EventBus()
        self.repository = repository
        self.resolver = DependencyResolver(repository) if repository else None

    def set_repository(self, repository):
        self.repository = repository
        self.resolver = DependencyResolver(repository)

    def install(self, name: str, version: str, directory: str = None):
        """安装并加载模块及其所有依赖"""
        if self.resolver is None:
            raise ValueError("Runtime 未设置 Repository")

        # 如果提供了目录，直接加载
        if directory:
            instance = self.context.load(name, version, directory)
            self.container.register(name, instance)
            self.events.emit("module_loaded", name, version)
            return instance

        # 否则从仓库解析依赖
        order = self.resolver.resolve(name, version)

        loaded_modules = []
        for module, ver in order:
            if (module, ver) in self.context.instances:
                loaded_modules.append((module, ver))
                continue

            directory = self.repository.package_dir(module, ver)
            if not directory.exists():
                # 尝试安装缺失的包
                self.events.emit("package_missing", module, ver)
                continue

            instance = self.context.load(module, ver, directory)
            self.container.register(module, instance)
            self.events.emit("module_loaded", module, ver)
            loaded_modules.append((module, ver))

        return self.context.get_instance(name, version)

    def call(self, name: str, version: str, function: str, *args):
        return self.service.call(name, version, function, *args)

    def loaded(self):
        return self.context.loaded()

    def unload(self, name: str, version: str):
        self.context.unload(name, version)
        self.events.emit("module_unloaded", name, version)

    def get_instance(self, name: str, version: str):
        return self.context.get_instance(name, version)
