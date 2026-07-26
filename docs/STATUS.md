# SMS 项目状态总结（截至 2026-07-21）

## 项目是什么（不变的定位，来自 README/VISION，已核实仍然成立）

软件的第一公民不是代码：代码是化石，决策是回应，问题是根源。
    Problem -> Decision -> Module -> Product

SMS 不是：IDE / 编译器 / 编程语言 / AI 编程助手 / 日常编码工具（直接对话写脚本更快）。
SMS 是：管理模块间关系（谁依赖谁、接口对不对）+ 验证演化安全（换了模块会不会崩）。

## 核心产品定位（历史演变，避免重新论证）

最初设想：多语言编译器（Python→Rust/C++）+ 模块工厂 + 激活 `_archive` 里 4500 行传统编译器。
**已推翻**：多语言翻译是伪需求，AI 真正需要的是"改了会不会崩"的确定性保障，不是代码生成能力。
**最终定位：杀死 Codegen 和多语言翻译，`_archive/` 里的编译器是废弃代码，不要复活、不要参考。SSA/CFG/Contract 类 Pass 的核心思想只保留其"验证"部分，服务于模块工厂主线。**

> 旧的 ARCHITECTURE.txt / PROJECT_VISION.txt / ROADMAP.txt 描述的"双核架构"（模块工厂 + 传统编译器多后端）已废弃并删除，本文件是唯一权威状态来源。

## 已完成的清理（归档决策）

- `compiler_ssa/` 全部（CFG、Dominator、CallGraph、SSA、passes/）→ `_archive/compiler_ssa_frozen/`
- `backend/rust_backend.py`、`python_backend.py`、`backend.py`（多语言 Codegen）→ `_archive/backend_codegen/`
- 旧 `builder/builder.py` → 已删除，替代品是 `sms/factory/emit.py`
- 共 189+ 个文件归档

## 现有代码目录结构（来自旧 ARCHITECTURE.txt，未逐一重新核实，仅供定位参考）

    sms/
      core/         知识图谱核心（注意：core/module.py 里的 Module 类已废弃，不是真正生效的定义，见下）
      assembly/     装配引擎 + 行为验证
      module/       标准模块定义（真正生效的 Module/Capability/Contract/Evidence 都在这里）
      concept/      能力概念注册表
      registry/     模块注册表（持久化）
      ir/           中间表示
      builder/      产品构建器（现在只剩 param_checker.py / return_checker.py）
      importer/     Python 导入器（旧文档标注"将被精简"，未核实当前状态）
      _archive/     已废弃归档，不要复活、不要参考

## 确认保留的部分（有真实调用链，验证过）

- `ir/`（IRModule, IRFunction, IRCompiler, IROptimizer，271行）——IROptimizer 确认只做"清洁/规范化"，不做性能优化，无害
- `builder/` —— 现在只剩 `param_checker.py`、`return_checker.py`、`__init__.py`。两个 checker 是独立检查逻辑，代码完整但当前无任何调用方引用（2026-07-26 grep 全项目确认），未接入验证调用链。
- `backend/python/builder.py` —— 被 emit.py 和 runtime 依赖
- `sms/factory/emit.py` —— 代码生成器（生成 dist/ 产品，不是 Codegen 优化）

## 真正生效的代码结构（避免每次重新定位）

- 真正被 `registry/registry.py` 使用的 `Module` 类定义在 **`module/module.py`**（字段：name/version/package_type/capabilities/contract/evidence/submodules/version_history/quality_state/author/origin/state），**不是** `core/module.py` 里字段不同的旧定义
- `Capability` → `module/capability.py`（name/description/input_type/output_type/optional/parameters/implementation）
- `Contract` → `module/contract.py`（**version/inputs/outputs/permissions/constraints/runtime，没有 dependencies 字段** —— 这点很重要，见下方 bug 记录）
- `Evidence` → `module/evidence.py`（test_pass/coverage/benchmark/signed/test_count/fail_count/test_results/checked_at/checked_by）
- 真实注册数据落盘在 `dist/registry.json`，按模块名分组、每版本一条记录
- `.smsrepo/*/abi.json`（params/returns 格式，带 .cpp/.rs）是旧多语言 Codegen 时代遗留的另一套 schema，**不要**参照这套格式写新模块
- `upgrade_module()` 状态机完整约定写在 `registry/registry.py` 文件头部 docstring，是唯一权威来源，每次先 `head -30 registry/registry.py` 确认，不要凭记忆复述

## 验证检查器：独立逻辑，未接入调用链（2026-07-26核实）

1. 参数个数检查（inspect.signature）
2. 参数类型检查
3. 返回结构检查

跑通闭环：改函数签名（2参数→1参数），调用处未同步修改，验证器正确报错拦截 `❌ 期望2个参数，实际1个 → 必崩`，阻止运行。用真实签名比对，不是历史记录或调用处参数个数，这个闭环是真实的。

**能力边界（不要混淆维度）**：现有三层检查都是"接口层/签名层"验证，不能覆盖"函数内部控制流"类 bug（如变量未在所有路径赋值、`UnboundLocalError`），那是 CFG 分析范畴，是独立维度。

## 模块工厂：upgrade_module 状态机（四态，已完成）

基于 Analyzer 1.0.0→2.0.0（remember 被删/plan 类型变了/execute 新增）验证过：
- `blocked` —— 破坏性变更，未确认，数据不变（dry_run 和非 dry_run 都适用）
- `upgraded_forced` —— 破坏性变更，已用 force_upgrade 确认，数据已变
- `warning` —— 兼容变更（如新增能力），自动生效，仅提示

中途发现并修复一个真实 bug：force_upgrade 场景下 status 显示 `blocked` 但版本号已变成 2.0.0，状态与数据不一致。已修复，现在 `status: upgraded_forced` 与数据一致。

## 首次真实项目接入：GameRenderer（无界）

选定无界的 `ui/game_renderer.py` 里的 `draw(game)` 函数注册进 registry —— 这是 SMS 第一次接入真实在写的项目模块，不再是 Calculator/Analyzer 自造样本。

选择理由：签名干净（单参数 `game`，无返回值），四处调用（`play_state.py`/`build_state.py`/`look_state.py`/`dig_state.py`）全部一致 `draw(self.game)`，且正好对应过一次真实崩溃（`UnboundLocalError: 's1'`，属于 CFG 维度，不是接口层验证能拦的，两者不要混淆）。

注册时如实填写 Evidence：没有自动化测试，`test_pass=False`、`quality_state=PENDING`，不为了让 `ready()` 返回 True 而编造证据。

**跑通两组真实 diff 验证：**
- 新增 `draw_debug_overlay` 能力（1.0.0→1.1.0）→ 正确判定 `status: warning`
- 移除 `draw` 能力（1.0.0→2.0.0）→ 正确判定 `status: blocked`，`hard_blocks` 正确列出被删能力

**需要注意的局限**：两组测试的 `affected: []` 只说明当前 registry 里没有第二个模块声明依赖 GameRenderer，不代表"依赖传播"链路已经验证过——这是两件不同的事，diff 分类逻辑准了，但传播链路还是空白。

## 已知未修复的真实 bug（2026-07-21 排查确认，不是猜测）

`_find_dependents`（`registry/registry.py:188-199`）依赖传播判断**当前两条路径都是死的**，接入第二个真实模块前必须先修：

1. `contract.dependencies` 路径（第196行 `getattr(mod.contract, 'dependencies', [])`）——`Contract` 类根本没有 `dependencies` 字段（真实字段是 version/inputs/outputs/permissions/constraints/runtime），永远拿到 `[]`。`dependencies` 字段只存在于废弃的 `core/module.py` 旧 Module 定义里，和真正生效的 Contract 无关。
2. `submodules` 路径（第193行 `module_name in (mod.submodules or [])`）——`submodules` 真实类型是 `List[dict]`（在 `module/module.py:54` 确认），但这行代码拿一个字符串去判断是否在一堆 dict 里，永远是 False。类型和判断逻辑对不上。

**已修复并真实验证（2026-07-26）**：选择了submodules这条路径。`python_importer.py`新增`_extract_imports`，扫描AST的Import/ImportFrom节点，把导入的模块名写入`submodules`（格式`{"name": ...}`）。`_find_dependents`改为匹配这个真实结构，同时删除`contract.dependencies`路径（Contract类从无此字段，所有真实调用点从未传过该参数，确认是死代码）。真实验证：PythonImporter对含5个真实import语句的源码测试，submodules正确提取全部5个；注册GameRenderer+PlayState两个真实模块（PlayState.submodules声明依赖GameRenderer），`_find_dependents('GameRenderer')`正确返回`['PlayState']`。依赖传播链路首次真实跑通。

## 当前最大缺口 / 待办

1. **✅ 已完成（2026-07-26）**：`_find_dependents` bug 已修复——`python_importer.py` 新增 `_extract_imports` 从 AST 提取真实 import，`_find_dependents` 改为匹配 `submodules` 里 dict 的 `"name"` 键，`contract.dependencies` 死路径已删除。真实验证：Importer 正确提取 5 个 import，两个真实模块（PlayState 依赖 GameRenderer）的 `_find_dependents` 返回 `['PlayState']`。依赖传播链路首次真实跑通，此前"前提条件未满足"已解除，可以接入第二个真实模块测 affected 非空行为。
2. 长期待定：是否给验证引擎新增"函数内部控制流安全"独立维度（区别于现有接口层检查），需要重新引入类似 CFG 的分析，但范围必须严格限定在"验证服务"，不能演变回 Codegen 优化老路。
3. 无界当前未 commit 的 `play_state.py` 改动纯属内部实现调整，未触及对外接口，不适合作为跨模块验证案例。
