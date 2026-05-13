---
title: 设计文档总览
created: 2026-05-13
version: 1.1.0
---

# 设计文档总览

> 所有技术设计与 UI 设计的入口。架构师维护此索引。

## 模块技术设计

| 模块 | 名称 | 状态 | 子文档 |
|------|------|------|--------|
| Module 0 | [用户系统](module-0-user/README.md) | 🔄 设计中 | api, data-model, flow |
| Module 1 | [数据底座](module-1-data/README.md) | 🔄 设计中 | api, data-model, flow |
| Module 2 | [新闻聚合](module-2-news/README.md) | 🔄 设计中 | api, data-model, flow |
| Module 3 | [市场概览](module-3-market/README.md) | 🔄 设计中 | api, data-model, flow |
| Module 4 | [估值分析](module-4-valuation/README.md) | 🔄 设计中 | api, data-model, flow |

## UI 设计

| 资源 | 说明 |
|------|------|
| [设计系统](design-system.md) | 颜色、字体、组件规范 |
| [交互原型](interactions/) | 交互说明与动效定义 |
| [视觉稿](mockups/) | 高保真视觉设计稿 |
| [线框图](wireframes/) | 页面结构与布局草图 |

## 架构决策记录 (ADR)

| 编号 | 决策 | 日期 | 状态 |
|------|------|------|------|
| ADR-001 | SQLite → PostgreSQL 迁移策略 | 2026-05-07 | ✅ 已采纳 |
| ADR-002 | 缓存策略：进程内 + SQLite | 2026-05-07 | ✅ 已采纳 |

## 模块依赖图

```
Module 0 (用户) ←── Module 1 (数据) ←── Module 2 (新闻)
                          ↑
                    Module 3 (市场) ←── Module 4 (估值)
```

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.1.0 | 2026-05-13 | 合并 strategy_compass/designs/ 下的 UI 设计资源 |
| v1.0.0 | 2026-05-13 | 初始版本，从 docs/modules/ 迁移重组 |
