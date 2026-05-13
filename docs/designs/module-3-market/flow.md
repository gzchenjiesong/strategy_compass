---
title: "Module 3: 市场概览 — 接口与业务逻辑设计"
type: spec
module: module-3
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
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

