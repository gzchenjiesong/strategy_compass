---
title: "Module 4: 估值分析 — 接口与业务逻辑设计"
type: spec
module: module-4
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---


# Module 4: 估值分析

> 前置文档：
> - [`docs/archive/modules-20260513/module-1-data-source-analysis.md`](../../archive/modules-20260513/module-1-data-source-analysis.md)（数据源选型）
> - [`docs/designs/module-1-data/README.md`](../module-1-data/README.md)（数据底座接口+数据模型）
>
> 本文档聚焦：Module 4 的接口定义 + 核心计算逻辑 + 与上下游的契约。
>
> **核心定位：** Module 4 是分析层的估值计算引擎，从 Module 1 获取原始数据，计算估值百分位、风险指标等，为 Module 3/5/6 提供统一的估值分析能力。

## 1. 职责边界

**做：**
- 估值百分位计算（PE/PB/PS/股息率/融资余额/杠杆率的历史百分位）
- 风险指标计算（最大回撤、当前回撤、年化波动率、夏普比率、卡玛比率、Beta）
- 价格偏离度计算（当前价格/指数点位在历史中的百分位）
- 热度指标计算（成交额变化率、板块涨跌家数比）
- 估值区间标签（低估/适中/高估）
- 提供标准化估值分析 API 供下游模块消费

**不做：**
- 数据获取（归 Module 1）
- 数据展示（归 Module 3/5/6）
- 新闻情绪分析（归 Module 2）
- 用户偏好管理（归 Module 0）

**核心约束：** 估值能力统一出口 — 所有估值计算通过 Module 4 提供，其他模块不重复实现。


## 子文档

| 文档 | 说明 |
|------|------|
| [api.md](api.md) | 估值分析接口 |
| [data-model.md](data-model.md) | 估值数据表结构 |
| [flow.md](flow.md) | 估值计算流程 |

## 5. 与上下游模块的接口契约

### 5.1 依赖的上游模块

| 上游模块 | 依赖内容 | 调用方式 | 用途 |
|---------|---------|---------|------|
| Module 0 用户系统 | `@auth_required` 认证 | 装饰器 | 所有接口鉴权 |
| Module 1 数据底座 | GET /api/v1/data/klines/* | 内部 HTTP 调用 | 历史 K 线（计算风险指标） |
| Module 1 数据底座 | GET /api/v1/data/valuations/* | 内部 HTTP 调用 | 估值原始数据（PE/PB/PS） |
| Module 1 数据底座 | GET /api/v1/data/margin/summary | 内部 HTTP 调用 | 融资融券数据 |
| Module 1 数据底座 | GET /api/v1/data/flows/* | 内部 HTTP 调用 | 资金流向数据 |
| Module 1 数据底座 | GET /api/v1/data/quotes/* | 内部 HTTP 调用 | 实时行情（涨跌家数） |

### 5.2 对下游暴露的能力

| 消费者模块 | 调用的 API | 用途 |
|-----------|-----------|------|
| Module 3 市场概览 | GET /api/v4/valuation/indices | 首页指数估值概览 |
| Module 3 市场概览 | GET /api/v4/valuation/market | 市场杠杆率等宏观指标 |
| Module 3 市场概览 | GET /api/v4/valuation/zone-summary?type=index | 指数估值区间分布 |
| Module 5 板块概念 | GET /api/v4/valuation/board/:code | 板块估值分析 |
| Module 5 板块概念 | GET /api/v4/valuation/boards | 板块估值排行 |
| Module 6 个股详情 | GET /api/v4/valuation/stock/:symbol | 个股估值分析 |
| Module 6 个股详情 | GET /api/v4/valuation/etf/:symbol | ETF 估值分析 |
| Module 6 个股详情 | GET /api/v4/valuation/history/stock/:symbol | 个股历史估值曲线 |


## 6. 错误处理

### 统一错误响应格式

```json
{
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "历史数据不足 1 年，无法计算百分位"
  }
}
```

### Module 4 错误码清单

| HTTP 状态码 | 错误码 | 说明 |
|-------------|--------|------|
| 401 | UNAUTHORIZED | 未提供 Token |
| 404 | SYMBOL_NOT_FOUND | 标的代码不存在 |
| 404 | DATA_NOT_FOUND | 该标的无估值数据 |
| 409 | DATA_NOT_READY | 该标的数据正在初始化中 |
| 422 | INSUFFICIENT_DATA | 历史数据不足，无法计算百分位 |
| 400 | INVALID_WINDOW | 百分位窗口参数无效（仅支持 3/5/10/20） |
| 500 | CALC_FAILED | 计算过程异常 |


## 7. 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| VALUATION_ZONE_LOW | 否 | 低估区间上限百分位，默认 30 |
| VALUATION_ZONE_HIGH | 否 | 高估区间下限百分位，默认 70 |
| RISK_FREE_RATE | 否 | 无风险利率（年化），默认 0.02 |
| PERCENTILE_CACHE_TTL | 否 | 百分位缓存 TTL（秒），默认 3600 |


## 8. 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 分标的类型指标体系 | 大盘指数/板块/个股/ETF/市场整体各用不同指标组合 | 不同标的关注点不同，统一指标无意义 |
| 大盘指数重点看价格百分位+PE/PB百分位 | 指数盈利稳定，百分位是判断估值水位的黄金指标 | |
| 板块重点看PE/PB百分位+板块热度 | 板块轮动时估值+热度双维度判断 | |
| 个股重点看回撤指标 | 个股波动大，回撤风险评估比指数更重要 | |
| 市场整体只看杠杆率 | 全市场级别的指标不宜过多，杠杆率最能反映资金水位 | |
| 百分位窗口默认 10 年 | 10 年覆盖一个完整牛熊周期，数据充足 | 支持 3/5/10/20 年灵活调整 |
| 百分位阈值 30%/70% | 行业惯例，非严格科学结论 | 可通过配置文件调整 |
| PE < 0 或 > 1000 排除 | 亏损或异常值不应参与百分位计算 | 避免误导 |
| 风险指标用内存计算 | 基于日 K 线计算，数据量可控 | 无需额外存储计算结果 |
| 估值百分位结果可缓存 | 百分位每日只变化一次 | TTL 1 小时，减少重复计算 |
| ETF 估值通过关联指数实现 | ETF 本身无 PE/PB，需映射到跟踪指数 | 建立 ETF→指数映射表 |
| Module 4 接口为内部调用 | Module 4 不直接暴露给前端 | 前端通过 Module 3/5/6 间接访问 |

