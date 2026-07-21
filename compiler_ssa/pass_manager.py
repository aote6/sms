from abc import ABC, abstractmethod

class IRPass(ABC):
    """IR Pass 基类"""
    name = "pass"

    @abstractmethod
    def run(self, module):
        pass


class PassManager:
    def __init__(self):
        self._passes = []

    def add(self, ir_pass: IRPass):
        self._passes.append(ir_pass)

    def run(self, module):
        for p in self._passes:
            module = p.run(module)
        return module
