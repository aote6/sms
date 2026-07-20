import hashlib
import json

class BuildCache:
    def __init__(self):
        self.cache: dict[str, str] = {}
    
    def hash(self, obj) -> str:
        """计算对象的哈希值"""
        try:
            # 尝试转为字符串
            content = repr(obj)
        except:
            content = str(obj)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def changed(self, name: str, obj) -> bool:
        """检查对象是否变化"""
        h = self.hash(obj)
        old = self.cache.get(name)
        if old == h:
            return False
        self.cache[name] = h
        return True
    
    def get(self, name: str) -> str:
        return self.cache.get(name)
    
    def save(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.cache, f)
    
    def load(self, filename: str):
        try:
            with open(filename, 'r') as f:
                self.cache = json.load(f)
        except FileNotFoundError:
            pass
