"""
registry.upgrade_module 的契约检查
使用定界风格：纯 Python 条件判断，运行时拦截
"""
import os
import sys
sys.path.insert(0, os.path.expanduser("~/lu/core"))
try:
    import op_log
except ImportError:
    op_log = None

from module import Module


def check_upgrade_preconditions(module_name: str, new_module: Module, old_module: Module):
    """
    升级前置条件：
    1. module_name 不能为空
    2. new_module 不能为 None
    3. new_module.name 必须等于 module_name
    4. 版本号必须递增
    """
    if not module_name:
        if op_log:
            op_log.log_op("contract_check", "registry.upgrade_module", "failed", detail="module_name 不能为空")
        raise ValueError("module_name 不能为空")

    if new_module is None:
        if op_log:
            op_log.log_op("contract_check", "registry.upgrade_module", "failed", detail="new_module 不能为 None")
        raise ValueError("new_module 不能为 None")

    if new_module.name != module_name:
        if op_log:
            op_log.log_op("contract_check", "registry.upgrade_module", "failed", detail=f"模块名不匹配: {new_module.name} != {module_name}")
        raise ValueError(
            f"模块名不匹配: new_module.name='{new_module.name}' != module_name='{module_name}'"
        )

    if old_module is not None:
        if not _version_gt(new_module.version, old_module.version):
            if op_log:
                op_log.log_op("contract_check", "registry.upgrade_module", "failed", detail=f"版本号未递增: new={new_module.version} <= old={old_module.version}")
            raise ValueError(
                f"版本号必须递增: new={new_module.version} <= old={old_module.version}"
            )

    if op_log:
        op_log.log_op("contract_check", "registry.upgrade_module", "success", detail=f"{module_name} 前置检查通过")


def _version_gt(v1: str, v2: str) -> bool:
    """semver 比较：v1 > v2"""
    try:
        p1 = [int(x) for x in v1.split(".")]
        p2 = [int(x) for x in v2.split(".")]
        # 补齐长度
        while len(p1) < len(p2):
            p1.append(0)
        while len(p2) < len(p1):
            p2.append(0)
        return p1 > p2
    except (ValueError, AttributeError):
        # 非 semver 格式，退回字符串比较
        return v1 > v2
