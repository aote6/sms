# SMS Standard Module 规范 v0.2

（v0.1 是 .txt，第六节对齐表已过时——写着"需新增"的字段实际早已存在。本版本按 2026-07-21 STATUS.md 已确认的真实字段核对更正，未核实的字段明确标注"待核实"，不瞎填。）

## 定位

软件模块 = 电子元器件。SMS = 元器件制造工厂。借鉴电子元器件行业的规格书、品控、封装标准。

## 一、身份标签

| 字段 | 说明 | 必填 |
|---|---|---|
| 指纹 | SHA256 哈希，全球唯一 | 是 |
| 名称 | 人类可读模块名 | 是 |
| 版本号 | 主版本.次版本.修订号 | 是 |
| 封装类型 | atomic / composite / imported / generated | 是 |

## 二、数据手册（Datasheet）

功能概述 / 引脚定义(inputs/outputs) / 运行条件(runtime) / 性能参数(benchmark) / 精度指标(coverage/test_pass) / 极限条件(constraints) / 封装信息(submodules) / 版本历史(version_history)

## 三、品控标签（生命周期状态机）

blank → pending → testing → passed → maintained → scrapped
（testing → blank 返工 / testing → scrapped 放弃）

合格标记（状态变为 passed 需同时满足）：
1. Contract 已定义（inputs/outputs 明确）
2. Capability 已填写
3. test_pass = True
4. 覆盖率 >= 80%
5. benchmark 数据非空

## 四、来源信息

作者/团队(author) / 产地(origin: handwritten/ai_generated/imported/third_party) / 维护期限(expires_at，可选)

## 五、与现有代码的对齐（v0.2 更正版，依据 2026-07-21 STATUS.md 已确认事实）

| 规范字段 | 现有代码位置 | 状态 |
|---|---|---|
| 指纹 | build/fingerprint.py -> Fingerprint.module() | 已实现 |
| 名称 | module/module.py -> Module.name | 已实现 |
| 版本号 | module/module.py -> Module.version | 已实现 |
| 封装类型 | module/module.py -> Module.package_type | **已实现**（v0.1 误标"需新增"） |
| 功能概述 | module/capability.py -> Capability.description | 已实现 |
| 引脚定义 | module/contract.py -> Contract.inputs/outputs | 已实现 |
| 运行条件 | module/contract.py -> Contract.runtime | 已实现 |
| 性能参数 | module/evidence.py -> Evidence.benchmark | 已实现 |
| 精度指标 | module/evidence.py -> Evidence.coverage/test_pass | 已实现 |
| 极限条件 | module/contract.py -> Contract.constraints | 字段有，未充分利用 |
| 封装信息 | module/module.py -> Module.submodules（**类型是 List[dict]**） | **已实现**（v0.1 误标"需新增"，但见下方 bug 提醒） |
| 版本历史 | module/module.py -> Module.version_history | **已实现**（v0.1 误标"需新增"） |
| 质量状态 | module/module.py -> Module.quality_state（另有独立的 Module.state） | **已实现**（v0.1 误标"需扩展枚举"，quality_state 和 state 是两个不同字段，待核实两者具体分工） |
| 来源信息 | module/module.py -> Module.author/origin | **已实现**（v0.1 误标"需新增"） |
| 维护期限 | 未在 STATUS.md 确认过 | **待核实**，不确定是否已实现 |
| 生产批次 | build/artifact.py -> Artifact.generated_at | 已实现 |

**重要提醒**：`submodules` 虽然字段本身已实现，但 `registry/registry.py` 里读取它做依赖传播判断的逻辑有真实 bug（字符串去匹配 dict 列表，永远失败），详见 STATUS.md「已知未修复的真实 bug」一节，不要以为字段存在就等于依赖传播能用。
