"""StageReport - 阶段报告"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class StageReport:
    name: str
    start_time: float
    end_time: float
    duration_ms: float
    status: str
    inputs: int = 0
    outputs: int = 0
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(cls, name: str, start: float, end: float, status: str = "success"):
        return cls(
            name=name,
            start_time=start,
            end_time=end,
            duration_ms=(end - start) * 1000,
            status=status,
        )

    def with_inputs(self, count: int):
        self.inputs = count
        return self

    def with_outputs(self, count: int):
        self.outputs = count
        return self

    def __repr__(self):
        return f"StageReport(name={self.name}, duration={self.duration_ms:.1f}ms, status={self.status})"


@dataclass
class PipelineProfile:
    reports: List[StageReport] = field(default_factory=list)

    def add(self, report: StageReport):
        self.reports.append(report)

    def total_duration(self) -> float:
        return sum(r.duration_ms for r in self.reports)

    def summary(self):
        print()
        print("=" * 50)
        print("Pipeline Profile")
        print("=" * 50)

        max_name_len = max([len(r.name) for r in self.reports], default=0) + 2
        for r in self.reports:
            status = "✅" if r.status == "success" else "❌"
            print(f"  {r.name:>{max_name_len}} {r.duration_ms:>8.1f}ms {status}")

        print("-" * 50)
        print(f"  {'TOTAL':>{max_name_len}} {self.total_duration():>8.1f}ms")
        print("=" * 50)

    def timeline(self):
        print()
        print("=" * 50)
        print("Pipeline Timeline")
        print("=" * 50)

        max_duration = max([r.duration_ms for r in self.reports], default=1)
        scale = 50 / max_duration if max_duration > 0 else 1

        for r in self.reports:
            bar_len = int(r.duration_ms * scale)
            bar = "█" * min(bar_len, 50)
            print(f"  {r.name:12} {bar} {r.duration_ms:.1f}ms")

        print("=" * 50)

    def slowest(self, n: int = 3):
        sorted_reports = sorted(self.reports, key=lambda r: r.duration_ms, reverse=True)
        print()
        print("=" * 50)
        print(f"Top {n} Slowest Stages")
        print("=" * 50)
        for i, r in enumerate(sorted_reports[:n], 1):
            print(f"  {i}. {r.name:12} {r.duration_ms:.1f}ms")
        print("=" * 50)
