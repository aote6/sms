"""
SMS + Kuai 集成版

SMS 负责增量调度，Kuai 负责执行。
模块 = Kuai flow 文件，构建 = 执行 flow。
每个模块在独立的临时目录中执行，测试隔离。
"""

import os, sys, time, shutil, tempfile

KUAI_HOME = '/data/data/com.termux/files/home/kuai'
sys.path.insert(0, KUAI_HOME)

from module import Module, Capability, Contract, Evidence, QualityState
from registry import ModuleRegistry
from build import BuildGraph

from flow.parser import parse_flow
from flow.registry import build_executable_blocks
from core.engine import Engine
from core.state import State


# 测试数据模板目录
TEST_FIXTURE = os.path.expanduser("~/test_project")


def prepare_test_dir():
    """复制模板目录到临时位置，返回临时目录路径"""
    tmpdir = tempfile.mkdtemp(prefix="sms_test_")
    if os.path.isdir(TEST_FIXTURE):
        shutil.copytree(TEST_FIXTURE, tmpdir, dirs_exist_ok=True)
    else:
        os.makedirs(tmpdir, exist_ok=True)
    return tmpdir


class KuaiExecutor:
    def __init__(self, flow_dir=f"{KUAI_HOME}/flows"):
        self.flow_dir = flow_dir
    
    def execute(self, module_name: str, work_dir: str) -> dict:
        """在指定的 work_dir 中执行模块"""
        flow_file = os.path.join(self.flow_dir, f"{module_name}.flow")
        if not os.path.exists(flow_file):
            return {"status": "error", "error": f"flow 文件不存在: {flow_file}"}
        
        with open(flow_file, "r", encoding="utf-8") as f:
            text = f.read()
        
        # 替换 flow 中的路径为临时工作目录
        text = text.replace('/data/data/com.termux/files/home/test_project', work_dir)
        text = text.replace('/data/data/com.termux/files/home/图片测试', work_dir)
        text = text.replace('/data/data/com.termux/files/home/归档测试', work_dir)
        
        parsed = parse_flow(text)
        executable = build_executable_blocks(parsed)
        
        engine = Engine(verbose=False)
        current_state = State()
        blocks_only = []
        for block, injections in executable:
            if injections:
                current_state = current_state.with_updates(**injections)
            blocks_only.append(block)
        
        try:
            final_state = engine.run_sequence(blocks_only, current_state)
            return {"status": "ok", "task": parsed['task'], "state": dict(final_state)}
        except Exception as e:
            return {"status": "error", "error": str(e)}


# 注册模块
registry = ModuleRegistry()
flow_dir = f"{KUAI_HOME}/flows"
for flow_file in sorted(os.listdir(flow_dir)):
    if not flow_file.endswith('.flow'):
        continue
    name = flow_file.replace('.flow', '')
    module = Module(
        name=name,
        version="1.0.0",
        quality_state=QualityState.PASSED,
        capabilities=[Capability(name, f"执行 {name} 流水线", "state", "state")],
        contract=Contract(runtime="python"),
        evidence=Evidence(test_pass=True, coverage=0.0, benchmark=0.0),
    )
    registry.register(module)

print(f"已注册 {len(registry.modules)} 个模块")

# BuildGraph
build_graph = BuildGraph()
for name in registry.modules.keys():
    build_graph.node(name)
    build_graph.mark_dirty(name)

print(f"\n{'='*60}")
print(f"SMS 调度 + Kuai 执行 — {len(registry.modules)} 个模块 (隔离测试)")
print('='*60)

kuai = KuaiExecutor()
ok, fail = 0, 0
for name in sorted(registry.modules.keys()):
    # 每个模块独立临时目录
    work_dir = prepare_test_dir()
    print(f"  🔨 {name}...", end=" ")
    start = time.time()
    try:
        result = kuai.execute(name, work_dir)
        elapsed = time.time() - start
        if result["status"] == "ok":
            print(f"✅ ({elapsed:.2f}s) {result['task']}")
            ok += 1
        else:
            print(f"❌ {result.get('error', '未知错误')}")
            fail += 1
    except Exception as e:
        print(f"❌ {str(e)[:80]}")
        fail += 1
    finally:
        # 清理临时目录
        shutil.rmtree(work_dir, ignore_errors=True)

print(f"\n✅ {ok}/{ok+fail} 个模块构建成功")
