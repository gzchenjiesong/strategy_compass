---
title: 角色定义与启动模板
created: 2026-05-13
version: 1.0.0
---

# 角色定义与启动模板

> Strategy Compass 的 AI Agent 角色定义和会话启动模板。

## 角色列表

| 角色 | 职责 | 启动模板 |
|------|------|----------|
| [产品经理](product-manager.md) | 需求调研、筛选、定义 | 见 [startup-templates.md](startup-templates.md) |
| [架构师](architect.md) | 技术设计、接口定义 | 见 [startup-templates.md](startup-templates.md) |
| [编码者](coder.md) | 代码实现、自测 | 见 [startup-templates.md](startup-templates.md) |
| [审查者](reviewer.md) | 代码审查、验收 | 见 [startup-templates.md](startup-templates.md) |

## 快速启动

每次开启新会话时，根据角色复制 [startup-templates.md](startup-templates.md) 中的对应模板。

## 角色协作关系

```
产品经理 → 架构师 → 编码者 → 审查者
   ↑________↓_________↓_________↓
```

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-05-13 | 初始版本 |
