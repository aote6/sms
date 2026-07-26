"""
SMS Demo Entry Point (2026-07-26 重构版)

从 registry 里的模块出发，经过 invariants 完整性检查 -> BuildGraph 依赖排序
-> BuildDriver(增量构建: 指纹+缓存+并行) -> RuntimeLoader 动态加载

变更说明见 docs/handoffs 或对应交接文档，核心变化：assembly/ 已归档，
不再作为知识图谱到构建计划的中转层。
"""

from core import *
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


# 1. 知识图谱 —— 仅作叙事性展示，不再驱动构建（assembly/已归档）
graph_kg = KnowledgeGraph()
problem = graph_kg.add_node(Node("输入法需要统一键盘", NodeType.PROBLEM))
decision = graph_kg.add_node(Node("界面和输入引擎分离", NodeType.DECISION))
module1 = graph_kg.add_node(Node("KeyboardRenderer", NodeType.MODULE))
module2 = graph_kg.add_node(Node("PinyinEngine", NodeType.MODULE))
module3 = graph_kg.add_node(Node("GestureDetector", NodeType.MODULE))
product = graph_kg.add_node(Node("LingTi Keyboard", NodeType.PRODUCT))
graph_kg.connect(product, problem, EdgeType.ANSWER)
graph_kg.connect(problem, decision, EdgeType.ANSWER)
graph_kg.connect(decision, module1, EdgeType.CREATE)
graph_kg.connect(decision, module2, EdgeType.CREATE)
graph_kg.connect(decision, module3, EdgeType.CREATE)

print("【问题-决策-模块 知识图谱】")
graph_kg.show()

# 2. 模块仓库
registry = ModuleRegistry()

kb_module = Module(
    name="KeyboardRenderer",
    version="1.0.0",
    quality_state=QualityState.PASSED,   # 原 state="ready"，按状态机语义映射
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
    quality_state=QualityState.BLANK,    # 原 state="draft"
    capabilities=[],
    contract=None,
    evidence=None,
)
registry.register(py_module)

# 3. 依据"知识图谱里的模块节点" + "registry已注册模块" 建 BuildGraph
module_node_names = {n.name for n in graph_kg.nodes.values() if n.node_type == NodeType.MODULE}
build_graph = BuildGraph()
for name in module_node_names | set(registry.modules.keys()):
    build_graph.node(name)
for name, module in registry.modules.items():
    for sub in (module.submodules or []):
        dep_name = sub.get("name") if isinstance(sub, dict) else None
        if dep_name:
            build_graph.add_dependency(name, dep_name)

# 4. Gap Resolver —— 扫描 BuildGraph 节点，registry 里没有对应模块的自动生成 TODO
gap_resolver = GapResolver(registry)
gap_resolver.resolve_graph(build_graph)
gap_resolver.summary()

# 5. 只把"就绪"的模块标记为待构建
for name, module in registry.modules.items():
    if module.ready():
        build_graph.mark_dirty(name)
    else:
        print(f"  ⏭ 跳过未就绪模块: {name} (quality_state={module.quality_state})")

build_graph.summary()

# 6. 定界完整性检查（构建前，对所有已注册模块检查，不只是 ready 的）
print("\n【定界: 模块完整性检查】")
for name, module in registry.modules.items():
    result = check_module_completeness(module)
    mark = "✅" if result["passed"] else "❌"
    detail = "OK" if not result["errors"] else "; ".join(result["errors"])
    print(f"  {mark} {name}: {detail}")

# 7. 增量构建（指纹 + 缓存 + 并行 + journal）
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

# 8. 加载并验证产物
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

# build/driver.py 对缓存命中的任务不写入 driver.results（已知缺口，
# 见交接文档），这里在 main.py 侧补一次兜底校验，不改 driver.py 本身
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
