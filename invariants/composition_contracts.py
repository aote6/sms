"""定界契约：跨模块组合兼容性检查

检查两个模块的 contract 输入输出是否兼容：
A 的 outputs 和 B 的 inputs 有交集 → A 的输出可以被 B 消费
"""

from typing import List, Dict, Any
from module.module import Module


def check_composition(modules: List[Module]) -> Dict[str, Any]:
    """检查模块间组合兼容性，返回 {passed, compatible_pairs, errors}"""
    result = {"passed": True, "compatible_pairs": [], "errors": []}

    for i, mod_a in enumerate(modules):
        for j, mod_b in enumerate(modules):
            if i >= j:
                continue
            if not mod_a.contract or not mod_b.contract:
                continue

            a_out = set(mod_a.contract.outputs)
            b_in = set(mod_b.contract.inputs)
            b_out = set(mod_b.contract.outputs)
            a_in = set(mod_a.contract.inputs)

            # A → B
            forward = a_out & b_in
            if forward:
                result["compatible_pairs"].append({
                    "from": mod_a.name, "to": mod_b.name,
                    "overlap": sorted(forward), "direction": "forward"
                })

            # B → A
            backward = b_out & a_in
            if backward:
                result["compatible_pairs"].append({
                    "from": mod_b.name, "to": mod_a.name,
                    "overlap": sorted(backward), "direction": "backward"
                })

    result["passed"] = len(result["compatible_pairs"]) > 0
    if not result["passed"]:
        result["errors"].append("没有找到兼容的模块组合")

    return result
