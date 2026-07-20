"""
SMS Compiler Type System
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ===========================
# Base
# ===========================

@dataclass(slots=True, frozen=True)
class IRType:
    name: str

    def __str__(self):
        return self.name


# ===========================
# Primitive Types
# ===========================

VOID = IRType("void")
ANY = IRType("Any")
BOOL = IRType("bool")
INT = IRType("int")
FLOAT = IRType("float")
STRING = IRType("str")


# ===========================
# User Type
# ===========================

@dataclass(slots=True)
class StructField:
    name: str
    type: IRType


@dataclass(slots=True)
class StructType:
    name: str
    fields: List[StructField] = field(default_factory=list)

    def add_field(self, name: str, t: IRType):
        self.fields.append(StructField(name, t))

    def field(self, name: str):
        for f in self.fields:
            if f.name == name:
                return f
        return None


# ===========================
# Generic
# ===========================

@dataclass(slots=True)
class ListType:
    element: IRType

    @property
    def name(self):
        return f"List[{self.element}]"


@dataclass(slots=True)
class DictType:
    key: IRType
    value: IRType

    @property
    def name(self):
        return f"Dict[{self.key},{self.value}]"


@dataclass(slots=True)
class OptionalType:
    value: IRType

    @property
    def name(self):
        return f"Optional[{self.value}]"


# ===========================
# Function Signature
# ===========================

@dataclass(slots=True)
class Parameter:
    name: str
    type: IRType = ANY
    default: Optional[str] = None


@dataclass(slots=True)
class FunctionType:
    parameters: List[Parameter]
    returns: IRType = VOID


# ===========================
# Registry
# ===========================

class TypeRegistry:
    def __init__(self):
        self._types = {}
        self.register(VOID)
        self.register(ANY)
        self.register(BOOL)
        self.register(INT)
        self.register(FLOAT)
        self.register(STRING)

    def register(self, t):
        self._types[t.name] = t

    def get(self, name):
        return self._types[name]

    def exists(self, name):
        return name in self._types

    def all(self):
        return list(self._types.values())


registry = TypeRegistry()


# ===========================
# Helpers
# ===========================

def list_of(t):
    return ListType(t)


def dict_of(k, v):
    return DictType(k, v)


def optional(t):
    return OptionalType(t)
