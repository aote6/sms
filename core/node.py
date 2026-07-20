from dataclasses import dataclass, field
from enum import Enum
import uuid

class NodeType(Enum):
    PROBLEM = "problem"
    DECISION = "decision"
    MODULE = "module"
    PRODUCT = "product"
    EVIDENCE = "evidence"

@dataclass
class Node:
    name: str
    node_type: NodeType
    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    metadata: dict = field(
        default_factory=dict
    )
