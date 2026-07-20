from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class ModuleStatus(Enum):
    DRAFT = "draft"
    READY = "ready"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"

@dataclass
class Capability:
    name: str
    description: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)

@dataclass
class Contract:
    interface: str
    version: str
    dependencies: List[str] = field(default_factory=list)

@dataclass
class Module:
    name: str
    version: str
    status: ModuleStatus = ModuleStatus.DRAFT
    capabilities: List[Capability] = field(default_factory=list)
    contract: Optional[Contract] = None
    implementation: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
