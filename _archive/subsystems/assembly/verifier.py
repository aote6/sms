from typing import List, Dict, Any
from module import Module


class BehaviorVerifier:

    def verify_contract(self, module: Module, instance: Any = None) -> Dict[str, Any]:
        result = {"module": module.name, "passed": True, "checks": [], "errors": []}

        if not module.contract:
            result["passed"] = False
            result["errors"].append("无 Contract")
            return result

        contract = module.contract
        result["checks"].append({
            "type": "contract_exists",
            "passed": True,
            "detail": f"inputs={contract.inputs}, outputs={contract.outputs}"
        })

        if not module.capabilities:
            result["passed"] = False
            result["errors"].append("无 Capability")
            return result

        for cap in module.capabilities:
            cap_check = {"type": "capability", "name": cap.name, "passed": True, "detail": ""}
            if cap.input_type in ("any", "", None):
                cap_check["passed"] = False
                cap_check["detail"] = "输入类型未定义"
            elif cap.output_type in ("any", "", None):
                cap_check["passed"] = False
                cap_check["detail"] = "输出类型未定义"
            else:
                cap_check["detail"] = f"输入={cap.input_type}, 输出={cap.output_type}"

            if not cap_check["passed"]:
                result["passed"] = False
                result["errors"].append(f"Capability '{cap.name}' 类型不完整")
            result["checks"].append(cap_check)

        if instance:
            for cap in module.capabilities:
                fn = getattr(instance, cap.name, None)
                if fn is None:
                    result["checks"].append({"type": "runtime", "name": cap.name, "passed": False, "detail": "方法不存在"})
                    result["passed"] = False
                else:
                    result["checks"].append({"type": "runtime", "name": cap.name, "passed": True, "detail": "方法存在"})

        module.evidence.test_pass = result["passed"]
        module.evidence.test_count = len(result["checks"])
        module.evidence.fail_count = len(result["errors"])
        module.evidence.test_results = result["checks"]

        return result

    def verify_composition(self, modules: List[Module]) -> Dict[str, Any]:
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

                # 检查两个方向的兼容性
                forward = a_out & b_in
                backward = b_out & a_in

                if forward:
                    result["compatible_pairs"].append({
                        "from": mod_a.name, "to": mod_b.name,
                        "overlap": list(forward), "direction": "forward"
                    })
                if backward:
                    result["compatible_pairs"].append({
                        "from": mod_b.name, "to": mod_a.name,
                        "overlap": list(backward), "direction": "backward"
                    })

        result["passed"] = len(result["compatible_pairs"]) > 0
        return result
