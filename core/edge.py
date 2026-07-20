from dataclasses import dataclass
from enum import Enum

class EdgeType(Enum):
    ANSWER = "answer"
    DEPEND = "depend"
    CREATE = "create"
    VERIFY = "verify"
    COMPOSE = "compose"

@dataclass
class Edge:
    source: str
    target: str
    edge_type: EdgeType
