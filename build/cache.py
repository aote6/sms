from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Optional

@dataclass
class BuildInfo:
    node_id: str
    fingerprint: str

class BuildCache:
    def __init__(self, path=".smscache"):
        self.path = Path(path)
        self.data: dict[str, str] = {}
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text())
            except:
                self.data = {}
    
    def fingerprint(self, obj) -> str:
        """计算对象的指纹"""
        try:
            if hasattr(obj, 'to_dict'):
                payload = obj.to_dict()
            else:
                payload = repr(obj)
            payload_str = json.dumps(payload, sort_keys=True, default=str)
        except:
            payload_str = str(obj)
        return hashlib.sha256(payload_str.encode()).hexdigest()
    
    def changed(self, node_id: str, ir) -> bool:
        """检查IR是否变化"""
        fp = self.fingerprint(ir)
        old = self.data.get(node_id)
        return old != fp
    
    def update(self, node_id: str, ir):
        """更新缓存"""
        self.data[node_id] = self.fingerprint(ir)
    
    def get(self, node_id: str) -> Optional[str]:
        return self.data.get(node_id)
    
    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2))
    
    def clear(self):
        self.data = {}
        self.save()
