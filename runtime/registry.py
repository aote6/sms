class RuntimeRegistry:
    def __init__(self):
        self._items = {}
    
    def register(self, runtime):
        self._items[runtime.name] = runtime
    
    def get(self, name):
        return self._items.get(name)
    
    def list_all(self):
        return list(self._items.keys())
