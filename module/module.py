from dataclasses import dataclass, field
from typing import List, Optional
from .capability import Capability
from .contract import Contract
from .evidence import Evidence


# 封装类型
class PackageType:
    ATOMIC = "atomic"
    COMPOSITE = "composite"
    IMPORTED = "imported"
    GENERATED = "generated"


# 质量状态
class QualityState:
    BLANK = "blank"
    PENDING = "pending"
    TESTING = "testing"
    PASSED = "passed"
    SCRAPPED = "scrapped"
    MAINTAINED = "maintained"


# 产地
class Origin:
    HANDWRITTEN = "handwritten"
    AI_GENERATED = "ai_generated"
    IMPORTED = "imported"
    THIRD_PARTY = "third_party"


@dataclass
class Module:
    # 身份标签
    name: str
    version: str
    package_type: str = PackageType.ATOMIC

    # 数据手册
    capabilities: List[Capability] = field(default_factory=list)
    contract: Optional[Contract] = None
    evidence: Optional[Evidence] = None
    submodules: List[dict] = field(default_factory=list)
    version_history: List[dict] = field(default_factory=list)

    # 品控标签
    quality_state: str = QualityState.BLANK

    # 来源信息
    author: str = ""
    origin: str = Origin.HANDWRITTEN
    expires_at: float = 0.0

    # 保留旧字段兼容
    implementation: str = ""
    state: str = QualityState.BLANK

    def ready(self) -> bool:
        """模块是否合格（可出厂）"""
        if self.contract is None:
            return False
        if self.evidence is None:
            return False
        if not self.evidence.test_pass:
            return False
        if len(self.capabilities) == 0:
            return False
        return True

    def promote(self, new_state: str):
        """变更质量状态"""
        self.quality_state = new_state
        self.state = new_state
