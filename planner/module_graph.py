"""ModuleGraph - 模块图"""


class ModuleGraph:
    def __init__(self):
        self.modules = {}

    def add(self, module):
        self.modules[module.name] = module
        return module

    def get(self, name):
        return self.modules.get(name)

    def all(self):
        return list(self.modules.values())

    def ready_modules(self):
        return [m for m in self.modules.values() if m.state == "ready"]

    def summary(self):
        print()
        print("=" * 50)
        print("Module Graph")
        print("=" * 50)
        for name, module in self.modules.items():
            state = module.state if hasattr(module, 'state') else "unknown"
            caps = [c.name for c in module.capabilities] if hasattr(module, 'capabilities') else []
            print(f"  {name} [{state}]")
            if caps:
                print(f"    caps: {', '.join(caps)}")
        print("=" * 50)
