"""Module ABI - 模块接口定义"""

from dataclasses import dataclass, field
from typing import List, Optional
import json


@dataclass
class ABIParameter:
    name: str
    type: str

    def to_dict(self):
        return {"name": self.name, "type": self.type}

    @classmethod
    def from_dict(cls, data):
        return cls(name=data["name"], type=data["type"])


@dataclass
class ABIFunction:
    name: str
    params: List[ABIParameter] = field(default_factory=list)
    returns: str = "void"

    def to_dict(self):
        return {
            "name": self.name,
            "params": [p.to_dict() for p in self.params],
            "returns": self.returns,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            params=[ABIParameter.from_dict(p) for p in data.get("params", [])],
            returns=data.get("returns", "void"),
        )


@dataclass
class ModuleABI:
    module: str
    version: str
    exports: List[ABIFunction] = field(default_factory=list)
    imports: List[ABIFunction] = field(default_factory=list)

    def to_dict(self):
        return {
            "module": self.module,
            "version": self.version,
            "exports": [e.to_dict() for e in self.exports],
            "imports": [i.to_dict() for i in self.imports],
        }

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data):
        return cls(
            module=data["module"],
            version=data["version"],
            exports=[ABIFunction.from_dict(e) for e in data.get("exports", [])],
            imports=[ABIFunction.from_dict(i) for i in data.get("imports", [])],
        )

    @classmethod
    def from_json(cls, data):
        return cls.from_dict(json.loads(data))

    def find_export(self, name: str) -> Optional[ABIFunction]:
        for e in self.exports:
            if e.name == name:
                return e
        return None

    def find_import(self, name: str) -> Optional[ABIFunction]:
        for i in self.imports:
            if i.name == name:
                return i
        return None
