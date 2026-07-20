from dataclasses import dataclass

@dataclass
class Capability:
    name: str
    description: str = ""
    input_type: str = "any"
    output_type: str = "any"
    optional: bool = False
