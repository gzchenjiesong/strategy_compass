---
title: "Module 3: 市场概览 — 接口与业务逻辑设计"
type: spec
module: module-3
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

## 3. API 接口定义

> 所有接口需通过 `@auth_required` 认证（依赖 Module 0）。
> Module 3 直接暴露给前端，是前端市场页面的唯一数据来源。

### 3.1 概览页

#### GET /api/v3/market/overview

获取概览页完整数据（一次性返回所有需要的数据）。

**响应：**

```json
{
  "market_sentiment": {
    "date": "2026-05-07",
    "leverage": {
      "financing_balance": 1852300000000.00,
      "financing_balance_percentile": 68.5,
      "leverage_ratio": 2.01,
      "leverage_ratio_percentile": 72.3,
      "zone": "overvalued"
    },
    "northbound": {
      "net_buy_5d": 25600000000.00,
      "net_buy_20d": 86500000000.00,
      "zone": "positive"
    },
    "overall_zone": "neutral"
  },
  "zone_summary": {
    "index": {
      "undervalued": 3,
      "neutral": 5,
      "overvalued": 2,
      "total": 10
    }
  },
  "core_indices": [
    {
      "symbol": "000001",
      "name": "上证指数",
      "market": "A",
      "price": 3356.78,
      "change_pct": 0.46,
      "pe_percentile": 45.2,
      "current_drawdown": -6.23,
      "zone": "neutral"
    }
  ],
  "important_news": [
    {
      "id": 12345,
      "title": "美联储主席鲍威尔发表讲话",
      "important": true,
      "time_ago": "10分钟前"
    }
  ]
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `market_sentiment` | 市场情绪指标（杠杆率 + 北向资金） |
| `market_sentiment.overall_zone` | 综合市场情绪：`bullish`/`neutral`/`bearish` |
| `zone_summary` | 估值区间分布统计 |
| `core_indices` | 核心指数速览（最多 6 个） |
| `important_news` | 重要快讯（最多 3 条） |

---

### 3.2 大盘页

#### GET /api/v3/market/indices

获取大盘页数据（A股/港股/美股指数卡片列表）。

**响应：**

```json
{
  "a_share": [
    {
      "symbol": "000001",
      "name": "上证指数",
      "price": 3356.78,
      "change_pct": 0.46,
      "pe_ttm": 14.52,
      "pe_percentile": 45.2,
      "pb": 1.38,
      "pb_percentile": 38.7,
      "current_drawdown": -6.23,
      "max_drawdown": -35.80,
      "zone": "neutral"
    }
  ],
  "hk": [
    {
      "symbol": "HSI",
      "name": "恒生指数",
      "price": 19856.30,
      "change_pct": -0.82,
      "price_percentile": 35.6,
      "current_drawdown": -12.50,
      "max_drawdown": -52.30,
      "zone": "undervalued"
    }
  ],
  "us": [
    {
      "symbol": ".INX",
      "name": "标普500",
      "price": 5123.45,
      "change_pct": 0.23,
      "price_percentile": 78.5,
      "current_drawdown": -3.20,
      "max_drawdown": -25.60,
      "zone": "overvalued"
    }
  ]
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `a_share` | A股指数卡片列表（含 PE/PB 百分位） |
| `hk` | 港股指数卡片列表（仅价格百分位+回撤） |
| `us` | 美股指数卡片列表（仅价格百分位+回撤） |
| `zone` | 综合估值区间 |

**A股指数字段（完整）：**

| 字段 | 说明 |
|------|------|
| `price` | 当前点位 |
| `change_pct` | 涨跌幅 |
| `pe_ttm` | PE-TTM |
| `pe_percentile` | PE 历史百分位 |
| `pb` | PB |
| `pb_percentile` | PB 历史百分位 |
| `current_drawdown` | 当前回撤 |
| `max_drawdown` | 历史最大回撤 |
| `zone` | 综合估值区间 |

**港股/美股指数字段（MVP 简化）：**

| 字段 | 说明 |
|------|------|
| `price` | 当前点位 |
| `change_pct` | 涨跌幅 |
| `price_percentile` | 价格历史百分位 |
| `current_drawdown` | 当前回撤 |
| `max_drawdown` | 历史最大回撤 |
| `zone` | 基于价格百分位判断 |

> **MVP 说明：** 港股/美股指数暂无免费 PE/PB 历史数据源（AKShare 仅覆盖 A 股指数），MVP 阶段以**价格百分位**替代 PE/PB 百分位进行估值判断。后续版本补充 PE/PB 数据。

**综合 zone 计算规则：**

```python
def calc_overall_zone(pe_percentile: float, pb_percentile: float) -> str:
    """综合 PE 和 PB 百分位判断估值区间（A股指数用）。"""
    avg = (pe_percentile + pb_percentile) / 2
    if avg <= 30:
        return "undervalued"
    elif avg <= 70:
        return "neutral"
    else:
        return "overvalued"


def calc_overall_zone_by_price(price_percentile: float) -> str:
    """基于价格百分位判断估值区间（港股/美股指数用）。"""
    if price_percentile <= 30:
        return "undervalued"
    elif price_percentile <= 70:
        return "neutral"
    else:
        return "overvalued"
```

---

### 3.3 板块页

#### GET /api/v3/market/boards

获取板块页数据（用户关注的行业+概念板块卡片列表）。

**响应：**

```json
{
  "industry": [
    {
      "code": "BK0477",
      "name": "半导体",
      "change_pct": 2.35,
      "pe_ttm": 42.18,
      "pe_percentile": 68.5,
      "pb": 3.85,
      "pb_percentile": 55.3,
      "current_drawdown": -12.50,
      "volume_ratio": 1.85,
      "rise_fall_ratio": 7.08,
      "zone": "neutral"
    }
  ],
  "concept": [
    {
      "code": "BK1045",
      "name": "人工智能",
      "change_pct": 3.12,
      "pe_ttm": 55.60,
      "pe_percentile": 72.3,
      "pb": 4.20,
      "pb_percentile": 68.5,
      "current_drawdown": -8.30,
      "volume_ratio": 2.15,
      "rise_fall_ratio": 5.20,
      "zone": "overvalued"
    }
  ]
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `industry` | 行业板块卡片列表（来自用户关注） |
| `concept` | 概念板块卡片列表（来自用户关注） |
| `volume_ratio` | 成交量变化率 |
| `rise_fall_ratio` | 涨跌家数比 |

---

### 3.4 指数详情（弹窗）

#### GET /api/v3/market/index/:symbol/detail

获取单个指数的完整详情数据（用于弹窗展示）。

**路径参数：**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| symbol | string | 指数代码 | `000300` |

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
  "date": "2026-05-07",
  "quote": {
    "price": 3985.42,
    "change": 42.18,
    "change_pct": 1.07,
    "open": 3950.00,
    "high": 3992.00,
    "low": 3945.00,
    "volume": 185230000000,
    "turnover": 2345600000000.00
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

> 此接口直接透传 Module 4 的 `GET /api/v4/valuation/index/:symbol` 响应，加上实时行情数据。

---

### 3.5 板块详情（弹窗）

#### GET /api/v3/market/board/:code/detail

获取单个板块的完整详情数据（用于弹窗展示）。

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
  "date": "2026-05-07",
  "quote": {
    "change_pct": 2.35,
    "turnover": 85600000000.00,
    "rise_count": 85,
    "fall_count": 12
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
    "rise_fall_ratio": 7.08,
    "volume_ratio": 1.85,
    "board_net_inflow": 3250000000.00
  }
}
```

> 此接口直接透传 Module 4 的 `GET /api/v4/valuation/board/:code` 响应，加上实时行情数据。

---

