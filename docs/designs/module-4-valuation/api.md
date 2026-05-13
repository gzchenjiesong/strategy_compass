---
title: "Module 4: 估值分析 — 接口与业务逻辑设计"
type: spec
module: module-4
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

## 3. API 接口定义

> 所有接口需通过 `@auth_required` 认证（依赖 Module 0）。
> Module 4 不直接暴露给前端，而是被 Module 3/5/6 调用。
> 以下接口供内部模块间调用，前端通过 Module 3/5/6 间接访问。

### 3.1 指数估值分析

#### GET /api/v4/valuation/index/:symbol

获取单个指数的完整估值分析。

**路径参数：**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| symbol | string | 指数代码 | `000300` |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| window_years | integer | 否 | 百分位计算窗口，默认 10（支持 3/5/10/20） |

**响应：**

```json
{
  "symbol": "000300",
  "name": "沪深300",
  "date": "2026-05-07",
  "window_years": 10,
  "price": {
    "current": 3985.42,
    "percentile": 62.3,
    "high_52w": 4250.00,
    "low_52w": 3520.00
  },
  "valuation": {
    "pe_ttm": 12.85,
    "pe_percentile": 45.2,
    "pe_zone": "neutral",
    "pb": 1.42,
    "pb_percentile": 38.7,
    "pb_zone": "undervalued",
    "dividend_yield": 2.65
  },
  "risk": {
    "current_drawdown": -6.23,
    "max_drawdown": -35.80,
    "annualized_volatility": 22.15,
    "sharpe_ratio": 0.68,
    "beta": 1.00
  },
  "deviation": {
    "vs_ma250": 3.52
  }
}
```

**估值区间标签（zone）：**

| 百分位范围 | 标签 | 说明 |
|-----------|------|------|
| 0 - 30% | `undervalued` | 低估 |
| 30 - 70% | `neutral` | 适中 |
| 70 - 100% | `overvalued` | 高估 |

#### GET /api/v4/valuation/indices

批量获取指数估值分析（首页概览用）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| symbols | string | 否 | 逗号分隔的指数代码，不传则返回全部核心指数 |
| window_years | integer | 否 | 百分位计算窗口，默认 10 |

**响应：**

```json
{
  "items": [
    {
      "symbol": "000300",
      "name": "沪深300",
      "date": "2026-05-07",
      "price_percentile": 62.3,
      "pe_ttm": 12.85,
      "pe_percentile": 45.2,
      "pb": 1.42,
      "pb_percentile": 38.7,
      "current_drawdown": -6.23,
      "pe_zone": "neutral",
      "pb_zone": "undervalued"
    }
  ]
}
```

---

### 3.2 板块估值分析

#### GET /api/v4/valuation/board/:code

获取单个板块的估值分析。

**路径参数：**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| code | string | 板块代码 | `BK0477` |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `industry`（默认）/ `concept` |
| window_years | integer | 否 | 百分位计算窗口，默认 10 |

**响应：**

```json
{
  "code": "BK0477",
  "name": "半导体",
  "type": "industry",
  "date": "2026-05-07",
  "window_years": 10,
  "price": {
    "percentile": 75.2
  },
  "valuation": {
    "pe_ttm": 42.18,
    "pe_percentile": 68.5,
    "pe_zone": "neutral",
    "pb": 3.85,
    "pb_percentile": 55.3,
    "pb_zone": "neutral"
  },
  "risk": {
    "current_drawdown": -12.50,
    "max_drawdown": -58.30,
    "annualized_volatility": 35.20
  },
  "heat": {
    "rise_count": 85,
    "fall_count": 12,
    "rise_fall_ratio": 7.08,
    "volume_ratio": 1.85,
    "board_net_inflow": 3250000000.00
  }
}
```

#### GET /api/v4/valuation/boards

批量获取板块估值分析（板块排行用）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `industry`（默认）/ `concept` |
| sort | string | 否 | 排序字段：`pe_percentile`（默认）/ `pb_percentile` / `price_percentile` / `rise_fall_ratio` |
| order | string | 否 | `asc`（默认）/ `desc` |
| zone | string | 否 | 过滤估值区间：`undervalued` / `neutral` / `overvalued` |
| limit | integer | 否 | 返回数量，默认 20，最大 50 |

**响应：**

```json
{
  "items": [
    {
      "code": "BK0477",
      "name": "半导体",
      "type": "industry",
      "date": "2026-05-07",
      "pe_ttm": 42.18,
      "pe_percentile": 68.5,
      "pe_zone": "neutral",
      "pb_percentile": 55.3,
      "price_percentile": 75.2,
      "current_drawdown": -12.50,
      "volume_ratio": 1.85,
      "rise_fall_ratio": 7.08
    }
  ]
}
```

---

### 3.3 个股估值分析

#### GET /api/v4/valuation/stock/:symbol

获取个股的估值分析。

**路径参数：**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| symbol | string | 股票代码 | `600519` |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| market | string | 否 | `A`（默认）/ `HK` |
| window_years | integer | 否 | 百分位计算窗口，默认 10 |
| benchmark | string | 否 | Beta 基准指数，默认 `000300`（沪深 300） |

**响应：**

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "market": "A",
  "date": "2026-05-07",
  "window_years": 10,
  "valuation": {
    "pe_ttm": 33.25,
    "pe_percentile": 52.8,
    "pe_zone": "neutral",
    "pb": 10.12,
    "pb_percentile": 65.3,
    "pb_zone": "neutral",
    "ps_ttm": 18.56,
    "ps_percentile": 48.2,
    "dividend_yield": 1.85
  },
  "risk": {
    "current_drawdown": -8.30,
    "max_drawdown": -45.20,
    "annualized_volatility": 28.50,
    "sharpe_ratio": 0.82,
    "calmar_ratio": 0.55,
    "beta": 0.85
  },
  "liquidity": {
    "turnover_rate": 0.52
  }
}
```

---

### 3.4 ETF/基金估值分析

#### GET /api/v4/valuation/etf/:symbol

获取 ETF 的估值分析（通过关联指数获取 PE/PB 百分位）。

**路径参数：**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| symbol | string | ETF 代码 | `510300` |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| window_years | integer | 否 | 百分位计算窗口，默认 10 |

**响应：**

```json
{
  "symbol": "510300",
  "name": "华泰柏瑞沪深300ETF",
  "date": "2026-05-07",
  "window_years": 10,
  "linked_index": {
    "symbol": "000300",
    "name": "沪深300"
  },
  "valuation": {
    "pe_ttm": 12.85,
    "pe_percentile": 45.2,
    "pe_zone": "neutral",
    "pb": 1.42,
    "pb_percentile": 38.7,
    "pb_zone": "undervalued"
  },
  "risk": {
    "current_drawdown": -5.80,
    "max_drawdown": -32.10,
    "annualized_volatility": 21.50,
    "sharpe_ratio": 0.72,
    "calmar_ratio": 0.65,
    "beta": 0.98
  }
}
```

---

### 3.5 市场整体估值

#### GET /api/v4/valuation/market

获取市场整体估值指标（杠杆率等宏观指标）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| window_years | integer | 否 | 百分位计算窗口，默认 10 |

**响应：**

```json
{
  "date": "2026-05-07",
  "window_years": 10,
  "leverage": {
    "financing_balance": 1852300000000.00,
    "financing_balance_percentile": 68.5,
    "leverage_ratio": 2.01,
    "leverage_ratio_percentile": 72.3,
    "financing_balance_change": 3520000000.00,
    "total_market_cap": 92350000000000.00
  },
  "northbound": {
    "net_buy_5d": 25600000000.00,
    "net_buy_20d": 86500000000.00
  }
}
```

---

### 3.6 估值区间统计

#### GET /api/v4/valuation/zone-summary

获取各类标的的估值区间分布统计（低估/适中/高估各有多少个）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `index`（默认）/ `industry` / `concept` |
| window_years | integer | 否 | 百分位计算窗口，默认 10 |

**响应：**

```json
{
  "type": "index",
  "date": "2026-05-07",
  "window_years": 10,
  "summary": {
    "undervalued": 3,
    "neutral": 5,
    "overvalued": 2,
    "total": 10
  },
  "items": [
    {
      "symbol": "000300",
      "name": "沪深300",
      "pe_percentile": 45.2,
      "pe_zone": "neutral"
    }
  ]
}
```

---

### 3.7 历史估值曲线

#### GET /api/v4/valuation/history/index/:symbol

获取指数的历史估值曲线（PE/PB 随时间变化的趋势数据，用于前端图表渲染）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| metric | string | 否 | `pe_ttm`（默认）/ `pb` |
| years | integer | 否 | 历史年数，默认 5 |
| limit | integer | 否 | 最大返回条数，默认 500 |

**响应：**

```json
{
  "symbol": "000300",
  "name": "沪深300",
  "metric": "pe_ttm",
  "items": [
    {
      "date": "2026-05-07",
      "price": 3985.42,
      "value": 12.85,
      "percentile": 45.2
    }
  ]
}
```

> **说明：** 返回的是日级数据点，前端可直接渲染为"价格 + PE 百分位"双轴图表。

#### GET /api/v4/valuation/history/stock/:symbol

获取个股的历史估值曲线。

**查询参数：** 同指数历史估值曲线。

---

