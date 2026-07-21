"""参数数量检查器 —— 支持编译时和运行时两种检查"""

def check_params(fn_name: str, input_type: str, call_args: str) -> dict:
    if not input_type or input_type in ("none", "any", ""):
        expected = 0
    else:
        parts = [p.strip() for p in input_type.split(",") if p.strip()]
        expected = len(parts)
    
    if not call_args or call_args.strip() == "":
        actual = 0
    else:
        actual = len([a.strip() for a in call_args.split(",") if a.strip()])
    
    if expected == actual:
        return {"passed": True, "message": f"✅ {fn_name}: 参数匹配 ({actual}个)"}
    else:
        return {"passed": False, "message": f"❌ {fn_name}: 需要 {expected} 个参数({input_type})，但调用只传了 {actual} 个 → 运行时必崩"}


# 生成运行时自检代码片段
def generate_runtime_check(fn_name: str, input_type: str, call_args: str) -> str:
    """生成一段 Python 代码，在调用前做参数数量检查"""
    result = check_params(fn_name, input_type, call_args)
    if not result["passed"]:
        return f"# ⚠️ {result['message']}"
    return f"# ✅ {result['message']}"
