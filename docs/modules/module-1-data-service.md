---
title: "Module 1: 数据底座 — 接口与数据模型设计"
type: spec
module: module-1
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

# Module 1: 数据底座

> 前置文档：`docs/modules/module-1-data-source-analysis.md`（数据源选型、缓存、去重、排序策略）
> 本文档聚焦：接口定义 + 数据表结构 + 核心业务逻辑。

## 1. 职责边界

**做：**
- 统一获取所有外部金融数据（行情/估值/财务/板块/基金/新闻）
- SQLite 持久化缓存 + 进程内内存缓存
- 数据清洗、去重、标准化
- 提供标准化数据 API 供下游模块消费
- 系统首次部署时初始化 10 个核心指数 20 年日 K
- 用户添加自选/关注后按需触发历史数据拉取

**不做：**
- 估值百分位计算（归 Module 4）
- 新闻加工处理（归 Module 2）
- 用户数据管理（归 Module 0）
- 直接对外展示（归 Module 3/5/6）

**核心约束：** 数据获取唯一入口 — 其他模块不直接调用外部 API。

## 2. API 接口定义

> 所有接口需通过 `@auth_required` 认证（依赖 Module 0）。
> 响应中的时间字段统一使用 ISO 8601 格式（UTC）。
> 价格/金额字段保留 2 位小数，百分比字段保留 2 位小数。

### 2.1 实时行情（Quotes）

#### GET /api/v1/data/quotes/stock/:symbol

获取单只股票/ETF 的实时行情。

**路径参数：**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| symbol | string | 股票代码（不含市场前缀） | `600519` |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| market | string | 否 | 市场：`A`（默认）/ `HK` |

**响应：**

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "market": "A",
  "price": 1856.00,
  "change": 23.50,
  "change_pct": 1.28,
  "open": 1840.00,
  "high": 1862.00,
  "low": 1835.00,
  "prev_close": 1832.50,
  "volume": 3256800,
  "turnover": 6042350000.00,
  "pe_ttm": 33.25,
  "pb": 10.12,
  "market_cap": 2331500000000.00,
  "updated_at": "2026-05-07T07:30:00Z"
}
```

**错误码：**

| code | 说明 |
|------|------|
| `SYMBOL_NOT_FOUND` | 标的代码不存在 |
| `DATA_NOT_READY` | 该标的数据尚未初始化完成 |

#### GET /api/v1/data/quotes/index/:symbol

获取单个指数的实时行情。

**路径参数：**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| symbol | string | 指数代码 | `000300` / `HSI` / `.INX` |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| market | string | 否 | `A`（默认）/ `GIDX` |

**响应：**

```json
{
  "symbol": "000300",
  "name": "沪深300",
  "market": "A",
  "price": 3985.42,
  "change": 42.18,
  "change_pct": 1.07,
  "open": 3950.00,
  "high": 3992.00,
  "low": 3945.00,
  "prev_close": 3943.24,
  "volume": 185230000000,
  "turnover": 2345600000000.00,
  "updated_at": "2026-05-07T07:30:00Z"
}
```

#### GET /api/v1/data/quotes/indices

批量获取指数实时行情（首页概览用）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| symbols | string | 否 | 逗号分隔的指数代码，不传则返回全部核心指数 |

**响应：**

```json
{
  "items": [
    {
      "symbol": "000001",
      "name": "上证指数",
      "market": "A",
      "price": 3356.78,
      "change": 15.23,
      "change_pct": 0.46,
      "updated_at": "2026-05-07T07:30:00Z"
    }
  ]
}
```

#### GET /api/v1/data/quotes/board/:code

获取单个板块的实时行情。

**路径参数：**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| code | string | 板块代码 | `BK0477` |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `industry`（默认）/ `concept` |

**响应：**

```json
{
  "code": "BK0477",
  "name": "半导体",
  "type": "industry",
  "change_pct": 2.35,
  "turnover": 85600000000.00,
  "lead_stock": "北方华创",
  "lead_change_pct": 5.12,
  "rise_count": 85,
  "fall_count": 12,
  "updated_at": "2026-05-07T07:30:00Z"
}
```

#### GET /api/v1/data/quotes/boards

获取板块实时排行。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `industry`（默认）/ `concept` |
| sort | string | 否 | `change_pct`（默认）/ `turnover` |
| order | string | 否 | `desc`（默认）/ `asc` |
| limit | integer | 否 | 返回数量，默认 20，最大 50 |

**响应：**

```json
{
  "items": [
    {
      "code": "BK0477",
      "name": "半导体",
      "change_pct": 2.35,
      "turnover": 85600000000.00,
      "lead_stock": "北方华创",
      "lead_change_pct": 5.12
    }
  ]
}
```

---

### 2.2 历史 K 线（K-Lines）

#### GET /api/v1/data/klines/stock/:symbol

获取个股/ETF 历史日 K 线。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| symbol | string | 股票/ETF 代码 |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| market | string | 否 | `A`（默认）/ `HK` |
| period | string | 否 | `daily`（默认）/ `weekly` / `monthly` |
| start_date | string | 否 | 起始日期 `YYYY-MM-DD`，不传从最早可用数据开始 |
| end_date | string | 否 | 结束日期，不传到最新 |
| limit | integer | 否 | 最大返回条数，默认 250，最大 5000 |

**响应：**

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "market": "A",
  "period": "daily",
  "items": [
    {
      "date": "2026-05-07",
      "open": 1840.00,
      "high": 1862.00,
      "low": 1835.00,
      "close": 1856.00,
      "volume": 3256800,
      "turnover": 6042350000.00,
      "change_pct": 1.28
    }
  ]
}
```

> **周 K/月 K 说明：** Module 1 存储日 K，`period=weekly/monthly` 时由 Service 层在查询结果上聚合生成，不单独存储。

#### GET /api/v1/data/klines/index/:symbol

获取指数历史日 K 线。

**查询参数：** 同 stock klines，额外支持：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| market | string | 否 | `A`（默认）/ `GIDX` |

**响应：** 同 stock klines 格式（无 name 字段时用 symbol 代替）。

#### GET /api/v1/data/klines/board/:code

获取板块历史日 K 线。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `industry`（默认）/ `concept` |
| start_date | string | 否 | 起始日期 |
| end_date | string | 否 | 结束日期 |
| limit | integer | 否 | 最大返回条数，默认 250 |

**响应：**

```json
{
  "code": "BK0477",
  "name": "半导体",
  "type": "industry",
  "period": "daily",
  "items": [
    {
      "date": "2026-05-07",
      "open": 5623.45,
      "high": 5698.12,
      "low": 5601.00,
      "close": 5685.30,
      "volume": 12568000000,
      "turnover": 85600000000.00,
      "change_pct": 1.25
    }
  ]
}
```

---

### 2.3 估值数据（Valuations）

#### GET /api/v1/data/valuations/stock/:symbol

获取个股/ETF 估值指标。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| market | string | 否 | `A`（默认）/ `HK` |
| start_date | string | 否 | 起始日期 |
| end_date | string | 否 | 结束日期 |
| limit | integer | 否 | 最大返回条数，默认 30 |

**响应：**

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "items": [
    {
      "date": "2026-05-07",
      "pe_ttm": 33.25,
      "pb": 10.12,
      "ps_ttm": 18.56,
      "dividend_yield": 1.85,
      "market_cap": 2331500000000.00,
      "total_market_cap": 2331500000000.00
    }
  ]
}
```

#### GET /api/v1/data/valuations/index/:symbol

获取指数估值数据。

**响应：**

```json
{
  "symbol": "000300",
  "name": "沪深300",
  "items": [
    {
      "date": "2026-05-07",
      "pe_ttm": 12.85,
      "pb": 1.42,
      "dividend_yield": 2.65
    }
  ]
}
```

#### GET /api/v1/data/valuations/board/:code

获取板块（申万行业）估值数据。

**响应：**

```json
{
  "code": "BK0477",
  "name": "半导体",
  "items": [
    {
      "date": "2026-05-07",
      "pe_static": 45.23,
      "pe_ttm": 42.18,
      "pb": 3.85
    }
  ]
}
```

---

### 2.4 财务数据（Financials）

#### GET /api/v1/data/financials/:symbol

获取个股财务摘要。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| report_type | string | 否 | `summary`（默认）/ `income` / `balance` / `cashflow` |
| limit | integer | 否 | 最近 N 期，默认 4（即最近 1 年） |

**响应（summary）：**

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "items": [
    {
      "report_date": "2025-12-31",
      "report_type": "annual",
      "revenue": 175000000000.00,
      "net_profit": 86500000000.00,
      "roe": 33.50,
      "gross_margin": 91.20,
      "eps": 68.85,
      "bvps": 205.60,
      "updated_at": "2026-04-20T00:00:00Z"
    }
  ]
}
```

---

### 2.5 板块数据（Boards）

#### GET /api/v1/data/boards

获取板块列表（用于板块搜索/选择）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `industry`（默认）/ `concept` |
| keyword | string | 否 | 搜索关键词（模糊匹配板块名称） |
| limit | integer | 否 | 默认 50，最大 200 |

**响应：**

```json
{
  "items": [
    {
      "code": "BK0477",
      "name": "半导体",
      "type": "industry",
      "stock_count": 97,
      "change_pct": 2.35,
      "updated_at": "2026-05-07T00:00:00Z"
    }
  ]
}
```

#### GET /api/v1/data/boards/:code/constituents

获取板块成分股列表。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | string | 板块代码 |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `industry`（默认）/ `concept` |
| sort | string | 否 | `market_cap`（默认）/ `change_pct` |
| order | string | 否 | `desc`（默认）/ `asc` |

**响应：**

```json
{
  "board_code": "BK0477",
  "board_name": "半导体",
  "items": [
    {
      "symbol": "002371",
      "name": "北方华创",
      "market": "A",
      "market_cap": 285000000000.00,
      "change_pct": 5.12,
      "weight": 8.56
    }
  ]
}
```

#### GET /api/v1/data/boards/indices/:symbol/constituents

获取指数成分股列表。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| symbol | string | 指数代码 |

**响应：**

```json
{
  "index_symbol": "000300",
  "index_name": "沪深300",
  "items": [
    {
      "symbol": "600519",
      "name": "贵州茅台",
      "market": "A",
      "weight": 5.82,
      "market_cap": 2331500000000.00
    }
  ]
}
```

---

### 2.6 资金流向（Flows）

#### GET /api/v1/data/flows/northbound

获取北向资金流向数据。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| days | integer | 否 | 最近 N 天，默认 30 |

**响应：**

```json
{
  "items": [
    {
      "date": "2026-05-07",
      "net_buy": 8560000000.00,
      "buy_amount": 65200000000.00,
      "sell_amount": 56640000000.00
    }
  ]
}
```

#### GET /api/v1/data/flows/board/:code

获取板块资金流向。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `industry`（默认）/ `concept` |
| days | integer | 否 | 最近 N 天，默认 5 |

**响应：**

```json
{
  "board_code": "BK0477",
  "board_name": "半导体",
  "items": [
    {
      "date": "2026-05-07",
      "net_inflow": 3250000000.00,
      "main_inflow": 2180000000.00,
      "retail_inflow": 1070000000.00
    }
  ]
}
```

---

### 2.7 基金数据（Funds）

#### GET /api/v1/data/funds/:symbol

获取基金净值数据。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| symbol | string | 基金代码 |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | integer | 否 | 最近 N 天，默认 30 |

**响应：**

```json
{
  "symbol": "510300",
  "name": "华泰柏瑞沪深300ETF",
  "type": "etf",
  "items": [
    {
      "date": "2026-05-07",
      "nav": 4.235,
      "acc_nav": 4.235,
      "change_pct": 1.05
    }
  ]
}
```

---

### 2.8 融资融券（Margin）

#### GET /api/v1/data/margin/summary

获取沪深融资融券历史汇总数据（含百分位计算所需的原始序列）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| days | integer | 否 | 最近 N 个交易日，默认 30 |
| include_percentile | boolean | 否 | 是否在响应中附带当前值在近 N 年的百分位，默认 false |
| window_years | integer | 否 | 百分位计算窗口，默认 10 年 |

**响应（include_percentile=false）：**

```json
{
  "market": "A",
  "items": [
    {
      "date": "2026-05-07",
      "financing_balance": 1852300000000.00,
      "securities_balance": 65320000000.00,
      "financing_buy_amount": 86500000000.00,
      "financing_balance_change": 3520000000.00,
      "total_market_cap": 92350000000000.00,
      "leverage_ratio": 2.01
    }
  ]
}
```

**响应（include_percentile=true）额外字段：**

```json
{
  "latest": {
    "date": "2026-05-07",
    "financing_balance": 1852300000000.00,
    "financing_balance_percentile": 68.5,
    "leverage_ratio": 2.01,
    "leverage_ratio_percentile": 72.3
  }
}
```

**业务说明：**
- `financing_balance`：沪深合计融资余额（单位：元）
- `securities_balance`：沪深合计融券余额（单位：元）
- `financing_buy_amount`：当日融资买入额（单位：元）
- `total_market_cap`：当日 A 股总市值（单位：元），取自 `index_valuation.total_market_cap`（上证指数总市值近似）
- `leverage_ratio`：杠杆率 = `financing_balance / total_market_cap × 100%`
- 百分位基于历史全序列计算，默认窗口 10 年

---

### 2.9 新闻数据（News）

#### GET /api/v1/data/news

获取新闻列表（原始数据，供 Module 2 加工）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| since | string | 否 | 起始时间 ISO 8601，不传返回最近新闻 |
| limit | integer | 否 | 默认 50，最大 200 |
| important_only | boolean | 否 | 只返回重要快讯，默认 false |

**响应：**

```json
{
  "items": [
    {
      "id": 12345,
      "source": "jin10",
      "source_id": "j10_20260507_001",
      "title": "美联储主席发表讲话",
      "content": "美联储主席鲍威尔表示...",
      "important": true,
      "tags": ["美联储", "利率"],
      "publish_time": "2026-05-07T08:30:00Z"
    }
  ]
}
```

---

### 2.10 数据任务管理（Data Tasks）

> 以下接口用于管理数据同步任务，供系统内部和管理员使用。

#### POST /api/v1/data/tasks/init-symbol

触发按需标的数据初始化（用户添加自选后调用）。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| symbol | string | 是 | 标的代码 |
| market | string | 是 | 市场类型：`A` / `HK` |
| type | string | 是 | 标的类型：`stock` / `etf` / `fund` |
| depth_years | integer | 否 | 拉取深度（年），默认 10 |

**响应：**

```json
{
  "task_id": "task_20260507_001",
  "symbol": "600519",
  "status": "queued",
  "estimated_seconds": 120
}
```

#### POST /api/v1/data/tasks/init-board

触发板块数据初始化（用户添加板块关注后调用）。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 板块代码 |
| type | string | 是 | `industry` / `concept` |
| depth_years | integer | 否 | 拉取深度（年），默认 15 |

**响应：** 同 init-symbol。

#### GET /api/v1/data/tasks/:task_id

查询数据任务状态。

**响应：**

```json
{
  "task_id": "task_20260507_001",
  "status": "running",
  "progress": 65,
  "total_records": 2500,
  "loaded_records": 1625,
  "started_at": "2026-05-07T08:00:00Z",
  "estimated_finish_at": "2026-05-07T08:02:00Z"
}
```

**任务状态：** `queued` → `running` → `completed` / `failed`

#### GET /api/v1/data/sync-status

获取系统数据同步状态概览（管理用）。

**响应：**

```json
{
  "core_indices": {
    "total": 10,
    "synced": 10,
    "last_sync": "2026-05-07T08:30:00Z"
  },
  "user_symbols": {
    "total": 45,
    "synced": 43,
    "pending": 2
  },
  "user_boards": {
    "total": 8,
    "synced": 8,
    "last_sync": "2026-05-07T08:30:00Z"
  },
  "news": {
    "total_count": 1256,
    "latest_time": "2026-05-07T08:25:00Z"
  }
}
```

## 3. 数据模型

### 3.1 ER 图

```
┌──────────────────────┐
│ stock_daily_kline    │  个股/ETF/港股日K
│──────────────────────│
│ id (PK)              │
│ symbol               │
│ market               │
│ date                 │
│ open / high / low    │
│ close / volume       │
│ turnover / change_pct│
└──────────────────────┘

┌──────────────────────┐
│ index_daily_kline    │  指数日K
│──────────────────────│
│ id (PK)              │
│ symbol               │
│ market               │
│ date                 │
│ open / high / low    │
│ close / volume       │
│ turnover / change_pct│
└──────────────────────┘

┌──────────────────────┐
│ board_daily_kline    │  板块日K
│──────────────────────│
│ id (PK)              │
│ board_code           │
│ board_type           │
│ date                 │
│ open / high / low    │
│ close / volume       │
│ turnover / change_pct│
└──────────────────────┘

┌──────────────────────┐
│ stock_valuation      │  个股估值指标
│──────────────────────│
│ id (PK)              │
│ symbol / market      │
│ date                 │
│ pe_ttm / pb / ps_ttm │
│ dividend_yield       │
│ market_cap / ...     │
└──────────────────────┘

┌────────────────────────┐
│ index_valuation        │  指数估值
│────────────────────────│
│ id (PK)                │
│ symbol                 │
│ date                   │
│ pe_ttm / pb            │
│ dividend_yield         │
│ total_market_cap       │  ← 新增：指数覆盖总市值
└────────────────────────┘

┌──────────────────────┐
│ board_valuation      │  板块估值
│──────────────────────│
│ id (PK)              │
│ board_code           │
│ date                 │
│ pe_static / pe_ttm   │
│ pb                   │
└──────────────────────┘

┌──────────────────────┐
│ financial_report     │  财务报表
│──────────────────────│
│ id (PK)              │
│ symbol / market      │
│ report_date          │
│ report_type          │
│ revenue / net_profit │
│ roe / eps / ...      │
└──────────────────────┘

┌──────────────────────┐
│ board_info           │  板块信息
│──────────────────────│
│ id (PK)              │
│ code (UNIQUE)        │
│ name / type          │
│ stock_count          │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│ board_constituent    │  板块成分股
│──────────────────────│
│ id (PK)              │
│ board_code (FK)      │
│ symbol               │
│ name / market        │
│ weight               │
└──────────────────────┘

┌──────────────────────┐
│ fund_nav             │  基金净值
│──────────────────────│
│ id (PK)              │
│ fund_code            │
│ nav_date             │
│ nav / acc_nav        │
│ change_pct           │
└──────────────────────┘

┌──────────────────────┐
│ money_flow           │  资金流向
│──────────────────────│
│ id (PK)              │
│ flow_type            │
│ entity_code          │
│ date                 │
│ net_inflow / ...     │
└──────────────────────┘

┌──────────────────────┐
│ news_raw             │  新闻原始数据
│──────────────────────│
│ id (PK)              │
│ source / source_id   │
│ title / content      │
│ important / tags     │
│ publish_time         │
└──────────────────────┘

┌──────────────────────────┐
│ margin_daily             │  融资融券汇总（沪深合计）
│──────────────────────────│
│ id (PK)                  │
│ date (UNIQUE)            │
│ financing_balance        │  合计融资余额
│ securities_balance       │  合计融券余额
│ financing_buy_amount     │  当日融资买入额
│ financing_balance_change │  融资余额日变动
│ total_market_cap         │  当日A股总市值
│ leverage_ratio           │  杠杆率%
└──────────────────────────┘

┌──────────────────────┐
│ data_sync_log        │  数据同步日志
│──────────────────────│
│ id (PK)              │
│ task_id              │
│ task_type            │
│ target               │
│ status / progress    │
│ started_at / ...     │
└──────────────────────┘
```

### 3.2 表结构

#### stock_daily_kline — 个股/ETF/港股日 K 线表

```sql
CREATE TABLE stock_daily_kline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol      TEXT    NOT NULL,
    market      TEXT    NOT NULL,   -- A | HK
    date        TEXT    NOT NULL,   -- YYYY-MM-DD
    open        REAL    NOT NULL,
    high        REAL    NOT NULL,
    low         REAL    NOT NULL,
    close       REAL    NOT NULL,
    volume      INTEGER NOT NULL DEFAULT 0,
    turnover    REAL    NOT NULL DEFAULT 0,
    change_pct  REAL,               -- 涨跌幅 %

    CHECK (market IN ('A', 'HK')),
    UNIQUE (symbol, market, date)
);

CREATE INDEX idx_stock_kline_symbol ON stock_daily_kline(symbol, market);
CREATE INDEX idx_stock_kline_date   ON stock_daily_kline(date);
```

**业务规则：**
- 覆盖 A 股个股、港股个股、场内 ETF（ETF 使用 A 股代码体系）
- 历史深度：个股/ETF 最长 10 年
- 去重：`(symbol, market, date)` 唯一，INSERT OR IGNORE
- 排序：默认 `date ASC`

#### index_daily_kline — 指数日 K 线表

```sql
CREATE TABLE index_daily_kline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol      TEXT    NOT NULL,
    market      TEXT    NOT NULL,   -- A | GIDX
    date        TEXT    NOT NULL,
    open        REAL    NOT NULL,
    high        REAL    NOT NULL,
    low         REAL    NOT NULL,
    close       REAL    NOT NULL,
    volume      INTEGER NOT NULL DEFAULT 0,
    turnover    REAL    NOT NULL DEFAULT 0,
    change_pct  REAL,

    CHECK (market IN ('A', 'GIDX')),
    UNIQUE (symbol, market, date)
);

CREATE INDEX idx_index_kline_symbol ON index_daily_kline(symbol, market);
CREATE INDEX idx_index_kline_date   ON index_daily_kline(date);
```

**业务规则：**
- 覆盖 A 股指数（上证/沪深300/A500/中证2000/科创50/创业板指）和全球指数（恒生/恒生科技/标普/纳指）
- 历史深度：20 年
- 首次部署自动拉取 10 个核心指数

#### board_daily_kline — 板块日 K 线表

```sql
CREATE TABLE board_daily_kline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    board_code  TEXT    NOT NULL,
    board_type  TEXT    NOT NULL,   -- industry | concept
    date        TEXT    NOT NULL,
    open        REAL    NOT NULL,
    high        REAL    NOT NULL,
    low         REAL    NOT NULL,
    close       REAL    NOT NULL,
    volume      INTEGER NOT NULL DEFAULT 0,
    turnover    REAL    NOT NULL DEFAULT 0,
    change_pct  REAL,

    CHECK (board_type IN ('industry', 'concept')),
    UNIQUE (board_code, date)
);

CREATE INDEX idx_board_kline_code ON board_daily_kline(board_code);
CREATE INDEX idx_board_kline_date ON board_daily_kline(date);
```

**业务规则：**
- 覆盖行业板块和概念板块
- 历史深度：15 年
- 按需触发：用户添加板块关注后拉取

#### stock_valuation — 个股估值指标表

```sql
CREATE TABLE stock_valuation (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol          TEXT    NOT NULL,
    market          TEXT    NOT NULL,
    date            TEXT    NOT NULL,
    pe_ttm          REAL,       -- 滚动市盈率
    pb              REAL,       -- 市净率
    ps_ttm          REAL,       -- 滚动市销率
    dividend_yield  REAL,       -- 股息率 %
    market_cap      REAL,       -- 流通市值
    total_market_cap REAL,      -- 总市值

    CHECK (market IN ('A', 'HK')),
    UNIQUE (symbol, market, date)
);

CREATE INDEX idx_stock_val_symbol ON stock_valuation(symbol, market);
CREATE INDEX idx_stock_val_date   ON stock_valuation(date);
```

**业务规则：**
- 覆盖 A 股个股、港股个股、场内 ETF
- 更新频率：每日收盘后
- 去重：`(symbol, market, date)` 唯一，INSERT OR REPLACE（当日可能修正）

#### index_valuation — 指数估值表

```sql
CREATE TABLE index_valuation (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol          TEXT    NOT NULL,
    date            TEXT    NOT NULL,
    pe_ttm          REAL,
    pb              REAL,
    dividend_yield  REAL,
    total_market_cap REAL,      -- 当日指数覆盖范围总市值（用于融资/市值比计算）

    UNIQUE (symbol, date)
);

CREATE INDEX idx_index_val_symbol ON index_valuation(symbol);
CREATE INDEX idx_index_val_date   ON index_valuation(date);
```

**业务规则：**
- 覆盖 A 股主要指数和全球指数（有估值数据的）
- 数据源：国证指数 `index_all_cni()` + 自行计算历史序列
- `total_market_cap`：上证指数（000001）覆盖的总市值，作为 A 股总市值的近似值
- 更新频率：每日收盘后

#### board_valuation — 板块估值表

```sql
CREATE TABLE board_valuation (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    board_code      TEXT    NOT NULL,
    date            TEXT    NOT NULL,
    pe_static       REAL,       -- 静态市盈率
    pe_ttm          REAL,       -- 滚动市盈率
    pb              REAL,       -- 市净率

    UNIQUE (board_code, date)
);

CREATE INDEX idx_board_val_code ON board_valuation(board_code);
CREATE INDEX idx_board_val_date ON board_valuation(date);
```

**业务规则：**
- 数据源：申万宏源 `sw_index_first_info()`
- 覆盖行业板块和概念板块（有估值数据的）
- 更新频率：每日收盘后
- 去重：`(board_code, date)` 唯一，INSERT OR REPLACE

#### financial_report — 财务报表表

```sql
CREATE TABLE financial_report (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol          TEXT    NOT NULL,
    market          TEXT    NOT NULL,
    report_date     TEXT    NOT NULL,   -- 报告期 YYYY-MM-DD
    report_type     TEXT    NOT NULL,   -- annual | semi_annual | quarterly
    revenue         REAL,               -- 营业收入
    net_profit      REAL,               -- 归母净利润
    roe             REAL,               -- 净资产收益率 %
    gross_margin    REAL,               -- 毛利率 %
    eps             REAL,               -- 每股收益
    bvps            REAL,               -- 每股净资产
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (market IN ('A', 'HK')),
    UNIQUE (symbol, market, report_date, report_type)
);

CREATE INDEX idx_fin_symbol ON financial_report(symbol, market);
CREATE INDEX idx_fin_date   ON financial_report(report_date);
```

**业务规则：**
- 更新频率：每周检查一次，季报期可缩短到每日
- 去重：`(symbol, market, report_date, report_type)` 唯一，INSERT OR REPLACE

#### board_info — 板块信息表

```sql
CREATE TABLE board_info (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT    NOT NULL UNIQUE,
    name        TEXT    NOT NULL,
    type        TEXT    NOT NULL,       -- industry | concept
    stock_count INTEGER NOT NULL DEFAULT 0,
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (type IN ('industry', 'concept'))
);

CREATE INDEX idx_board_info_type ON board_info(type);
CREATE INDEX idx_board_info_name ON board_info(name);
```

**业务规则：**
- 全量刷新：每日 18:00
- 支持按名称模糊搜索

#### board_constituent — 板块成分股表

```sql
CREATE TABLE board_constituent (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    board_code  TEXT    NOT NULL,
    symbol      TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    market      TEXT    NOT NULL DEFAULT 'A',
    weight      REAL,               -- 权重 %（如有）
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),

    UNIQUE (board_code, symbol)
);

CREATE INDEX idx_board_const_code   ON board_constituent(board_code);
CREATE INDEX idx_board_const_symbol ON board_constituent(symbol);
```

**业务规则：**
- 覆盖行业板块和概念板块的成分股
- 同时包含指数成分股（通过 `board_code` 前缀区分：`IDX:000300`）
- 更新频率：板块成分股每日 18:00，指数成分股按季度

#### fund_nav — 基金净值表

```sql
CREATE TABLE fund_nav (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code   TEXT    NOT NULL,
    name        TEXT    NOT NULL DEFAULT '',
    nav_date    TEXT    NOT NULL,       -- 净值日期
    nav         REAL    NOT NULL,       -- 单位净值
    acc_nav     REAL,                   -- 累计净值
    change_pct  REAL,                   -- 日涨跌幅 %

    UNIQUE (fund_code, nav_date)
);

CREATE INDEX idx_fund_nav_code ON fund_nav(fund_code);
CREATE INDEX idx_fund_nav_date ON fund_nav(nav_date);
```

**业务规则：**
- 覆盖场内 ETF 和场外基金
- 更新频率：每日晚间
- 去重：`(fund_code, nav_date)` 唯一，INSERT OR IGNORE

#### money_flow — 资金流向表

```sql
CREATE TABLE money_flow (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_type   TEXT    NOT NULL,   -- northbound | industry | concept
    entity_code TEXT    NOT NULL DEFAULT '',  -- 板块代码，northbound 时为空
    date        TEXT    NOT NULL,
    net_inflow  REAL,               -- 净流入
    main_inflow REAL,               -- 主力净流入
    retail_inflow REAL,             -- 散户净流入
    buy_amount  REAL,               -- 买入金额
    sell_amount REAL,               -- 卖出金额

    UNIQUE (flow_type, entity_code, date)
);

CREATE INDEX idx_flow_type ON money_flow(flow_type, entity_code);
CREATE INDEX idx_flow_date ON money_flow(date);
```

**业务规则：**
- `flow_type = 'northbound'` 时 `entity_code` 为空字符串
- 更新频率：交易时段每 5 分钟 / 每日收盘后
- 去重：`(flow_type, entity_code, date)` 唯一，INSERT OR REPLACE

#### margin_daily — 融资融券汇总表

```sql
CREATE TABLE margin_daily (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    date                    TEXT    NOT NULL UNIQUE,   -- 交易日 YYYY-MM-DD
    financing_balance       REAL    NOT NULL,           -- 沪深合计融资余额（元）
    securities_balance      REAL    NOT NULL DEFAULT 0, -- 沪深合计融券余额（元）
    financing_buy_amount    REAL    NOT NULL DEFAULT 0, -- 当日融资买入额（元）
    financing_balance_change REAL,                      -- 融资余额日变动（元）
    total_market_cap        REAL,                       -- 当日A股总市值（元），来自 index_valuation
    leverage_ratio          REAL,                       -- 杠杆率 = financing_balance / total_market_cap × 100%
    updated_at              TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_margin_date ON margin_daily(date);
```

**业务规则：**
- 覆盖 A 股融资融券（沪深合计），每日一条记录
- 历史深度：**10 年**（融资融券业务 2010 年启动）
- 数据源：AKShare `stock_margin_sse()` + `stock_margin_szse()` 合并计算
- `total_market_cap` 取自 `index_valuation` 表中上证指数（000001）当日的 `total_market_cap`
- `leverage_ratio` 在入库时预计算，方便查询
- 去重：`date` 唯一，INSERT OR REPLACE（当日数据可能修正）
- 排序：默认 `date DESC`，百分位计算时切换为 `date ASC`
- 存储估算：10 年 × 250 交易日 ≈ 2500 条

#### news_raw — 新闻原始数据表

```sql
CREATE TABLE news_raw (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    source       TEXT    NOT NULL,       -- jin10
    source_id    TEXT    NOT NULL UNIQUE, -- 金十新闻 ID
    title        TEXT    NOT NULL,
    content      TEXT    NOT NULL DEFAULT '',
    important    INTEGER NOT NULL DEFAULT 0,  -- 0=普通, 1=重要
    tags         TEXT    NOT NULL DEFAULT '[]',  -- JSON 数组
    publish_time TEXT    NOT NULL,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_news_source_id  ON news_raw(source_id);
CREATE INDEX idx_news_publish    ON news_raw(publish_time);
CREATE INDEX idx_news_important  ON news_raw(important);
```

**业务规则：**
- MVP 阶段仅使用金十数据（`source = 'jin10'`）
- TTL：72 小时，超时自动清理
- 去重：`source_id` 唯一，INSERT OR IGNORE
- 排序：`publish_time DESC`

#### data_sync_log — 数据同步日志表

```sql
CREATE TABLE data_sync_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id         TEXT    NOT NULL UNIQUE,
    task_type       TEXT    NOT NULL,   -- init_index | init_symbol | init_board | daily_kline | valuation | financial | news | flow | margin
    target          TEXT    NOT NULL,   -- 标的代码或板块代码
    status          TEXT    NOT NULL DEFAULT 'queued',  -- queued | running | completed | failed
    progress        INTEGER NOT NULL DEFAULT 0,         -- 0-100
    total_records   INTEGER NOT NULL DEFAULT 0,
    loaded_records  INTEGER NOT NULL DEFAULT 0,
    error_message   TEXT,
    started_at      TEXT,
    finished_at     TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (status IN ('queued', 'running', 'completed', 'failed'))
);

CREATE INDEX idx_sync_log_status ON data_sync_log(status);
CREATE INDEX idx_sync_log_type   ON data_sync_log(task_type);
CREATE INDEX idx_sync_log_target ON data_sync_log(target);
```

**业务规则：**
- 记录每次数据拉取任务的状态和进度
- 支持查询任务进度和历史记录
- 失败任务记录 error_message，便于排查

### 3.3 预置数据

#### 核心指数清单（硬编码，不存数据库）

系统首次部署时自动拉取以下 10 个核心指数的 20 年日 K 线：

| # | 市场 | 指数代码 | 指数名称 | AKShare 接口符号 | 估值数据可用性 | 备注 |
|---|------|---------|---------|-----------------|--------------|------|
| 1 | A股 | 000001 | 上证指数 | `000001` | ✅ PE/PB | 国证指数提供 |
| 2 | A股 | 000300 | 沪深300 | `000300` | ✅ PE/PB | 国证指数提供 |
| 3 | A股 | 000905 | 中证500 | `000905` | ✅ PE/PB | 国证指数提供 |
| 4 | A股 | 399006 | 创业板指 | `399006` | ✅ PE/PB | 国证指数提供 |
| 5 | A股 | 000688 | 科创50 | `000688` | ✅ PE/PB | 国证指数提供 |
| 6 | A股 | 930050 | 中证A500 | `930050` | ✅ PE/PB | 国证指数提供 |
| 7 | 港股 | HSI | 恒生指数 | `恒生指数` | ⚠️ 仅价格 | 无免费 PE/PB 历史接口 |
| 8 | 港股 | HSTECH | 恒生科技 | `恒生科技指数` | ⚠️ 仅价格 | 无免费 PE/PB 历史接口 |
| 9 | 美股 | SPX | 标普500 | `标普500` | ⚠️ 仅价格 | 无免费 PE/PB 历史接口 |
| 10 | 美股 | IXIC | 纳斯达克 | `纳斯达克` | ⚠️ 仅价格 | 无免费 PE/PB 历史接口 |

> **估值数据说明：**
> - A股指数（000001-930050）：通过 AKShare `index_all_cni()` 获取每日 PE/PB，存入 `index_valuation` 表
> - 港股/美股指数（HSI/SPX/IXIC）：AKShare `index_global_hist_em()` 只提供价格数据，无 PE/PB。MVP 阶段以**价格百分位**进行估值判断，后续版本补充 PE/PB 数据

```sql
-- 同步日志示例（首次部署时自动创建）
INSERT INTO data_sync_log (task_id, task_type, target, status)
VALUES ('init_core_indices_20260507', 'init_index', 'core_10', 'queued');
```

## 4. 核心业务逻辑

### 4.1 行情获取流程

```python
class QuoteService:

    def get_stock_quote(self, symbol: str, market: str = 'A') -> dict:
        # 1. 查内存缓存
        cache_key = f"quote:{market}:{symbol}"
        cached = memory_cache.get(cache_key)
        if cached and not cached.is_expired(ttl=60):
            return cached

        # 2. 查 SQLite 最新快照
        latest = StockDailyKline.query.filter_by(
            symbol=symbol, market=market
        ).order_by(desc('date')).first()

        # 3. 如果是交易时段且快照超过 60 秒，调用外部源刷新
        if is_trading_hours() and (not latest or latest.date == today()):
            fresh = akshare.get_stock_realtime(symbol, market)
            if fresh:
                # 更新内存缓存
                memory_cache.set(cache_key, fresh, ttl=60)
                # 更新 SQLite 当日快照
                self._upsert_daily_kline(fresh)
                return fresh

        # 4. 非交易时段或无新数据，返回缓存
        return latest.to_dict() if latest else None
```

### 4.2 历史 K 线拉取流程

```python
class KlineService:

    def fetch_historical_klines(self, symbol: str, market: str,
                                 depth_years: int = 10) -> str:
        """
        触发历史 K 线拉取任务。
        返回 task_id，前端可通过任务接口查询进度。
        """
        task_id = generate_task_id()
        # 创建同步日志
        DataSyncLog.create(task_id=task_id, task_type='init_symbol',
                          target=f"{market}:{symbol}", status='queued')

        # 提交到后台任务队列
        task_queue.enqueue(self._do_fetch_klines,
                          task_id, symbol, market, depth_years)
        return task_id

    def _do_fetch_klines(self, task_id, symbol, market, depth_years):
        log = DataSyncLog.query.filter_by(task_id=task_id).first()
        log.status = 'running'
        log.started_at = now()
        log.save()

        try:
            # 调用 AKShare 拉取历史数据
            df = akshare.get_stock_hist(symbol, market,
                                        years=depth_years)
            log.total_records = len(df)

            for i, row in df.iterrows():
                # INSERT OR IGNORE 去重
                StockDailyKline.insert_or_ignore(
                    symbol=symbol, market=market,
                    date=row['date'], open=row['open'],
                    high=row['high'], low=row['low'],
                    close=row['close'], volume=row['volume'],
                    turnover=row['turnover']
                )
                log.loaded_records = i + 1
                log.progress = int((i + 1) / len(df) * 100)
                if i % 100 == 0:
                    log.save()  # 每 100 条更新一次进度

                # 限流：每条间隔 0.5 秒
                time.sleep(0.5)

            log.status = 'completed'
            log.finished_at = now()
            log.save()

        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)
            log.finished_at = now()
            log.save()
```

### 4.3 定时刷新调度

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# 每日 16:30 — K 线增量更新
scheduler.add_job(daily_kline_update, 'cron',
                  hour=16, minute=30, day_of_week='mon-fri')

# 每日 18:00 — 估值 + 板块刷新
scheduler.add_job(daily_valuation_update, 'cron',
                  hour=18, minute=0, day_of_week='mon-fri')

# 每 30 分钟 — 新闻拉取
scheduler.add_job(news_fetch_incremental, 'interval',
                  minutes=30)

# 每周一 10:00 — 财务报表检查
scheduler.add_job(weekly_financial_check, 'cron',
                  hour=10, minute=0, day_of_week='mon')

def daily_kline_update():
    """增量更新所有已入库标的的日 K"""
    # 1. 更新 10 个核心指数
    for idx in CORE_INDICES:
        fetch_latest_kline(idx.symbol, idx.market, type='index')

    # 2. 更新所有用户自选股（从 Module 0 获取）
    symbols = get_all_user_watchlist_symbols()
    for sym in symbols:
        fetch_latest_kline(sym.symbol, sym.market, type='stock')
        time.sleep(0.5)  # 限流

    # 3. 更新所有用户关注板块
    boards = get_all_user_sector_favorites()
    for board in boards:
        fetch_latest_kline(board.code, type='board')
        time.sleep(0.5)
```

### 4.4 用户添加自选触发流程

```python
def on_user_add_watchlist_item(user_id: int, symbol: str,
                                market: str, asset_type: str):
    """
    Module 0 添加自选股后，触发 Module 1 数据初始化。
    通过事件机制或直接调用实现。
    """
    # 检查该标的是否已有历史数据
    exists = StockDailyKline.query.filter_by(
        symbol=symbol, market=market
    ).first()

    if not exists:
        # 首次添加，触发历史数据拉取
        task_id = kline_service.fetch_historical_klines(
            symbol=symbol, market=market, depth_years=10
        )
        return {"status": "data_loading", "task_id": task_id}

    return {"status": "data_ready"}
```

## 5. 与上下游模块的接口契约

### 5.1 对下游暴露的能力

| 消费者模块 | 调用的 API | 用途 |
|-----------|-----------|------|
| Module 2 新闻聚合 | GET /api/v1/data/news | 获取金十原始快讯 |
| Module 3 市场概览 | GET /api/v1/data/quotes/indices | 首页指数行情 |
| Module 3 市场概览 | GET /api/v1/data/quotes/boards | 板块涨跌排行 |
| Module 3 市场概览 | GET /api/v1/data/flows/northbound | 北向资金流向 |
| Module 4 估值分析 | GET /api/v1/data/valuations/index/:symbol | 指数 PE/PB |
| Module 4 估值分析 | GET /api/v1/data/klines/index/:symbol | 历史 K 线（计算 PE 百分位） |
| Module 4 估值分析 | GET /api/v1/data/boards/indices/:symbol/constituents | 指数成分股 |
| Module 4 估值分析 | GET /api/v1/data/margin/summary | 融资融券历史+百分位（杠杆率分析） |
| Module 5 板块概念 | GET /api/v1/data/klines/board/:code | 板块历史 K 线 |
| Module 5 板块概念 | GET /api/v1/data/boards/:code/constituents | 板块成分股 |
| Module 5 板块概念 | GET /api/v1/data/flows/board/:code | 板块资金流向 |
| Module 6 个股详情 | GET /api/v1/data/klines/stock/:symbol | 个股历史 K 线 |
| Module 6 个股详情 | GET /api/v1/data/valuations/stock/:symbol | 个股估值 |
| Module 6 个股详情 | GET /api/v1/data/financials/:symbol | 个股财务 |

### 5.2 依赖的上游模块

| 上游模块 | 依赖内容 | 调用方式 |
|---------|---------|---------|
| Module 0 用户系统 | `@auth_required` 认证 | 装饰器 |
| Module 0 用户系统 | 用户自选股列表 | GET /api/v1/watchlists/:id/items |
| Module 0 用户系统 | 用户板块关注列表 | GET /api/v1/sectors/favorites |

## 6. 错误处理规范

### 统一错误响应格式

```json
{
  "error": {
    "code": "SYMBOL_NOT_FOUND",
    "message": "标的代码不存在"
  }
}
```

### Module 1 错误码清单

| HTTP 状态码 | 错误码 | 说明 |
|-------------|--------|------|
| 401 | UNAUTHORIZED | 未提供 Token |
| 404 | SYMBOL_NOT_FOUND | 标的代码不存在 |
| 404 | BOARD_NOT_FOUND | 板块代码不存在 |
| 404 | DATA_NOT_FOUND | 无可用数据 |
| 409 | DATA_NOT_READY | 该标的数据正在初始化中 |
| 400 | INVALID_DATE_RANGE | 日期范围无效 |
| 400 | INVALID_PERIOD | K 线周期参数无效 |
| 429 | RATE_LIMITED | 请求过于频繁 |
| 500 | FETCH_FAILED | 外部数据源获取失败 |
| 500 | TASK_FAILED | 数据任务执行失败 |

## 7. 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| JIN10_API_KEY | 是 | 金十数据 API Key |
| DATA_CACHE_DIR | 否 | SQLite 数据文件目录，默认 `./data` |
| MEMORY_CACHE_TTL | 否 | 内存缓存默认 TTL（秒），默认 60 |
| AKSHARE_CALL_INTERVAL | 否 | AKShare 调用间隔（秒），默认 0.5 |
| SYNC_WORKER_COUNT | 否 | 后台同步 Worker 数量，默认 1 |
| CORE_INDICES | 否 | 核心指数清单（JSON），默认内置 10 个 |

## 8. 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| K 线表按类型分表 | stock / index / board 三张表 | 不同历史深度、不同查询模式、不同索引策略 |
| K 线只存日 K | 日 K 存储，周/月 K 按需聚合 | 减少存储冗余，聚合逻辑简单 |
| 估值数据 INSERT OR REPLACE | 当日覆盖更新 | 估值数据可能在盘后修正 |
| K 线数据 INSERT OR IGNORE | 已存在不覆盖 | 历史数据不会修正，避免重复写入 |
| 新闻 TTL 72 小时 | 自动清理过期新闻 | 新闻时效性强，控制数据量 |
| 初始化按需触发 | 用户添加后异步拉取 | 不预拉全量数据，减少无意义存储和外部源压力 |
| 任务状态持久化 | data_sync_log 表 | 重启后可恢复任务状态，支持进度查询 |
| 内存缓存用进程内 dict | MVP 够用 | 无需引入 Redis，单机部署场景足够 |
| 融资融券纳入数据底座 | 沪深汇总级别，10 年历史 | 杠杆率百分位是市场热度核心指标，数据量极小（~2500 条） |
| 融资融券入库时预计算杠杆率 | leverage_ratio 字段冗余存储 | 避免每次查询时重复计算，百分位查询更高效 |
| A 股总市值近似 | 上证指数 total_market_cap | 覆盖 90%+ 市值，精度足够；避免全市场扫描的性能开销 |

## 9. 待确认项

- [ ] 金十数据 API 的具体接口路径和返回格式？（需确认 API Key 后对接）
- [ ] 港股实时行情是否也需要从 AKShare 获取？还是只用腾讯财经？
- [ ] 板块搜索是否需要支持拼音首字母搜索？（如输入 `bdt` 匹配 `半导体`）
- [ ] 数据同步失败时是否需要告警通知？（MVP 后置？）
