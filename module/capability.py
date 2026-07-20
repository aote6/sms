from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class Capability:
    name: str
    description: str = ""
    input_type: str = "any"
    output_type: str = "any"
    optional: bool = False
    parameters: List[tuple] = field(default_factory=list)
    implementation: str = ""
