import requests
import akshare as ak

from app.utils.exceptions import SymbolNotFound


class QuoteService:
    def get_stock_quote(self, symbol: str, market: str = "A") -> dict:
        try:
            if market == "A":
                df = ak.stock_individual_spot_xq(symbol=symbol)
                if df.empty:
                    raise SymbolNotFound()
                row = df.iloc[0]
                return {
                    "symbol": symbol,
                    "name": str(row.get("股票名称", symbol)),
                    "market": market,
                    "price": float(row.get("最新价", 0)),
                    "change": float(row.get("涨跌额", 0)),
                    "change_pct": float(row.get("涨跌幅", 0)),
                    "open": float(row.get("今开", 0)),
                    "high": float(row.get("最高", 0)),
                    "low": float(row.get("最低", 0)),
                    "prev_close": float(row.get("昨收", 0)),
                    "volume": int(row.get("成交量", 0)),
                    "turnover": float(row.get("成交额", 0)),
                    "pe_ttm": self._safe_float(row.get("市盈率_TTM")),
                    "pb": self._safe_float(row.get("市净率")),
                    "market_cap": float(row.get("总市值", 0)),
                }
            else:
                return self._get_tencent_quote(symbol, market)
        except Exception as e:
            if "SymbolNotFound" in str(type(e)):
                raise
            return self._get_tencent_quote(symbol, market)

    def get_index_quote(self, symbol: str, market: str = "A") -> dict:
        try:
            return self._get_tencent_quote(symbol, market)
        except Exception:
            # 腾讯不支持美股指数，使用 AKShare 作为 fallback
            if market == "US":
                return self._get_us_index_quote_from_akshare(symbol)
            raise SymbolNotFound()

    def _get_us_index_quote_from_akshare(self, symbol: str) -> dict:
        """通过 AKShare 获取美股指数最新行情（从日K线中取最后一条）"""
        import akshare as ak
        ak_symbol = ".INX" if symbol == "SPX" else ".IXIC" if symbol == "IXIC" else symbol
        df = ak.index_us_stock_sina(symbol=ak_symbol)
        if df.empty:
            raise SymbolNotFound()
        row = df.iloc[-1]
        close_val = float(row.get("close", 0))
        open_val = float(row.get("open", 0))
        change_pct = round((close_val - open_val) / open_val * 100, 2) if open_val else 0
        return {
            "symbol": symbol,
            "name": "标普500" if symbol == "SPX" else "纳斯达克" if symbol == "IXIC" else symbol,
            "market": "US",
            "price": close_val,
            "change": round(close_val - open_val, 2),
            "change_pct": change_pct,
            "open": open_val,
            "high": float(row.get("high", 0)),
            "low": float(row.get("low", 0)),
            "prev_close": open_val,
            "volume": int(row.get("volume", 0)) if self._notna(row.get("volume")) else 0,
            "turnover": 0,
        }

    def _notna(self, val):
        import math
        return val is not None and not (isinstance(val, float) and math.isnan(val))

    def _get_tencent_quote(self, symbol: str, market: str) -> dict:
        tencent_symbol = self._to_tencent_symbol(symbol, market)
        url = f"https://qt.gtimg.cn/q={tencent_symbol}"
        resp = requests.get(url, timeout=10)
        resp.encoding = "gbk"
        text = resp.text
        if not text or "v_" not in text:
            raise SymbolNotFound()

        data_part = text.split('"')[1]
        fields = data_part.split("~")
        if len(fields) < 45:
            raise SymbolNotFound()

        return {
            "symbol": symbol,
            "name": fields[1],
            "market": market,
            "price": float(fields[3]),
            "change": float(fields[31]),
            "change_pct": float(fields[32]),
            "open": float(fields[5]) if len(fields) > 5 else 0,
            "high": float(fields[33]),
            "low": float(fields[34]),
            "prev_close": float(fields[4]) if len(fields) > 4 else 0,
            "volume": int(float(fields[36])) if len(fields) > 36 else 0,
            "turnover": float(fields[37]) if len(fields) > 37 else 0,
            "updated_at": fields[30] if len(fields) > 30 else "",
        }

    def _to_tencent_symbol(self, symbol: str, market: str) -> str:
        if market == "A":
            # Index codes: 000xxx = sh, 399xxx = sz
            if symbol.startswith("399"):
                return f"sz{symbol}"
            return f"sh{symbol}"
        elif market == "HK":
            return f"hk{symbol}"
        elif market == "US":
            return symbol
        return symbol

    def _safe_float(self, val):
        if val is None or val == "-":
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
