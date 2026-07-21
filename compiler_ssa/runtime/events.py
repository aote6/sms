"""EventBus - 事件总线"""


class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event: str, callback):
        self.listeners.setdefault(event, []).append(callback)

    def emit(self, event: str, *args, **kwargs):
        for cb in self.listeners.get(event, []):
            cb(*args, **kwargs)

    def clear(self):
        self.listeners.clear()
