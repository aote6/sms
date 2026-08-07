# SMS — 增量构建调度器

SMS 是 Kuai 的增量构建调度层。它决定"什么时候构建、构建谁、跳过谁"，Kuai 负责执行。

## 核心机制

- 指纹：每个模块（Kuai flow 文件）计算 SHA256 指纹
- 缓存：指纹不变跳过，变了才重编
- 隔离：每个模块在独立临时目录执行，副作用互不影响
- 并行：支持多 worker 并行构建

## 快速开始

cd ~/sms && python main.py

首次全量构建 23 个模块，再次运行全部缓存命中。

## 目录

| 目录 | 职责 |
|---|---|
| module/ | 模块定义 |
| build/ | 增量构建引擎 |
| registry/ | 模块注册表 |
| resolver/ | 缺失模块检测 |
| invariants/ | 完整性检查 |
| main.py | 入口 |

## 归档

_archive/ 下保留了 SSA 编译器和旧 pipeline 实现。
