# SMS 项目状态

> 2026-07-26 更新：SMS+Kuai 集成完成，增量构建全线贯通

## SMS 现在是什么

SMS 是 Kuai 的增量构建调度器。

- 模块 = Kuai flow 文件
- 构建 = 执行 flow
- 增量 = flow 文件内容 SHA256 指纹 + 缓存
- 隔离 = 每个模块在独立临时目录中执行

SMS 不编译代码。它管理构建生命周期：注册模块、检查完整性、计算指纹、调度执行、记录日志。实际执行由 Kuai 完成。

## 当前能力

- 模块注册与定义（Module/Capability/Contract/Evidence/QualityState）
- 增量构建（指纹+缓存，改 1 个 flow 只重编 1 个）
- 并行调度（build/scheduler.py + thread_pool）
- 构建日志（build/journal.py）
- 构建前完整性检查（invariants/）
- 缺失模块自动生成 TODO（resolver/gap_resolver.py）
- Kuai 执行层接入（23 个模块验证通过）
- 测试隔离（每个模块独立临时目录，副作用互不影响）

## 架构

SMS（调度层）36 文件 2113 行 -> Kuai（执行层）

- module/     模块定义（5 文件）
- build/      增量构建引擎（23 文件）
- registry/   模块注册表
- resolver/   缺失模块检测
- invariants/ 完整性检查
- main.py     调度入口

## 验证方式

cd ~/sms && python main.py

首次全量构建 23 个模块，再次运行全部缓存命中。改 1 个 flow 文件只重编那 1 个。

## 已删除

- ir/ — 活编译器（模板填充器），已被 Kuai 执行层替代
- backend/ — PythonBuilder，不再需要
- runtime/ — 运行时加载器，不再需要
- sms_build_adapters.py — 适配层，不再需要
- core/ — 知识图谱（纯展示），已删除

## 归档

_archive/ 下保留：
- compiler_ssa_frozen/ — 完整 SSA 编译器（4061 行）
- subsystems/pipeline/ — build/ 引擎前身
- build_artifacts/ — .smspkg 打包格式示例
