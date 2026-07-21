"""Runtime Context - 管理已加载的模块"""

from __future__ import annotations

from compiler_ssa.loader import RuntimeLoader


class RuntimeContext:
    def __init__(self):
        self.loader = RuntimeLoader()
        self.modules = {}   # (name, version) -> directory
        self.instances = {} # (name, version) -> module instance

    def load(self, name: str, version: str, directory: str):
        key = (name, version)
        if key in self.instances:
            return self.instances[key]

        module = self.loader.load(directory, name)
        self.modules[key] = directory
        self.instances[key] = module
        return module

    def unload(self, name: str, version: str):
        key = (name, version)
        self.modules.pop(key, None)
        self.instances.pop(key, None)

    def loaded(self):
        return sorted(self.instances.keys())

    def get_instance(self, name: str, version: str):
        key = (name, version)
        return self.instances.get(key)

    def get_module_path(self, name: str, version: str):
        key = (name, version)
        return self.modules.get(key)
