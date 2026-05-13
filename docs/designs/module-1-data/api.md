---
title: "Module 1: 数据底座 — 接口与数据模型设计"
type: spec
module: module-1
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

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

