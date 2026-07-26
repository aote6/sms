"""
SMS + Kuai 集成版

SMS 负责增量调度，Kuai 负责执行。
模块 = Kuai flow 文件，指纹 = flow 内容 hash，缓存命中跳过。
每个模块在独立临时目录中执行，测试隔离。
"""

import os, sys, time, shutil, tempfile, hashlib

KUAI_HOME = '/data/data/com.termux/files/home/kuai'
sys.path.insert(0, KUAI_HOME)

from module import Module, Capability, Contract, Evidence, QualityState
from registry import ModuleRegistry
from build import BuildCache

from flow.parser import parse_flow
from flow.registry import build_executable_blocks
from core.engine import Engine
from core.state import State

TEST_FIXTURE = os.path.expanduser("~/test_project")


def prepare_test_dir():
    tmpdir = tempfile.mkdtemp(prefix="sms_test_")
    if os.path.isdir(TEST_FIXTURE):
        shutil.copytree(TEST_FIXTURE, tmpdir, dirs_exist_ok=True)
    else:
        os.makedirs(tmpdir, exist_ok=True)
    return tmpdir


def flow_fingerprint(flow_path: str) -> str:
    with open(flow_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


class KuaiExecutor:
    def __init__(self, flow_dir=f"{KUAI_HOME}/flows"):
        self.flow_dir = flow_dir
    
    def execute(self, module_name: str, work_dir: str) -> dict:
        flow_file = os.path.join(self.flow_dir, f"{module_name}.flow")
        with open(flow_file, "r", encoding="utf-8") as f:
            text = f.read()
        
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
        name=name, version="1.0.0",
        quality_state=QualityState.PASSED,
        capabilities=[Capability(name, f"执行 {name} 流水线", "state", "state")],
        contract=Contract(runtime="python"),
        evidence=Evidence(test_pass=True, coverage=0.0, benchmark=0.0),
    )
    registry.register(module)

print(f"已注册 {len(registry.modules)} 个模块")

# —— 第一阶段：计算所有指纹，对比缓存，确定 dirty 集合 ——
cache = BuildCache()
flow_dir = f"{KUAI_HOME}/flows"
dirty_modules = set()
clean_modules = set()

for name in registry.modules.keys():
    fp = flow_fingerprint(os.path.join(flow_dir, f"{name}.flow"))
    entry = cache.get(name)
    if entry and entry.fingerprint == fp:
        clean_modules.add(name)
    else:
        dirty_modules.add(name)

print(f"指纹比对: {len(dirty_modules)} 个变更, {len(clean_modules)} 个缓存命中\n")

# —— 第二阶段：执行 dirty 模块 ——
print(f"{'='*60}")
print(f"SMS 增量调度 + Kuai 执行 — {len(dirty_modules)} 个需构建")
print('='*60)

kuai = KuaiExecutor()
ok, fail, skipped = 0, 0, len(clean_modules)

for name in clean_modules:
    print(f"  ⏭ {name} (缓存命中)")

for name in sorted(dirty_modules):
    work_dir = prepare_test_dir()
    print(f"  🔨 {name}...", end=" ")
    start = time.time()
    try:
        result = kuai.execute(name, work_dir)
        elapsed = time.time() - start
        if result["status"] == "ok":
            print(f"✅ ({elapsed:.2f}s) {result['task']}")
            ok += 1
            # 更新缓存
            fp = flow_fingerprint(os.path.join(flow_dir, f"{name}.flow"))
            from build.cache_entry import CacheEntry
            cache.put(CacheEntry(
                module=name, fingerprint=fp, artifact="",
                abi="", package="", timestamp=time.time()
            ))
        else:
            print(f"❌ {result.get('error', '未知错误')}")
            fail += 1
    except Exception as e:
        print(f"❌ {str(e)[:80]}")
        fail += 1
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

cache.save()

print(f"\n✅ {ok} 构建  ⏭ {skipped} 跳过  ❌ {fail} 失败")
print(f"总计: {ok+skipped+fail}/{len(registry.modules)} 个模块")
