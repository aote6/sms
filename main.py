"""
SMS Demo Entry Point (2026-07-26)

从 registry 里的模块出发，经过 invariants 完整性检查 -> BuildGraph 依赖排序
-> BuildDriver(增量构建: 指纹+缓存+并行) -> RuntimeLoader 动态加载
"""

from module import Module, Capability, Contract, Evidence, QualityState
from registry import ModuleRegistry
from resolver import GapResolver
from ir import IRCompiler
from backend.python.builder import PythonBuilder
from runtime import RuntimeLoader
from build import BuildGraph, BuildCache, BuildScheduler, BuildExecutor, BuildDriver
from build.artifact import Artifact
from invariants.module_completeness import check_module_completeness
from sms_build_adapters import BackendAdapter, SimplePackager


# 1. 模块仓库
registry = ModuleRegistry()

kb_module = Module(
    name="KeyboardRenderer",
    version="1.0.0",
    quality_state=QualityState.PASSED,
    capabilities=[
        Capability("render", "渲染键盘界面", "key_events", "display"),
        Capability("layout", "管理键盘布局", "config", "layout_data"),
    ],
    contract=Contract(runtime="python"),
    evidence=Evidence(test_pass=True, coverage=0.85, benchmark=100.0),
)
registry.register(kb_module)

py_module = Module(
    name="PinyinEngine",
    version="0.5.0",
    quality_state=QualityState.BLANK,
    capabilities=[],
    contract=None,
    evidence=None,
)
registry.register(py_module)

# 2. 建 BuildGraph（从 registry 已注册模块）
build_graph = BuildGraph()
for name in registry.modules.keys():
    build_graph.node(name)
for name, module in registry.modules.items():
    for sub in (module.submodules or []):
        dep_name = sub.get("name") if isinstance(sub, dict) else None
        if dep_name:
            build_graph.add_dependency(name, dep_name)

# 3. Gap Resolver —— 扫描 BuildGraph 节点，没注册的自动生成 TODO
gap_resolver = GapResolver(registry)
gap_resolver.resolve_graph(build_graph)
gap_resolver.summary()

# 4. 只把就绪的模块标记为待构建
for name, module in registry.modules.items():
    if module.ready():
        build_graph.mark_dirty(name)
    else:
        print(f"  ⏭ 跳过未就绪模块: {name} (quality_state={module.quality_state})")

build_graph.summary()

# 5. 定界完整性检查
print("\n【定界: 模块完整性检查】")
for name, module in registry.modules.items():
    result = check_module_completeness(module)
    mark = "✅" if result["passed"] else "❌"
    detail = "OK" if not result["errors"] else "; ".join(result["errors"])
    print(f"  {mark} {name}: {detail}")

# 6. 增量构建
print("\n" + "=" * 60)
print("构建系统 (build/ 增量构建引擎)")
print("=" * 60)

cache = BuildCache()
compiler = IRCompiler()
python_builder = PythonBuilder(output_dir="./dist")
backend = BackendAdapter(python_builder)
packager = SimplePackager()

executor = BuildExecutor(
    registry=registry,
    compiler=compiler,
    backend=backend,
    packager=packager,
    cache=cache,
)
scheduler = BuildScheduler(build_graph)
driver = BuildDriver(scheduler=scheduler, executor=executor, workers=4)

built = driver.run(build_graph)
driver.journal.summary()

# 7. 加载验证
print("\n【运行时加载验证】")
loader = RuntimeLoader()

validated = set()
for result in driver.results:
    if not result.success:
        continue
    artifact_path = result.artifact
    if artifact_path == "cached":
        entry = cache.get(result.task)
        artifact_path = entry.artifact if entry else None
    if not artifact_path:
        continue
    validated.add(result.task)
    module = registry.get(result.task)
    art = Artifact.create(
        module=result.task,
        version=module.version if module else "",
        language="python",
        path=artifact_path,
    )
    try:
        instance = loader.create(art)
        print(f"  ✅ 加载成功: {result.task} v{instance.version}")
    except Exception as e:
        print(f"  ❌ 加载失败: {result.task}: {e}")

# 缓存兜底校验
for name, module in registry.modules.items():
    if name in validated or not module.ready():
        continue
    entry = cache.get(name)
    if not entry:
        continue
    art = Artifact.create(module=name, version=module.version, language="python", path=entry.artifact)
    try:
        instance = loader.create(art)
        print(f"  ✅ 加载成功(缓存): {name} v{instance.version}")
    except Exception as e:
        print(f"  ❌ 加载失败(缓存): {name}: {e}")

print(f"\n✅ 构建完成: {len(built)} 个模块")
