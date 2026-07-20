from dataclasses import dataclass, field
from .capability import Capability
from .contract import Contract
from .evidence import Evidence

@dataclass
class Module:
    name: str
    version: str
    state: str = "draft"
    capabilities: list[Capability] = field(default_factory=list)
    contract: Contract | None = None
    evidence: Evidence | None = None
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
