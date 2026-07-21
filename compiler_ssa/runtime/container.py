"""Container - 服务容器"""


class Container:
    def __init__(self):
        self.services = {}

    def register(self, name: str, instance):
        self.services[name] = instance

    def resolve(self, name: str):
        if name not in self.services:
            raise KeyError(f"服务未注册: {name}")
        return self.services[name]

    def exists(self, name: str) -> bool:
        return name in self.services

    def list(self):
        return list(self.services.keys())
