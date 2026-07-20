from module import Module
from typing import Optional

class ModuleRegistry:
    def __init__(self):
        self.modules: dict[str, Module] = {}
    
    def register(self, module: Module):
        self.modules[module.name] = module
    
    def get(self, name: str) -> Optional[Module]:
        return self.modules.get(name)
    
    def ready_modules(self):
        return [m for m in self.modules.values() if m.ready()]
    
    def list_all(self):
        for name, module in self.modules.items():
            status = "✓" if module.ready() else "○"
            print(f"  {status} {name} v{module.version} [{module.state}]")
