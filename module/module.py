from dataclasses import dataclass, field
from typing import List, Optional
from .capability import Capability
from .contract import Contract
from .evidence import Evidence


class PackageType:
    ATOMIC = "atomic"
    COMPOSITE = "composite"
    IMPORTED = "imported"
    GENERATED = "generated"


class QualityState:
    BLANK = "blank"
    PENDING = "pending"
    TESTING = "testing"
    PASSED = "passed"
    SCRAPPED = "scrapped"
    MAINTAINED = "maintained"

    # 合法的状态转换
    _transitions = {
        BLANK: [PENDING, SCRAPPED],
        PENDING: [TESTING, SCRAPPED],
        TESTING: [PASSED, BLANK, SCRAPPED],  # BLANK = 返工
        PASSED: [MAINTAINED, SCRAPPED],
        MAINTAINED: [SCRAPPED, PASSED],
        SCRAPPED: [BLANK],  # 只能回炉
    }

    @classmethod
    def can_transition(cls, from_state: str, to_state: str) -> bool:
        allowed = cls._transitions.get(from_state, [])
        return to_state in allowed


class Origin:
    HANDWRITTEN = "handwritten"
    AI_GENERATED = "ai_generated"
    IMPORTED = "imported"
    THIRD_PARTY = "third_party"


@dataclass
class Module:
    name: str
    version: str
    package_type: str = PackageType.ATOMIC
    capabilities: List[Capability] = field(default_factory=list)
    contract: Optional[Contract] = None
    evidence: Optional[Evidence] = None
    submodules: List[dict] = field(default_factory=list)
    version_history: List[dict] = field(default_factory=list)
    quality_state: str = QualityState.BLANK
    author: str = ""
    origin: str = Origin.HANDWRITTEN
    expires_at: float = 0.0
    implementation: str = ""
    state: str = QualityState.BLANK

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

    def promote(self, new_state: str) -> bool:
        """变更质量状态，返回是否成功"""
        if QualityState.can_transition(self.quality_state, new_state):
            self.quality_state = new_state
            self.state = new_state
            return True
        return False
