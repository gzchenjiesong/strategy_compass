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
> - `docs/modules/module-1-data-source-analysis.md`（数据源选型）
> - `docs/modules/module-1-data-service.md`（数据底座接口+数据模型）
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

## 2. 指标体系

### 2.1 总体设计原则

**不同标的类型，使用不同的指标组合。** 核心逻辑：

| 标的类型 | 核心关注 | 原因 |
|---------|---------|------|
| 大盘指数 | 价格百分位 + PE/PB百分位 + 杠杆率 | 宏观层面判断市场整体估值水位 |
| 行业板块 | PE/PB百分位 + 板块热度 + 资金流向 | 板块轮动与估值匹配 |
| 概念板块 | PE/PB百分位 + 板块热度 + 成交量 | 概念炒作程度与估值偏离 |
| 个股 | PE/PB百分位 + 回撤指标 + 基本面 | 个股深度分析，风险评估更重要 |
| ETF/基金 | PE/PB百分位 + 回撤指标 + 夏普比率 | 产品评价维度，风险收益比是核心 |
| 市场整体 | 杠杆率 + 融资余额百分位 | 全市场只看一组宏观指标 |

### 2.2 大盘指数指标矩阵

#### A股指数指标（完整）

| 指标 | 计算方式 | 数据来源 | 输出 |
|------|---------|---------|------|
| **价格历史百分位** | 当前价格在 N 年历史价格序列中的排位 | index_daily_kline | 百分位 (0-100) |
| **PE-TTM 百分位** | 当前 PE 在 N 年历史 PE 序列中的排位 | index_valuation.pe_ttm | 百分位 (0-100) |
| **PB 百分位** | 当前 PB 在 N 年历史 PB 序列中的排位 | index_valuation.pb | 百分位 (0-100) |
| **股息率** | 当日股息率 | index_valuation.dividend_yield | 百分比 |
| **当前回撤** | (历史最高 - 当前价) / 历史最高 | index_daily_kline | 百分比 |
| **最大回撤** | 历史最大回撤幅度 | index_daily_kline | 百分比 |
| **年化波动率** | 日收益率标准差 × √252 | index_daily_kline | 百分比 |
| **夏普比率** | (年化收益 - 无风险利率) / 年化波动率 | index_daily_kline | 数值 |
| **Beta** | 与上证指数的回归系数 | index_daily_kline | 数值 |
| **大盘偏离度** | 当前价格 vs 250 日均线的偏离 | index_daily_kline | 百分比 |

#### 港股/美股指数指标（MVP 简化）

> **MVP 阶段：** 港股/美股指数暂无免费 PE/PB 历史数据源（AKShare 仅覆盖 A 股指数），以**价格百分位**替代 PE/PB 进行估值判断。

| 指标 | 计算方式 | 数据来源 | 输出 |
|------|---------|---------|------|
| **价格历史百分位** | 当前价格在 N 年历史价格序列中的排位 | index_daily_kline | 百分位 (0-100) |
| **当前回撤** | (历史最高 - 当前价) / 历史最高 | index_daily_kline | 百分比 |
| **最大回撤** | 历史最大回撤幅度 | index_daily_kline | 百分比 |
| **年化波动率** | 日收益率标准差 × √252 | index_daily_kline | 百分比 |
| **夏普比率** | (年化收益 - 无风险利率) / 年化波动率 | index_daily_kline | 数值 |
| **Beta** | 与对应市场基准指数的回归系数 | index_daily_kline | 数值 |
| **大盘偏离度** | 当前价格 vs 250 日均线的偏离 | index_daily_kline | 百分比 |

> **百分位计算窗口：** 默认 10 年（2500 交易日），支持传参调整（3/5/10/20 年）。
> **10 个核心指数**自动计算，用户自选指数按需触发。

### 2.3 行业板块指标矩阵

| 指标 | 计算方式 | 数据来源 | 输出 |
|------|---------|---------|------|
| **PE-TTM 百分位** | 当前 PE 在 N 年历史中的排位 | board_valuation.pe_ttm | 百分位 (0-100) |
| **PB 百分位** | 当前 PB 在 N 年历史中的排位 | board_valuation.pb | 百分位 (0-100) |
| **价格百分位** | 当前价格在 N 年历史中的排位 | board_daily_kline | 百分位 (0-100) |
| **当前回撤** | (历史最高 - 当前价) / 历史最高 | board_daily_kline | 百分比 |
| **最大回撤** | 历史最大回撤幅度 | board_daily_kline | 百分比 |
| **年化波动率** | 日收益率标准差 × √252 | board_daily_kline | 百分比 |
| **板块涨跌家数比** | rise_count / fall_count | quotes/board 接口 | 比值 |
| **板块资金净流入** | 当日净流入金额 | money_flow (board) | 金额 |
| **成交量变化率** | 当日成交量 vs 20 日均量 | board_daily_kline | 倍数 |

### 2.4 概念板块指标矩阵

与行业板块相同，额外增加：

| 指标 | 说明 |
|------|------|
| **成交量变化率** | 概念炒作阶段成交量变化更敏感，单独标注 |

### 2.5 个股指标矩阵

| 指标 | 计算方式 | 数据来源 | 输出 |
|------|---------|---------|------|
| **PE-TTM 百分位** | 当前 PE 在 N 年历史中的排位 | stock_valuation.pe_ttm | 百分位 (0-100) |
| **PB 百分位** | 当前 PB 在 N 年历史中的排位 | stock_valuation.pb | 百分位 (0-100) |
| **PS-TTM 百分位** | 当前 PS 在 N 年历史中的排位 | stock_valuation.ps_ttm | 百分位 (0-100) |
| **股息率** | 当日股息率 | stock_valuation.dividend_yield | 百分比 |
| **当前回撤** | (历史最高 - 当前价) / 历史最高 | stock_daily_kline | 百分比 |
| **最大回撤** | 历史最大回撤幅度 | stock_daily_kline | 百分比 |
| **年化波动率** | 日收益率标准差 × √252 | stock_daily_kline | 百分比 |
| **夏普比率** | (年化收益 - 无风险利率) / 年化波动率 | stock_daily_kline | 数值 |
| **卡玛比率** | 年化收益 / 最大回撤 | stock_daily_kline | 数值 |
| **Beta** | 与沪深 300 的回归系数 | stock_daily_kline + index_daily_kline | 数值 |
| **换手率** | 成交额 / 流通市值 | kline.turnover + stock_valuation.market_cap | 百分比 |

### 2.6 ETF/基金指标矩阵

| 指标 | 计算方式 | 数据来源 | 输出 |
|------|---------|---------|------|
| **PE-TTM 百分位** | 跟踪指数的 PE 百分位 | index_valuation（通过 ETF 关联指数） | 百分位 (0-100) |
| **PB 百分位** | 跟踪指数的 PB 百分位 | index_valuation | 百分位 (0-100) |
| **当前回撤** | (历史最高净值 - 当前净值) / 历史最高 | fund_nav | 百分比 |
| **最大回撤** | 历史最大回撤 | fund_nav / stock_daily_kline | 百分比 |
| **年化波动率** | 日收益率标准差 × √252 | fund_nav / stock_daily_kline | 百分比 |
| **夏普比率** | (年化收益 - 无风险利率) / 年化波动率 | fund_nav / stock_daily_kline | 数值 |
| **卡玛比率** | 年化收益 / 最大回撤 | fund_nav / stock_daily_kline | 数值 |
| **Beta** | 与跟踪指数的回归系数 | fund_nav + index_daily_kline | 数值 |

> **ETF 关联指数映射**：ETF 估值百分位需要知道它跟踪哪个指数。此映射关系可通过 `board_constituent` 表或硬编码核心 ETF→指数映射表实现。

### 2.7 市场整体指标（全局唯一）

| 指标 | 计算方式 | 数据来源 | 输出 |
|------|---------|---------|------|
| **融资余额百分位** | 当日融资余额在 10 年历史中的排位 | margin_daily.financing_balance | 百分位 (0-100) |
| **杠杆率** | 融资余额 / A 股总市值 × 100% | margin_daily.leverage_ratio | 百分比 |
| **杠杆率百分位** | 当日杠杆率在 10 年历史中的排位 | margin_daily.leverage_ratio | 百分位 (0-100) |
| **融资余额日变动** | 当日融资余额变化 | margin_daily.financing_balance_change | 金额 |
| **北向资金累计净流入** | 近 N 日北向资金累计 | money_flow (northbound) | 金额 |

> **注：** 市场整体指标不区分标的，全局只有一份，Module 3 首页仪表盘直接调用。

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

## 4. 核心计算逻辑

### 4.1 百分位计算

百分位是 Module 4 最核心的计算。计算公式：

```python
def calc_percentile(current_value: float, history: list[float]) -> float:
    """
    计算 current_value 在 history 序列中的百分位。
    
    返回 0-100 的数值：
    - 0 表示当前值是历史最低
    - 100 表示当前值是历史最高
    - 50 表示处于历史中位数
    """
    if not history:
        return 50.0  # 无历史数据时返回中性值
    
    below_count = sum(1 for v in history if v < current_value)
    equal_count = sum(1 for v in history if v == current_value)
    
    percentile = (below_count + 0.5 * equal_count) / len(history) * 100
    return round(percentile, 1)
```

**百分位计算规则：**
- 历史序列排除空值（NULL）和异常值（PE < 0 或 PE > 1000 时跳过）
- 时间窗口默认 10 年，支持 3/5/10/20 年
- 历史数据不足 1 年时，不计算百分位，返回 `null` 并附带 `insufficient_data` 标记

### 4.2 估值区间标签

```python
def get_zone(percentile: float) -> str:
    """根据百分位返回估值区间标签。"""
    if percentile is None:
        return "unknown"
    if percentile <= 30:
        return "undervalued"    # 低估
    elif percentile <= 70:
        return "neutral"        # 适中
    else:
        return "overvalued"     # 高估
```

**区间阈值：** 30% / 70%，可通过配置文件调整（`ZONE_LOW=30, ZONE_HIGH=70`）。

### 4.3 风险指标计算

所有风险指标基于日 K 线数据计算：

```python
import math
from typing import Optional

ANNUAL_TRADING_DAYS = 252
RISK_FREE_RATE = 0.02  # 无风险利率 2%，可配置

def calc_annualized_volatility(daily_returns: list[float]) -> float:
    """年化波动率 = 日收益率标准差 × √252"""
    if len(daily_returns) < 30:
        return None
    
    mean = sum(daily_returns) / len(daily_returns)
    variance = sum((r - mean) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
    daily_std = math.sqrt(variance)
    return round(daily_std * math.sqrt(ANNUAL_TRADING_DAYS) * 100, 2)


def calc_max_drawdown(prices: list[float]) -> tuple[float, int, int]:
    """
    最大回撤。
    返回：(最大回撤百分比, 峰值索引, 谷值索引)
    """
    if len(prices) < 2:
        return (None, 0, 0)
    
    max_dd = 0
    peak_idx = 0
    peak = prices[0]
    
    for i, p in enumerate(prices):
        if p > peak:
            peak = p
            peak_idx = i
        dd = (peak - p) / peak
        if dd > max_dd:
            max_dd = dd
    
    return (round(max_dd * 100, 2), peak_idx, 0)


def calc_current_drawdown(prices: list[float]) -> float:
    """当前回撤 = (历史最高 - 当前价) / 历史最高"""
    if len(prices) < 2:
        return None
    
    historical_high = max(prices)
    current = prices[-1]
    dd = (historical_high - current) / historical_high
    return round(dd * 100, 2)


def calc_sharpe_ratio(annualized_return: float, annualized_volatility: float) -> float:
    """夏普比率 = (年化收益 - 无风险利率) / 年化波动率"""
    if annualized_volatility is None or annualized_volatility == 0:
        return None
    return round((annualized_return - RISK_FREE_RATE) / (annualized_volatility / 100), 2)


def calc_calmar_ratio(annualized_return: float, max_drawdown: float) -> float:
    """卡玛比率 = 年化收益 / 最大回撤"""
    if max_drawdown is None or max_drawdown == 0:
        return None
    return round(annualized_return / (max_drawdown / 100), 2)


def calc_beta(daily_returns: list[float], benchmark_returns: list[float]) -> float:
    """Beta = Cov(Ri, Rm) / Var(Rm)"""
    if len(daily_returns) != len(benchmark_returns) or len(daily_returns) < 60:
        return None
    
    mean_r = sum(daily_returns) / len(daily_returns)
    mean_b = sum(benchmark_returns) / len(benchmark_returns)
    
    cov = sum((r - mean_r) * (b - mean_b) for r, b in zip(daily_returns, benchmark_returns)) / (len(daily_returns) - 1)
    var_b = sum((b - mean_b) ** 2 for b in benchmark_returns) / (len(benchmark_returns) - 1)
    
    if var_b == 0:
        return None
    return round(cov / var_b, 2)


def calc_volume_ratio(volumes: list[int], window: int = 20) -> float:
    """成交量变化率 = 当日成交量 / 近 N 日均量"""
    if len(volumes) < window + 1:
        return None
    
    current = volumes[-1]
    avg = sum(volumes[-window - 1:-1]) / window
    
    if avg == 0:
        return None
    return round(current / avg, 2)
```

### 4.4 杠杆率计算

```python
def calc_leverage_ratio(financing_balance: float, total_market_cap: float) -> float:
    """杠杆率 = 融资余额 / A 股总市值 × 100%"""
    if total_market_cap == 0:
        return None
    return round(financing_balance / total_market_cap * 100, 4)
```

### 4.5 计算性能优化

百分位计算需要扫描历史序列，是 Module 4 最大的性能瓶颈。优化策略：

| 策略 | 实现方式 | 说明 |
|------|---------|------|
| **内存预计算** | 系统启动时预加载所有已入库标的的估值序列到内存 | 10 个核心指数 + 用户自选标的 |
| **增量更新** | 每日 18:00 估值数据更新后，仅追加当日数据点到内存序列 | 避免全量重算 |
| **缓存结果** | 百分位计算结果缓存 1 小时 | 同一标的短时间内不会变化 |
| **按需计算** | 用户自选标的首次访问时计算，结果持久化 | 避免启动时计算全部标的 |
| **批量接口** | 批量接口使用 IN 查询一次性取出所有估值历史 | 减少数据库查询次数 |

> **预估性能：** 单个指数百分位计算（2500 条历史数据排序）< 5ms，10 个核心指数批量 < 50ms。

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
