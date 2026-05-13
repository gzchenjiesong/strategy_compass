from datetime import datetime, timedelta

from app import db
from app.services.quote_service import QuoteService
from app.services.valuation_service import ValuationService
from app.services.news_service import NewsService
from app.models.data import IndexInfo, IndexDailyKline, IndexValuation, NewsRaw


class MarketService:
    def __init__(self):
        self.quote_service = QuoteService()
        self.valuation_service = ValuationService()
        self.news_service = NewsService()

    # ───────────────────────────────
    # 概览页
    # ───────────────────────────────
    def get_overview(self):
        """首页概览数据聚合"""
        core_indices = IndexInfo.query.filter_by(is_core=True).all()

        # 核心指数速览（取有数据的最多6个）
        core_quotes = []
        for idx in core_indices:
            card = self._build_index_card(idx)
            if card:
                core_quotes.append(card)
            if len(core_quotes) >= 6:
                break

        # 估值区间分布
        zone_summary = self._calc_zone_summary(core_indices)

        # 重要快讯（最多3条）
        important_news = self._get_important_news()

        return {
            "core_indices": core_quotes,
            "zone_summary": zone_summary,
            "important_news": important_news,
        }

    # ───────────────────────────────
    # 大盘页
    # ───────────────────────────────
    def get_indices(self):
        """大盘页数据 — 按市场分组"""
        all_indices = IndexInfo.query.filter_by(is_core=True).all()

        a_share = []
        hk = []
        us = []

        for idx in all_indices:
            card = self._build_index_card(idx)
            if not card:
                continue
            if idx.market == "A":
                a_share.append(card)
            elif idx.market == "HK":
                hk.append(card)
            elif idx.market == "US":
                us.append(card)

        return {
            "a_share": a_share,
            "hk": hk,
            "us": us,
        }

    # ───────────────────────────────
    # 辅助方法
    # ───────────────────────────────
    def _build_index_card(self, idx: IndexInfo) -> dict | None:
        """组装单个指数卡片数据"""
        # 实时行情
        try:
            q = self.quote_service.get_index_quote(idx.symbol, idx.market)
        except Exception:
            return None

        price = q.get("price")
        change_pct = q.get("change_pct")

        # 估值数据（A股指数用 PE/PB，港股/美股用价格百分位）
        pe_ttm = None
        pb = None
        pe_percentile = None
        pb_percentile = None
        price_percentile = None
        current_drawdown = None
        max_drawdown = None
        zone = "neutral"

        # K线数据用于计算风险指标和价格百分位
        klines = IndexDailyKline.query.filter_by(
            symbol=idx.symbol, market=idx.market
        ).order_by(IndexDailyKline.date.desc()).limit(10 * 260).all()

        if len(klines) >= 60:
            closes = [k.close for k in klines]
            closes.reverse()

            # 当前回撤 & 最大回撤
            peak = max(closes)
            current_drawdown = round((closes[-1] - peak) / peak * 100, 2)
            max_drawdown = self._calc_max_drawdown(closes)

            # 价格百分位（所有指数通用）
            price_percentile = self._calc_percentile(closes[-1], closes)

            # A股指数：PE/PB 百分位
            if idx.market == "A":
                valuations = IndexValuation.query.filter_by(
                    symbol=idx.symbol
                ).order_by(IndexValuation.date.desc()).limit(10 * 260).all()

                pe_list = [v.pe_ttm for v in valuations if v.pe_ttm and v.pe_ttm > 0]
                pb_list = [v.pb for v in valuations if v.pb and v.pb > 0]

                if pe_list:
                    pe_list.reverse()
                    pe_ttm = round(pe_list[-1], 2)
                    pe_percentile = round(self._calc_percentile(pe_list[-1], pe_list), 2)

                if pb_list:
                    pb_list.reverse()
                    pb = round(pb_list[-1], 2)
                    pb_percentile = round(self._calc_percentile(pb_list[-1], pb_list), 2)

                # 综合 zone（A股用 PE+PB 平均）
                zone = self._calc_zone(pe_percentile, pb_percentile)
            else:
                # 港股/美股用价格百分位判断
                zone = self._calc_zone_by_price(price_percentile)

        card = {
            "symbol": idx.symbol,
            "name": idx.name,
            "market": idx.market,
            "price": price,
            "change_pct": change_pct,
            "zone": zone,
        }

        if pe_ttm is not None:
            card["pe_ttm"] = pe_ttm
        if pb is not None:
            card["pb"] = pb
        if pe_percentile is not None:
            card["pe_percentile"] = pe_percentile
        if pb_percentile is not None:
            card["pb_percentile"] = pb_percentile
        if price_percentile is not None:
            card["price_percentile"] = round(price_percentile, 2)
        if current_drawdown is not None:
            card["current_drawdown"] = current_drawdown
        if max_drawdown is not None:
            card["max_drawdown"] = max_drawdown

        return card

    def _calc_zone_summary(self, indices):
        """计算估值区间分布"""
        zones = {"undervalued": 0, "neutral": 0, "overvalued": 0}
        total = 0

        for idx in indices:
            card = self._build_index_card(idx)
            if card and card.get("zone"):
                zones[card["zone"]] = zones.get(card["zone"], 0) + 1
                total += 1

        return {
            "undervalued": zones["undervalued"],
            "neutral": zones["neutral"],
            "overvalued": zones["overvalued"],
            "total": total,
        }

    def _get_important_news(self):
        """获取重要快讯"""
        try:
            result = self.news_service.get_important_news(limit=3)
            return [
                {
                    "id": item["id"],
                    "title": item["title"],
                    "time_ago": self._format_time_ago(item["publish_time"]),
                }
                for item in result.get("items", [])
            ]
        except Exception:
            return []

    def _calc_max_drawdown(self, prices):
        """计算历史最大回撤"""
        peak = prices[0]
        max_dd = 0
        for p in prices:
            if p > peak:
                peak = p
            dd = (p - peak) / peak
            if dd < max_dd:
                max_dd = dd
        return round(max_dd * 100, 2)

    def _calc_percentile(self, current, history):
        """计算百分位"""
        if not history or current is None:
            return None
        count = sum(1 for h in history if h < current)
        return count / len(history) * 100

    def _calc_zone(self, pe_pct, pb_pct):
        """综合 PE+PB 百分位判断估值区间"""
        vals = [v for v in [pe_pct, pb_pct] if v is not None]
        if not vals:
            return "neutral"
        avg = sum(vals) / len(vals)
        if avg <= 30:
            return "undervalued"
        elif avg >= 70:
            return "overvalued"
        return "neutral"

    def _calc_zone_by_price(self, price_pct):
        """基于价格百分位判断估值区间"""
        if price_pct is None:
            return "neutral"
        if price_pct <= 30:
            return "undervalued"
        elif price_pct >= 70:
            return "overvalued"
        return "neutral"

    def _format_time_ago(self, time_str: str) -> str:
        """格式化相对时间"""
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            diff = datetime.now() - dt
            minutes = int(diff.total_seconds() // 60)
            hours = minutes // 60
            if minutes < 1:
                return "刚刚"
            if minutes < 60:
                return f"{minutes}分钟前"
            if hours < 24:
                return f"{hours}小时前"
            return f"{dt.month}-{dt.day}"
        except Exception:
            return time_str
