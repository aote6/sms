from abc import ABC, abstractmethod
from ir import IRModule
from build.artifact import Artifact

class Backend(ABC):
    name: str = "base"
    
    @abstractmethod
    def emit(self, ir: IRModule) -> Artifact:
        """从IR生成产物，返回Artifact"""
        pass
