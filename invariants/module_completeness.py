"""定界契约：单模块完整性检查

检查单个 Module 是否具备完整信息：
- contract 是否存在
- capability 的 input_type/output_type 是否完整
"""

from typing import List, Dict, Any
from module.module import Module


def check_module_completeness(module: Module) -> Dict[str, Any]:
    """检查模块信息完整性，返回 {passed, checks, errors}"""
    result = {"module": module.name, "passed": True, "checks": [], "errors": []}

    # 1. contract 必须存在
    if module.contract is None:
        result["passed"] = False
        result["errors"].append("缺少 Contract")
        return result

    result["checks"].append({
        "type": "contract_exists",
        "passed": True,
        "detail": f"inputs={module.contract.inputs}, outputs={module.contract.outputs}"
    })

    # 2. capability 不能为空
    if not module.capabilities:
        result["passed"] = False
        result["errors"].append("缺少 Capability")
        return result

    # 3. 每个 capability 的 input_type/output_type 必须完整
    for cap in module.capabilities:
        cap_ok = True
        detail_parts = []

        if cap.input_type in ("any", "", None):
            cap_ok = False
            detail_parts.append("输入类型未定义")
        if cap.output_type in ("any", "", None):
            cap_ok = False
            detail_parts.append("输出类型未定义")

        check = {
            "type": "capability_type",
            "name": cap.name,
            "passed": cap_ok,
            "detail": "; ".join(detail_parts) if detail_parts else f"输入={cap.input_type}, 输出={cap.output_type}"
        }

        result["checks"].append(check)
        if not cap_ok:
            result["passed"] = False
            result["errors"].append(f"Capability '{cap.name}' 类型不完整")

    return result
