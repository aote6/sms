"""Runtime Service - 调用已加载模块的函数"""

from compiler.runtime.context import RuntimeContext


class RuntimeService:
    def __init__(self, context: RuntimeContext):
        self.context = context

    def call(self, name: str, version: str, function: str, *args, **kwargs):
        module = self.context.get_instance(name, version)
        if module is None:
            raise ValueError(f"模块未加载: {name} v{version}")

        fn = getattr(module, function)
        if fn is None:
            raise AttributeError(f"函数不存在: {name}.{function}")

        return fn(*args, **kwargs)

    def has_function(self, name: str, version: str, function: str) -> bool:
        module = self.context.get_instance(name, version)
        if module is None:
            return False
        return hasattr(module, function)
