from core import *
from module import Module, Capability, Contract, Evidence
from assembly import AssemblyEngine
from registry import ModuleRegistry
from resolver import GapResolver
from ir import IRCompiler, IROptimizer
from backend import PythonBackend
from runtime import RuntimeLoader
from build import BuildCache, Scheduler

# 1. 知识图谱
graph = KnowledgeGraph()

problem = graph.add_node(Node("输入法需要统一键盘", NodeType.PROBLEM))
decision = graph.add_node(Node("界面和输入引擎分离", NodeType.DECISION))
module1 = graph.add_node(Node("KeyboardRenderer", NodeType.MODULE))
module2 = graph.add_node(Node("PinyinEngine", NodeType.MODULE))
module3 = graph.add_node(Node("GestureDetector", NodeType.MODULE))
product = graph.add_node(Node("LingTi Keyboard", NodeType.PRODUCT))

graph.connect(product, problem, EdgeType.ANSWER)
graph.connect(problem, decision, EdgeType.ANSWER)
graph.connect(decision, module1, EdgeType.CREATE)
graph.connect(decision, module2, EdgeType.CREATE)
graph.connect(decision, module3, EdgeType.CREATE)

# 2. 模块仓库
registry = ModuleRegistry()

kb_module = Module(
    name="KeyboardRenderer",
    version="1.0.0",
    state="ready",
    capabilities=[
        Capability("render", "渲染键盘界面", "key_events", "display"),
        Capability("layout", "管理键盘布局", "config", "layout_data")
    ],
    contract=Contract(runtime="python"),
    evidence=Evidence(test_pass=True, coverage=0.85, benchmark=100.0)
)
registry.register(kb_module)

py_module = Module(
    name="PinyinEngine",
    version="0.5.0",
    state="draft",
    capabilities=[],
    contract=None,
    evidence=None
)
registry.register(py_module)

# 3. 装配引擎
engine = AssemblyEngine(graph)
for node in graph.nodes.values():
    if node.node_type == NodeType.MODULE:
        mod = registry.get(node.name)
        if mod:
            engine.register_module(node, mod)

# 4. Gap Resolver
plan = engine.create_plan(product)
resolver = GapResolver(registry)
for node in plan.nodes.values():
    if node.kind == NodeType.MODULE.value and node.module is None:
        mod = Module(
            name=node.name,
            version="0.0.1",
            state="todo",
            capabilities=[Capability("TODO", f"需要实现 {node.name}")],
            contract=Contract(runtime="python"),
            evidence=Evidence()
        )
        registry.register(mod)
        node.module = mod
        print(f"⚡ GAP RESOLVED: 生成模块 '{node.name}'")

print("\n【最终装配计划 - DAG】")
plan.show()

# 5. 增量构建 + Artifact
print("\n" + "="*60)
print("构建系统 (Artifact + Runtime)")
print("="*60)

cache = BuildCache()
compiler = IRCompiler()
optimizer = IROptimizer(level=2)
backend = PythonBackend()
loader = RuntimeLoader()

artifacts = []

for node in plan.topological_sort():
    if not node.module or not node.module.ready():
        continue
    
    print(f"\n📦 处理: {node.module.name}")
    ir = compiler.compile(node.module)
    ir_opt = optimizer.optimize(ir)
    
    # 检查缓存
    if not cache.changed(node.id, ir_opt):
        print(f"   ⏩ 跳过 (未变化): {node.name}")
        continue
    
    # 生成 Artifact
    artifact = backend.emit(ir_opt)
    cache.update(node.id, ir_opt)
    artifacts.append(artifact)
    
    # 加载并测试
    try:
        instance = loader.create(artifact)
        print(f"   ✅ 加载成功: {artifact.module} v{instance.version}")
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")

cache.save()
print(f"\n✅ 构建完成: {len(artifacts)} 个 Artifact")
for a in artifacts:
    print(f"   - {a.module} ({a.language}) -> {a.path}")
