# backend/__init__.py
# 原 BackendRegistry + Backend/PythonBackend/RustBackend 导入已移除。
# 这三个类对应的文件在 _archive/ 里，属于已废弃的多语言 Codegen。
# emit.py 和 main.py 目前直接 import backend.python_backend，
# 需要改为使用 backend/python/builder.py 里的 PythonBuilder。
# 此文件暂时保留为占位，不再做自动注册。
