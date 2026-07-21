from abc import ABC, abstractmethod

class Pass(ABC):
    """IR Pass 基类"""
    name = "Pass"

    @abstractmethod
    def run(self, module):
        return module
