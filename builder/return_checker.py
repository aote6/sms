"""返回结构检查器"""

# 每种行为模板承诺的必须字段
REQUIRED_FIELDS = {
    "code_executor": ["status", "output"],
    "dict_store": ["status"],
    "file_operator": ["status"],
    "file_store": ["status", "id"],
    "llm_planner": ["status", "steps"],
    "llm_react": ["status", "action"],
    "dispatcher": ["status"],
    "message_pass": ["status", "response"],
    "llm_debate": ["status", "consensus"],
    "default": ["status"],
}


def get_required_fields(behavior: str) -> list:
    """获取某个行为模板的必须返回字段"""
    return REQUIRED_FIELDS.get(behavior, ["status"])


def generate_return_check(fn_name: str, behavior: str) -> str:
    """生成返回值检查代码"""
    fields = get_required_fields(behavior)
    checks = []
    for field in fields:
        checks.append(f'    if "{field}" not in result_{fn_name}:')
        checks.append(f'        errors.append("❌ {fn_name}: 返回值缺少必须字段 \\"{field}\\"")')
    return "\n".join(checks)
