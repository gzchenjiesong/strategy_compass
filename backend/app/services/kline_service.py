import akshare as ak

from app import db
from app.models.data import IndexDailyKline, StockDailyKline
from app.utils.exceptions import SymbolNotFound, DataNotReady


class KlineService:
    def get_index_klines(self, symbol, market, start_date, end_date, limit=250):
        query = IndexDailyKline.query.filter_by(symbol=symbol, market=market)
        if start_date:
            query = query.filter(IndexDailyKline.date >= start_date)
        if end_date:
            query = query.filter(IndexDailyKline.date <= end_date)
        rows = query.order_by(IndexDailyKline.date.desc()).limit(limit).all()
        if not rows:
            raise DataNotReady()
        rows.reverse()
        return {
            "symbol": symbol,
            "market": market,
            "items": [
                {
                    "date": r.date,
                    "open": r.open,
                    "high": r.high,
                    "low": r.low,
                    "close": r.close,
                    "volume": r.volume,
                    "turnover": r.turnover,
                    "change_pct": r.change_pct,
                }
                for r in rows
            ],
        }

    def get_stock_klines(self, symbol, market, start_date, end_date, limit=250):
        query = StockDailyKline.query.filter_by(symbol=symbol, market=market)
        if start_date:
            query = query.filter(StockDailyKline.date >= start_date)
        if end_date:
            query = query.filter(StockDailyKline.date <= end_date)
        rows = query.order_by(StockDailyKline.date.desc()).limit(limit).all()
        if not rows:
            raise DataNotReady()
        rows.reverse()
        return {
            "symbol": symbol,
            "market": market,
            "items": [
                {
                    "date": r.date,
                    "open": r.open,
                    "high": r.high,
                    "low": r.low,
                    "close": r.close,
                    "volume": r.volume,
                    "turnover": r.turnover,
                    "change_pct": r.change_pct,
                }
                for r in rows
            ],
        }

    @staticmethod
    def sync_index_klines(symbol: str, market: str = "A", years: int = 10):
        import time
        from datetime import datetime, timedelta

        cutoff_date = (datetime.now() - timedelta(days=years * 365)).strftime("%Y-%m-%d")

        for attempt in range(3):
            try:
                if market == "A":
                    df = ak.index_zh_a_hist(symbol=symbol, period="daily")
                elif market == "HK":
                    df = ak.stock_hk_index_daily_sina(symbol=symbol)
                else:
                    return 0
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    print(f"[sync_index_klines] Failed to fetch {symbol} after 3 attempts: {e}")
                    return 0

        if df is None or df.empty:
            return 0

        count = 0
        for _, row in df.iterrows():
            if market == "A":
                date_str = str(row.get("日期", ""))[:10]
                open_val = float(row.get("开盘", 0) or 0)
                high_val = float(row.get("最高", 0) or 0)
                low_val = float(row.get("最低", 0) or 0)
                close_val = float(row.get("收盘", 0) or 0)
                volume_val = int(row.get("成交量", 0) or 0)
                turnover_val = float(row.get("成交额", 0) or 0)
                change_pct_val = float(row.get("涨跌幅", 0) or 0)
            else:
                date_str = str(row.get("date", ""))[:10]
                open_val = float(row.get("open", 0) or 0)
                high_val = float(row.get("high", 0) or 0)
                low_val = float(row.get("low", 0) or 0)
                close_val = float(row.get("close", 0) or 0)
                volume_val = int(row.get("volume", 0) or 0)
                turnover_val = float(row.get("amount", 0) or 0)
                change_pct_val = None

            if not date_str or date_str < cutoff_date:
                continue
            exists = IndexDailyKline.query.filter_by(
                symbol=symbol, market=market, date=date_str
            ).first()
            if exists:
                continue
            kline = IndexDailyKline(
                symbol=symbol,
                market=market,
                date=date_str,
                open=open_val,
                high=high_val,
                low=low_val,
                close=close_val,
                volume=volume_val,
                turnover=turnover_val,
                change_pct=change_pct_val,
            )
            db.session.add(kline)
            count += 1
            if count % 500 == 0:
                db.session.commit()
        db.session.commit()
        return count
