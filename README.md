# SMS - Software Manufacturing System

软件制造系统。不是 IDE，不是编译器，不是编程语言，不是 AI 编程助手。

## 核心思想

代码是化石，决策是回应，问题是根源。
SMS 保存的不是代码，是软件之所以成为软件的认知根源。

    Problem -> Decision -> Module -> Product

## 当前定位（2026-07-21 确认，唯一权威见 docs/STATUS.md）

模块工厂 + 验证引擎：验证"改了会不会崩"，不做代码生成、不做多语言编译。

## 文档

- 项目状态与架构（唯一权威）: docs/STATUS.md
- 标准模块规范: docs/STANDARD_MODULE_SPEC.md
- 会话交接: docs/HANDOFF.md（每次会话结束时按需生成，当前尚未生成过，不存在也正常）

## 快速开始

    cd sms
    python3 main.py
