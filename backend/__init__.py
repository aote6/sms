from .backend import Backend
from .python_backend import PythonBackend
from .rust_backend import RustBackend

class BackendRegistry:
    def __init__(self):
        self._backends = {}
    
    def register(self, backend: Backend):
        self._backends[backend.name] = backend
    
    def get(self, name: str) -> Backend:
        return self._backends.get(name)
    
    def list_all(self):
        return list(self._backends.keys())

# 默认注册
_default_registry = BackendRegistry()
_default_registry.register(PythonBackend())
_default_registry.register(RustBackend())

def get_backend(name: str) -> Backend:
    return _default_registry.get(name)
