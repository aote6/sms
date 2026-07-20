"""Weights - 评分权重"""


class Weights:
    def __init__(self):
        self.weights = {
            "priority": 1.0,
            "coverage": 100.0,
            "performance": 0.10,
            "memory": -0.02,
            "size": -0.01,
            "ready": 100.0,
            "verified": 80.0,
            "draft": 20.0,
        }

    def get(self, key: str, default: float = 0.0) -> float:
        return self.weights.get(key, default)

    def set(self, key: str, value: float):
        self.weights[key] = value

    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.weights[key] = value

    def summary(self):
        print()
        print("=" * 50)
        print("Weights")
        print("=" * 50)
        for key, value in sorted(self.weights.items()):
            print(f"  {key:12} = {value}")
        print("=" * 50)
