import importlib.util
from pathlib import Path
from build.artifact import Artifact

class RuntimeLoader:
    def load(self, artifact: Artifact):
        """加载 Artifact 对应的模块"""
        if not artifact.exists():
            raise FileNotFoundError(f"Artifact 不存在: {artifact.path}")
        
        spec = importlib.util.spec_from_file_location(
            artifact.module,
            artifact.path
        )
        if spec is None:
            raise ImportError(f"无法加载模块: {artifact.module}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def create(self, artifact: Artifact):
        """加载并创建实例"""
        module = self.load(artifact)
        if not hasattr(module, "create"):
            raise RuntimeError(f"{artifact.module} 没有 create() 工厂方法")
        return module.create()
    
    def call(self, artifact: Artifact, func_name: str, *args, **kwargs):
        """加载模块并调用指定函数"""
        module = self.load(artifact)
        if not hasattr(module, func_name):
            raise AttributeError(f"{artifact.module} 没有 {func_name}() 方法")
        func = getattr(module, func_name)
        return func(*args, **kwargs)
