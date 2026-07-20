"""EventBus - 事件总线（类型化事件）"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Type


@dataclass
class Event:
    pass


# ============ 事件定义 ============

@dataclass
class SessionStart(Event):
    session: Any


@dataclass
class SessionFinish(Event):
    session: Any


@dataclass
class ModuleStart(Event):
    module: str


@dataclass
class ModuleCompiled(Event):
    module: str


@dataclass
class IRGenerated(Event):
    module: str
    ir: Any


@dataclass
class ArtifactGenerated(Event):
    path: str
    kind: str


@dataclass
class PackageBuilt(Event):
    path: str


@dataclass
class CacheHit(Event):
    module: str


@dataclass
class CacheMiss(Event):
    module: str


@dataclass
class BuildError(Event):
    message: str
    module: str = ""


@dataclass
class BuildWarning(Event):
    message: str
    module: str = ""


# ============ EventBus ============

class EventBus:
    def __init__(self):
        self._handlers: Dict[Type, List[Callable]] = {}

    def subscribe(self, event_type: Type, handler: Callable):
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event: Event):
        for handler in self._handlers.get(type(event), []):
            handler(event)

    def clear(self):
        self._handlers.clear()
