"""CompilerProfiler - 编译器性能分析器（含百分比、热点排序、统计）"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import time


@dataclass
class PhaseRecord:
    name: str
    duration_ms: float
    metadata: Dict[str, float] = field(default_factory=dict)

    def percentage(self, total: float) -> float:
        return (self.duration_ms / total * 100) if total > 0 else 0


@dataclass
class PassRecord:
    name: str
    duration_ms: float
    before: int = 0
    after: int = 0
    removed: int = 0

    def percentage(self, total: float) -> float:
        return (self.duration_ms / total * 100) if total > 0 else 0


class CompilerProfiler:
    def __init__(self):
        self.phases: List[PhaseRecord] = []
        self.passes: List[PassRecord] = []
        self.analysis_phases: List[PhaseRecord] = []
        self._current_phase = None
        self._current_start = 0

        # Statistics
        self.stats = {
            "modules": 0,
            "functions": 0,
            "basic_blocks": 0,
            "instructions": 0,
            "phi_nodes": 0,
            "call_sites": 0,
            "constants_folded": 0,
            "dead_instructions": 0,
            "copies_removed": 0,
            "calls_inlined": 0,
            "gvn_eliminated": 0,
        }

    def start_phase(self, name: str):
        self._current_phase = name
        self._current_start = time.perf_counter()

    def end_phase(self, metadata: Dict[str, float] = None):
        if self._current_phase is None:
            return
        duration = (time.perf_counter() - self._current_start) * 1000
        record = PhaseRecord(
            name=self._current_phase,
            duration_ms=duration,
            metadata=metadata or {}
        )
        self.phases.append(record)
        self._current_phase = None
        return record

    def record_analysis_phase(self, name: str, duration_ms: float):
        self.analysis_phases.append(PhaseRecord(name, duration_ms))

    def record_pass(self, name: str, duration_ms: float, before: int = 0, after: int = 0):
        self.passes.append(PassRecord(
            name=name,
            duration_ms=duration_ms,
            before=before,
            after=after,
            removed=before - after if before > 0 and after > 0 else 0
        ))

    def update_stats(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.stats:
                self.stats[key] = value

    def summary(self):
        print()
        print("=" * 60)
        print("Compiler Profile")
        print("=" * 60)

        # Phases (右对齐)
        total_phase = sum(p.duration_ms for p in self.phases)
        if self.phases:
            print("\n📊 Phases:")
            max_name_len = max(len(p.name) for p in self.phases) + 2
            for p in self.phases:
                pct = p.percentage(total_phase)
                print(f"  {p.name:>{max_name_len}} {p.duration_ms:>8.1f} ms  ({pct:>5.1f}%)")
            print("-" * (max_name_len + 30))
            print(f"  {'TOTAL':>{max_name_len}} {total_phase:>8.1f} ms  (100.0%)")

        # Passes with hot spots
        if self.passes:
            total_pass = sum(p.duration_ms for p in self.passes)
            print("\n📊 Optimization Passes:")
            max_name_len = max(len(p.name) for p in self.passes) + 2
            for p in sorted(self.passes, key=lambda x: x.duration_ms, reverse=True):
                pct = p.percentage(total_pass)
                removed_str = f"  (removed {p.removed})" if p.removed > 0 else ""
                print(f"  {p.name:>{max_name_len}} {p.duration_ms:>8.1f} ms  ({pct:>5.1f}%){removed_str}")
            print("-" * (max_name_len + 30))
            print(f"  {'TOTAL':>{max_name_len}} {total_pass:>8.1f} ms  (100.0%)")

            # Hotspots
            print("\n🔥 Optimization Hotspots:")
            hotspots = sorted(self.passes, key=lambda x: x.duration_ms, reverse=True)[:5]
            for i, p in enumerate(hotspots, 1):
                print(f"  {i}. {p.name:20} {p.duration_ms:>8.1f} ms")

        # Analysis phases
        if self.analysis_phases:
            total_analysis = sum(p.duration_ms for p in self.analysis_phases)
            print("\n📊 Analysis:")
            max_name_len = max(len(p.name) for p in self.analysis_phases) + 2
            for p in self.analysis_phases:
                pct = p.percentage(total_analysis)
                print(f"  {p.name:>{max_name_len}} {p.duration_ms:>8.1f} ms  ({pct:>5.1f}%)")
            print("-" * (max_name_len + 30))
            print(f"  {'TOTAL':>{max_name_len}} {total_analysis:>8.1f} ms  (100.0%)")

        # Optimization Summary
        print("\n📈 Optimization Summary:")
        opt_items = [
            ("Constants Folded", self.stats.get("constants_folded", 0)),
            ("Dead Instructions", self.stats.get("dead_instructions", 0)),
            ("Copies Removed", self.stats.get("copies_removed", 0)),
            ("Calls Inlined", self.stats.get("calls_inlined", 0)),
            ("GVN Eliminated", self.stats.get("gvn_eliminated", 0)),
            ("Phi Nodes", self.stats.get("phi_nodes", 0)),
        ]
        for name, value in opt_items:
            print(f"  {name:20} {value:>8}")

        # Compiler Statistics
        print("\n📊 Compiler Statistics:")
        stat_items = [
            ("Modules", self.stats.get("modules", 0)),
            ("Functions", self.stats.get("functions", 0)),
            ("Basic Blocks", self.stats.get("basic_blocks", 0)),
            ("Instructions", self.stats.get("instructions", 0)),
            ("Phi Nodes", self.stats.get("phi_nodes", 0)),
            ("Call Sites", self.stats.get("call_sites", 0)),
        ]
        for name, value in stat_items:
            print(f"  {name:20} {value:>8}")

        # Performance
        instructions = self.stats.get("instructions", 0)
        compile_time = total_phase if self.phases else 1
        throughput = instructions / (compile_time / 1000) if compile_time > 0 else 0
        print("\n⚡ Performance:")
        print(f"  Compile Time        {compile_time:>8.1f} ms")
        print(f"  Instructions        {instructions:>8}")
        print(f"  Throughput          {throughput:>8.0f} inst/s")

        print("=" * 60)
