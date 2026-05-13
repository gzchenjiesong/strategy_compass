#!/usr/bin/env python3
"""Fetch and store US index (S&P 500, NASDAQ) historical K-line data."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import akshare as ak
from app import create_app, db
from app.models.data import IndexDailyKline

# symbol -> (akshare_symbol, market, name)
US_INDICES = {
    "SPX": (".INX", "US", "标普500"),
    "IXIC": (".IXIC", "US", "纳斯达克"),
}


def sync_us_klines():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        for symbol, (ak_symbol, market, name) in US_INDICES.items():
            print(f"Syncing K-line for {symbol} ({name}) from Sina ...")
            try:
                df = ak.index_us_stock_sina(symbol=ak_symbol)
            except Exception as e:
                print(f"  -> failed to fetch: {e}")
                continue

            if df.empty:
                print("  -> empty dataframe")
                continue

            # Rename columns to standard format
            df = df.rename(columns={
                "date": "date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume",
            })

            count = 0
            for _, row in df.iterrows():
                date_str = str(row.get("date", ""))[:10]
                if not date_str:
                    continue

                exists = IndexDailyKline.query.filter_by(
                    symbol=symbol, market=market, date=date_str
                ).first()
                if exists:
                    continue

                # Calculate change_pct
                close_val = float(row.get("close", 0))
                open_val = float(row.get("open", 0))
                change_pct = round((close_val - open_val) / open_val * 100, 2) if open_val else 0

                kline = IndexDailyKline(
                    symbol=symbol,
                    market=market,
                    date=date_str,
                    open=round(float(row.get("open", 0)), 4),
                    high=round(float(row.get("high", 0)), 4),
                    low=round(float(row.get("low", 0)), 4),
                    close=round(close_val, 4),
                    volume=int(row.get("volume", 0)) if _notna(row.get("volume")) else 0,
                    change_pct=change_pct,
                )
                db.session.add(kline)
                count += 1
                if count % 500 == 0:
                    db.session.commit()
                    print(f"  -> committed {count} records...")

            db.session.commit()
            print(f"  -> inserted {count} new records, total now {IndexDailyKline.query.filter_by(symbol=symbol).count()}")


def _notna(val):
    import math
    return val is not None and not (isinstance(val, float) and math.isnan(val))


if __name__ == "__main__":
    sync_us_klines()
