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
> - `docs/modules/module-1-data-service.md`（数据底座接口）
> - `docs/modules/module-4-valuation-analysis.md`（估值分析接口）
> - `docs/modules/module-2-news-aggregator.md`（新闻聚合接口）
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

## 2. 页面结构映射

### 2.1 底部导航栏（固定）

```
┌──────────┬──────────┬──────────┬──────────┐
│   资讯   │   市场   │   关注   │   策略   │
│ Module2  │ Module3  │ Module5  │ Module6  │
└──────────┴──────────┴──────────┴──────────┘
```

### 2.2 Module 3 顶部标签栏（动态）

```
┌──────────┬──────────┬──────────┬────────────────────┐
│   概览   │   大盘   │   板块   │      [用户头像]     │
└──────────┴──────────┴──────────┴────────────────────┘
```

### 2.3 各标签页内容

| 标签 | 内容 | 数据卡片类型 |
|------|------|-------------|
| **概览** | 市场情绪总览 | 情绪指标卡片 + 估值区间分布卡片 + 核心指数速览卡片 |
| **大盘** | A股/港股/美股指数 | 指数卡片（每个指数一个卡片） |
| **板块** | 行业+概念板块 | 板块卡片（每个板块一个卡片） |

### 2.4 卡片 → 弹窗交互

- **卡片**：展示精简数据（2-4 个核心指标）
- **点击卡片**：弹出浮层（Modal），展示完整指标详情
- **弹窗关闭**：返回原页面，不切换路由

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

## 4. 核心业务逻辑

### 4.1 数据聚合流程

Module 3 的核心工作是**数据聚合** — 从 Module 1 和 Module 4 获取数据，组装为前端格式：

```python
class MarketOverviewService:

    def get_overview(self, user_id: int) -> dict:
        """
        获取概览页数据。
        聚合：市场情绪 + 估值区间分布 + 核心指数速览 + 重要快讯。
        """
        # 1. 市场整体估值（Module 4）
        market_valuation = self._call_module4("/api/v4/valuation/market")

        # 2. 估值区间分布（Module 4）
        zone_summary = self._call_module4("/api/v4/valuation/zone-summary?type=index")

        # 3. 核心指数批量估值（Module 4）
        core_indices = self._call_module4("/api/v4/valuation/indices")

        # 4. 重要快讯（Module 2）
        important_news = self._call_module2("/api/v2/news?filter=important&limit=3")

        # 5. 组装响应
        return {
            "market_sentiment": self._build_sentiment(market_valuation),
            "zone_summary": zone_summary,
            "core_indices": self._simplify_indices(core_indices),
            "important_news": important_news["items"]
        }

    def get_indices(self) -> dict:
        """
        获取大盘页数据。
        按市场分组返回指数卡片列表。
        """
        # 获取所有核心指数的估值数据
        all_indices = self._call_module4("/api/v4/valuation/indices")

        # 按市场分组
        result = {"a_share": [], "hk": [], "us": []}
        for item in all_indices["items"]:
            market = self._get_market_by_symbol(item["symbol"])
            card = self._build_index_card(item)
            result[market].append(card)

        return result

    def get_boards(self, user_id: int) -> dict:
        """
        获取板块页数据。
        返回用户关注的行业+概念板块卡片列表。
        """
        # 1. 获取用户关注板块（Module 0）
        user_boards = self._get_user_favorite_boards(user_id)

        # 2. 批量获取板块估值（Module 4）
        industry_codes = [b.code for b in user_boards if b.type == "industry"]
        concept_codes = [b.code for b in user_boards if b.type == "concept"]

        industry_valuations = []
        if industry_codes:
            industry_valuations = self._call_module4(
                f"/api/v4/valuation/boards?type=industry&limit=50"
            )
            # 过滤出用户关注的
            industry_valuations = self._filter_by_codes(
                industry_valuations["items"], industry_codes
            )

        concept_valuations = []
        if concept_codes:
            concept_valuations = self._call_module4(
                f"/api/v4/valuation/boards?type=concept&limit=50"
            )
            concept_valuations = self._filter_by_codes(
                concept_valuations["items"], concept_codes
            )

        return {
            "industry": [self._build_board_card(v) for v in industry_valuations],
            "concept": [self._build_board_card(v) for v in concept_valuations]
        }
```

### 4.2 卡片数据组装

```python
def _build_index_card(self, valuation: dict) -> dict:
    """组装指数卡片（精简格式，适合列表展示）。"""
    return {
        "symbol": valuation["symbol"],
        "name": valuation["name"],
        "price": valuation["price"]["current"],
        "change_pct": self._get_change_pct(valuation["symbol"]),
        "pe_ttm": valuation["valuation"]["pe_ttm"],
        "pe_percentile": valuation["valuation"]["pe_percentile"],
        "pb": valuation["valuation"]["pb"],
        "pb_percentile": valuation["valuation"]["pb_percentile"],
        "current_drawdown": valuation["risk"]["current_drawdown"],
        "max_drawdown": valuation["risk"]["max_drawdown"],
        "zone": self._calc_overall_zone(
            valuation["valuation"]["pe_percentile"],
            valuation["valuation"]["pb_percentile"]
        )
    }


def _build_board_card(self, valuation: dict) -> dict:
    """组装板块卡片（精简格式）。"""
    return {
        "code": valuation["code"],
        "name": valuation["name"],
        "change_pct": self._get_board_change_pct(valuation["code"]),
        "pe_ttm": valuation["valuation"]["pe_ttm"],
        "pe_percentile": valuation["valuation"]["pe_percentile"],
        "pb": valuation["valuation"]["pb"],
        "pb_percentile": valuation["valuation"]["pb_percentile"],
        "current_drawdown": valuation["risk"]["current_drawdown"],
        "volume_ratio": valuation["heat"]["volume_ratio"],
        "rise_fall_ratio": valuation["heat"]["rise_fall_ratio"],
        "zone": self._calc_overall_zone(
            valuation["valuation"]["pe_percentile"],
            valuation["valuation"]["pb_percentile"]
        )
    }
```

### 4.3 市场情绪计算

```python
def _build_sentiment(self, market_valuation: dict) -> dict:
    """
    构建市场情绪指标。
    综合杠杆率百分位和北向资金判断市场整体情绪。
    """
    leverage = market_valuation["leverage"]
    northbound = market_valuation["northbound"]

    # 杠杆率区间
    leverage_zone = self._get_zone(leverage["leverage_ratio_percentile"])

    # 北向资金区间（5日累计净流入）
    northbound_5d = northbound["net_buy_5d"]
    if northbound_5d > 50000000000:  # 50亿
        northbound_zone = "positive"
    elif northbound_5d < -50000000000:
        northbound_zone = "negative"
    else:
        northbound_zone = "neutral"

    # 综合情绪
    overall = self._calc_overall_sentiment(leverage_zone, northbound_zone)

    return {
        "date": market_valuation["date"],
        "leverage": {
            "financing_balance": leverage["financing_balance"],
            "financing_balance_percentile": leverage["financing_balance_percentile"],
            "leverage_ratio": leverage["leverage_ratio"],
            "leverage_ratio_percentile": leverage["leverage_ratio_percentile"],
            "zone": leverage_zone
        },
        "northbound": {
            "net_buy_5d": northbound_5d,
            "net_buy_20d": northbound["net_buy_20d"],
            "zone": northbound_zone
        },
        "overall_zone": overall
    }


def _calc_overall_sentiment(self, leverage_zone: str, northbound_zone: str) -> str:
    """
    综合判断市场情绪。
    
    规则：
    - 杠杆率低估 + 北向流入 → bullish
    - 杠杆率高估 + 北向流出 → bearish
    - 其他 → neutral
    """
    score = 0
    if leverage_zone == "undervalued":
        score += 1
    elif leverage_zone == "overvalued":
        score -= 1

    if northbound_zone == "positive":
        score += 1
    elif northbound_zone == "negative":
        score -= 1

    if score >= 2:
        return "bullish"
    elif score <= -2:
        return "bearish"
    else:
        return "neutral"
```

### 4.4 缓存策略

```python
# 首页数据缓存时间（秒）
OVERVIEW_CACHE_TTL = 300  # 5 分钟
INDICES_CACHE_TTL = 60    # 1 分钟（行情变化快）
BOARDS_CACHE_TTL = 300    # 5 分钟

def get_overview(self, user_id: int) -> dict:
    cache_key = f"overview:{user_id}"
    cached = memory_cache.get(cache_key)
    if cached and not cached.is_expired(ttl=OVERVIEW_CACHE_TTL):
        return cached

    # 查询并缓存
    result = self._query_overview(user_id)
    memory_cache.set(cache_key, result, ttl=OVERVIEW_CACHE_TTL)
    return result
```

---

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

## 7. 性能考虑

| 优化点 | 实现方式 | 预估效果 |
|--------|---------|---------|
| 首页数据缓存 | 内存缓存 5 分钟 | 减少 90% 重复查询 |
| 批量查询 | 一次性获取所有核心指数 | 减少 N 次单查询 |
| 卡片精简 | 只返回展示所需字段 | 减少 50% 数据传输 |
| 弹窗懒加载 | 点击时才查询详情 | 首屏加载更快 |

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

## 9. 前端组件映射

### 9.1 页面结构

```
AppLayout
├── TopBar（顶部固定栏）
│   ├── TabButtons（动态标签：概览/大盘/板块）
│   └── UserAvatar（固定用户头像）
├── MainContent（中间滚动区）
│   └── CardList（卡片列表）
│       ├── IndexCard（指数卡片）
│       ├── BoardCard（板块卡片）
│       └── NewsCard（新闻卡片 - 概览页）
├── BottomNav（底部固定栏）
│   ├── NavItem（资讯）
│   ├── NavItem（市场 - 当前激活）
│   ├── NavItem（关注）
│   └── NavItem（策略）
└── DetailModal（弹窗浮层）
    ├── IndexDetail（指数详情）
    └── BoardDetail（板块详情）
```

### 9.2 卡片设计

**指数卡片（大盘页）：**

```
┌─────────────────────────────┐
│ 上证指数        000001  [A] │
│                             │
│  3356.78          +0.46%    │
│                             │
│  PE: 14.5  |  百分位: 45%   │
│  回撤: -6.2% | 状态: 适中   │
└─────────────────────────────┘
```

**板块卡片（板块页）：**

```
┌─────────────────────────────┐
│ 半导体            BK0477    │
│                             │
│  +2.35%          热度: 高   │
│                             │
│  PE: 42.2  |  百分位: 69%   │
│  量比: 1.85 | 状态: 适中    │
└─────────────────────────────┘
```

### 9.3 弹窗设计

**指数详情弹窗：**

```
┌─────────────────────────────┐
│ 沪深300 (000300)        [X] │
├─────────────────────────────┤
│ 实时行情                     │
│  3985.42  +1.07%            │
├─────────────────────────────┤
│ 估值指标                     │
│  PE-TTM: 12.85  百分位: 45% │
│  PB: 1.42       百分位: 39% │
│  股息率: 2.65%              │
├─────────────────────────────┤
│ 风险指标                     │
│  当前回撤: -6.23%           │
│  最大回撤: -35.80%          │
│  年化波动: 22.15%           │
│  夏普比率: 0.68             │
├─────────────────────────────┤
│ [查看历史估值曲线]            │
└─────────────────────────────┘
```

---

## 10. 未来扩展（非 MVP）

| 功能 | 说明 |
|------|------|
| 自定义首页布局 | 用户可拖拽调整卡片顺序 |
| 全球市场概览 | 增加更多海外市场指数（日经、德国DAX等） |
| 板块热度排行 | 全量板块按热度排序，不限用户关注 |
| 大盘分时图 | 指数实时分时走势 |
| 指数成分股列表 | 弹窗内展示指数成分股及权重 |
| 方案D：全市场统计 | 新增全市场统计表（总市值、总成交额等） |
