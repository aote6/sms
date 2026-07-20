from dataclasses import dataclass, field
from typing import List, Optional, Any
from .capability import Capability
from .contract import Contract
from .evidence import Evidence


@dataclass
class Module:
    name: str
    version: str
    state: str = "draft"
    capabilities: List[Capability] = field(default_factory=list)
    contract: Optional[Contract] = None
    evidence: Optional[Evidence] = None
    implementation: str = ""

    def ready(self) -> bool:
        if self.contract is None:
            return False
        if self.evidence is None:
            return False
        if not self.evidence.test_pass:
            return False
        if len(self.capabilities) == 0:
            return False
        return True
