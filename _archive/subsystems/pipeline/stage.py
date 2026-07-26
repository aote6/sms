from abc import ABC, abstractmethod

class Stage(ABC):
    name = "stage"

    @abstractmethod
    def run(self, context):
        pass
