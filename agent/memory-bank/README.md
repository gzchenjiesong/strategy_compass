---
title: 长期记忆总览
created: 2026-05-13
version: 1.0.0
---

# 长期记忆总览

> 项目的长期记忆库。所有角色均可读取，按职责更新。

## 记忆文件

| 文件 | 内容 | 更新频率 | 负责角色 |
|------|------|----------|----------|
| [active-context.md](active-context.md) | 当前状态、任务流水线 | 每次会话 | 所有角色 |
| [projectbrief.md](projectbrief.md) | 项目定位与范围 | 很少 | 产品经理 |
| [product-context.md](product-context.md) | 用户画像与核心体验 | 每月 | 产品经理 |
| [system-patterns.md](system-patterns.md) | 架构模式与技术约束 | 每迭代 | 架构师 |
| [tech-context.md](tech-context.md) | 技术栈与工具链 | 每迭代 | 架构师 |
| [progress.md](progress.md) | 模块完成状态 | 每迭代 | 审查者 |
| [optimization-plan.md](optimization-plan.md) | 优化计划与技术债务 | 每月 | 架构师 |

## 使用规则

1. **读取**：所有角色均可读取所有文件
2. **更新**：按上表"负责角色"更新，其他角色只读
3. **冲突**：同时更新时，后更新者覆盖，但需记录变更日志
4. **清理**：每月检查，过期信息归档到 `agent/archive/`

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-05-13 | 初始版本 |
