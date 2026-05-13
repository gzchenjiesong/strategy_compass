---
title: "Module 3: 市场概览 — 接口与业务逻辑设计"
type: spec
module: module-3
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---


# Module 3: 市场概览

> 前置文档：
> - [`docs/designs/module-1-data/README.md`](../../module-1-data/README.md)（数据底座接口）
> - [`docs/designs/module-4-valuation/README.md`](../../module-4-valuation/README.md)（估值分析接口）
> - [`docs/designs/module-2-news/README.md`](../../module-2-news/README.md)（新闻聚合接口）
>
> 本文档聚焦：Module 3 的接口定义 + 数据聚合逻辑 + 与上下游的契约。
>
> **核心定位：** Module 3 是应用层的首页仪表盘模块，聚合 Module 1（原始数据）和 Module 4（估值分析）的数据，组装成前端卡片所需的格式，为用户提供"一眼看清市场"的能力。

## 1. 职责边界

**做：**
- 首页数据聚合（概览/大盘/板块三个视图）
- 卡片数据组装（将分散的数据组装为前端卡片格式）
- 弹窗详情数据提供（指数详情、板块详情）
- 数据缓存（减少重复查询和计算）

**不做：**
- 原始数据获取（归 Module 1）
- 估值百分位计算（归 Module 4）
- 新闻加工（归 Module 2）
- 用户数据管理（归 Module 0）

**核心约束：** 首页数据统一聚合出口 — 前端所有首页相关数据通过 Module 3 获取，不直接调用 Module 1/4。


## 子文档

| 文档 | 说明 |
|------|------|
| [api.md](api.md) | 市场数据接口 |
| [data-model.md](data-model.md) | 市场数据表结构 |
| [flow.md](flow.md) | 数据聚合流程 |

## 5. 与上下游模块的接口契约

### 5.1 依赖的上游模块

| 上游模块 | 依赖内容 | 调用方式 | 用途 |
|---------|---------|---------|------|
| Module 0 用户系统 | `@auth_required` 认证 | 装饰器 | 接口鉴权 |
| Module 0 用户系统 | 用户关注板块列表 | 内部调用 | 板块页过滤 |
| Module 1 数据底座 | 实时行情数据 | 内部调用 | 卡片涨跌幅 |
| Module 2 新闻聚合 | 重要快讯 | 内部 HTTP | 概览页快讯 |
| Module 4 估值分析 | 指数/板块估值 | 内部 HTTP | 核心数据 |

### 5.2 对下游暴露的能力

| 消费者 | 调用的 API | 用途 |
|--------|-----------|------|
| 前端市场页面 | GET /api/v3/market/overview | 概览页展示 |
| 前端市场页面 | GET /api/v3/market/indices | 大盘页展示 |
| 前端市场页面 | GET /api/v3/market/boards | 板块页展示 |
| 前端市场页面 | GET /api/v3/market/index/:symbol/detail | 指数详情弹窗 |
| 前端市场页面 | GET /api/v3/market/board/:code/detail | 板块详情弹窗 |

---


## 6. 错误处理

### 统一错误响应格式

```json
{
  "error": {
    "code": "SYMBOL_NOT_FOUND",
    "message": "标的代码不存在"
  }
}
```

### Module 3 错误码清单

| HTTP 状态码 | 错误码 | 说明 |
|-------------|--------|------|
| 401 | UNAUTHORIZED | 未提供 Token |
| 404 | SYMBOL_NOT_FOUND | 指数/板块代码不存在 |
| 404 | DATA_NOT_READY | 该标的数据正在初始化中 |
| 500 | AGGREGATION_FAILED | 数据聚合失败（下游模块异常） |

---


## 8. 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| Module 3 直接暴露给前端 | 前端不直接调用 Module 1/4 | 统一聚合入口，减少前端复杂度 |
| 三个标签页三个独立接口 | 非一个接口返回全部 | 按需加载，减少不必要的数据传输 |
| 卡片只展示精简数据 | 弹窗才展示完整指标 | 列表页性能优先，详情页体验优先 |
| 弹窗用浮层非路由跳转 | 保持页面上下文 | 高频操作（点卡片看详情），浮层体验更好 |
| 市场情绪综合判断 | 杠杆率 + 北向资金 | 两个互补指标，单一指标容易失真 |
| 缓存 5 分钟 | 首页概览数据 | 行情秒级变化，但估值每日变化，5 分钟平衡实时性和性能 |
| 板块页只显示用户关注 | 非全量板块 | 用户关注才有意义，减少信息噪音 |

---


