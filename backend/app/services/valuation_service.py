import math

from app import db
from app.models.data import IndexDailyKline, IndexValuation
from app.utils.exceptions import SymbolNotFound, InsufficientData


class ValuationService:
    def get_index_valuation(self, symbol: str, window_years: int = 10):
        klines = IndexDailyKline.query.filter_by(symbol=symbol).order_by(
            IndexDailyKline.date.desc()
        ).limit(window_years * 260).all()
        if len(klines) < 60:
            raise InsufficientData()

        valuations = IndexValuation.query.filter_by(symbol=symbol).order_by(
            IndexValuation.date.desc()
        ).limit(window_years * 260).all()

        closes = [k.close for k in klines]
        closes.reverse()

        pe_list = [v.pe_ttm for v in valuations if v.pe_ttm and v.pe_ttm > 0]
        pb_list = [v.pb for v in valuations if v.pb and v.pb > 0]

        current_pe = pe_list[-1] if pe_list else None
        current_pb = pb_list[-1] if pb_list else None

        pe_percentile = calc_percentile(current_pe, pe_list) if current_pe else None
        pb_percentile = calc_percentile(current_pb, pb_list) if current_pb else None

        risk = calc_risk_metrics(closes)

        zone = "neutral"
        if pe_percentile is not None:
            if pe_percentile <= 30:
                zone = "undervalued"
            elif pe_percentile >= 70:
                zone = "overvalued"

        return {
            "symbol": symbol,
            "valuation": {
                "pe_ttm": round(current_pe, 2) if current_pe else None,
                "pb": round(current_pb, 2) if current_pb else None,
                "pe_percentile": round(pe_percentile, 2) if pe_percentile is not None else None,
                "pb_percentile": round(pb_percentile, 2) if pb_percentile is not None else None,
                "zone": zone,
            },
            "risk": risk,
        }

    def get_stock_valuation(self, symbol: str, market: str, window_years: int = 10):
        from app.models.data import StockDailyKline, StockValuation
        klines = StockDailyKline.query.filter_by(symbol=symbol, market=market).order_by(
            StockDailyKline.date.desc()
        ).limit(window_years * 260).all()
        if len(klines) < 60:
            raise InsufficientData()

        valuations = StockValuation.query.filter_by(symbol=symbol, market=market).order_by(
            StockValuation.date.desc()
        ).limit(window_years * 260).all()

        closes = [k.close for k in klines]
        closes.reverse()

        pe_list = [v.pe_ttm for v in valuations if v.pe_ttm and v.pe_ttm > 0]
        pb_list = [v.pb for v in valuations if v.pb and v.pb > 0]

        current_pe = pe_list[-1] if pe_list else None
        current_pb = pb_list[-1] if pb_list else None

        pe_percentile = calc_percentile(current_pe, pe_list) if current_pe else None
        pb_percentile = calc_percentile(current_pb, pb_list) if current_pb else None

        risk = calc_risk_metrics(closes)

        zone = "neutral"
        if pe_percentile is not None:
            if pe_percentile <= 30:
                zone = "undervalued"
            elif pe_percentile >= 70:
                zone = "overvalued"

        return {
            "symbol": symbol,
            "market": market,
            "valuation": {
                "pe_ttm": round(current_pe, 2) if current_pe else None,
                "pb": round(current_pb, 2) if current_pb else None,
                "pe_percentile": round(pe_percentile, 2) if pe_percentile is not None else None,
                "pb_percentile": round(pb_percentile, 2) if pb_percentile is not None else None,
                "zone": zone,
            },
            "risk": risk,
        }

    def get_market_valuation(self):
        from app.models.data import IndexInfo
        core_indices = IndexInfo.query.filter_by(is_core=True).all()
        items = []
        for idx in core_indices:
            try:
                val = self.get_index_valuation(idx.symbol, window_years=10)
                items.append({
                    "symbol": idx.symbol,
                    "name": idx.name,
                    "market": idx.market,
                    **val["valuation"],
                })
            except Exception:
                continue
        return {"items": items}


def calc_percentile(current, history):
    if current is None or not history:
        return 50.0

    filtered = [
        h for h in history
        if h is not None and h > 0 and h < 1000
    ]
    if not filtered:
        return 50.0

    count = sum(1 for h in filtered if h <= current)
    return (count / len(filtered)) * 100


def calc_risk_metrics(prices):
    if not prices or len(prices) < 2:
        return {
            "max_drawdown": None,
            "current_drawdown": None,
            "annualized_volatility": None,
        }

    max_dd, peak, _ = calc_max_drawdown(prices)
    current_dd = calc_current_drawdown(prices)
    vol = calc_annualized_volatility(prices)

    return {
        "max_drawdown": round(max_dd, 2) if max_dd is not None else None,
        "current_drawdown": round(current_dd, 2) if current_dd is not None else None,
        "annualized_volatility": round(vol, 2) if vol is not None else None,
    }


def calc_max_drawdown(prices):
    peak = prices[0]
    max_dd = 0.0
    peak_idx = 0
    trough_idx = 0
    for i, p in enumerate(prices):
        if p > peak:
            peak = p
            peak_idx = i
        dd = (peak - p) / peak * 100
        if dd > max_dd:
            max_dd = dd
            trough_idx = i
    return max_dd, peak_idx, trough_idx


def calc_current_drawdown(prices):
    peak = max(prices)
    current = prices[-1]
    return (peak - current) / peak * 100


def calc_annualized_volatility(prices):
    if len(prices) < 2:
        return None
    returns = []
    for i in range(1, len(prices)):
        r = (prices[i] - prices[i - 1]) / prices[i - 1]
        returns.append(r)
    if not returns:
        return None
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / len(returns)
    daily_vol = math.sqrt(variance)
    return daily_vol * math.sqrt(252) * 100
