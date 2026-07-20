from abc import ABC, abstractmethod
from ir import IRModule

class Runtime(ABC):
    name = "runtime"
    
    @abstractmethod
    def build(self, ir: IRModule) -> str:
        pass
    
    @abstractmethod
    def run(self, filename: str):
        pass
