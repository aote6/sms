from dataclasses import dataclass, field

@dataclass
class Contract:
    version: str = "1.0"
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    runtime: str = "python"
