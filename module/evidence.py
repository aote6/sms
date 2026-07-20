from dataclasses import dataclass

@dataclass
class Evidence:
    test_pass: bool = False
    coverage: float = 0.0
    benchmark: float = 0.0
    signed: bool = False
