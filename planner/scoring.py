"""Score - 多目标评分"""

from dataclasses import dataclass, field


@dataclass
class Score:
    total: float = 0.0
    items: dict = field(default_factory=dict)

    def add(self, name: str, value: float):
        self.items[name] = value
        self.total += value

    def __str__(self):
        return f"{self.total:.2f}"

    def __repr__(self):
        items_str = ", ".join([f"{k}={v:.2f}" for k, v in self.items.items()])
        return f"Score(total={self.total:.2f}, {items_str})"
