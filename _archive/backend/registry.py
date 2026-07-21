"""Backend Registry - 管理所有后端"""

from .python_backend import PythonBackend
from .cpp_backend import CppBackend
from .rust_backend import RustBackend


class BackendRegistry:
    def __init__(self):
        self.backends = {}
        self.register(PythonBackend())
        self.register(CppBackend())
        self.register(RustBackend())

    def register(self, backend):
        self.backends[backend.name] = backend

    def get(self, name):
        return self.backends.get(name)

    def names(self):
        return sorted(self.backends.keys())

    def summary(self):
        print()
        print("=" * 50)
        print("Backend Registry")
        print("=" * 50)
        for name in self.names():
            backend = self.get(name)
            print(f"  {name} -> {backend.extension}")
        print("=" * 50)
