#!/usr/bin/env python3
"""Fetch recent index valuations from CSIndex for indices not covered by LG."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import akshare as ak
from app import create_app, db
from app.models.data import IndexValuation

CSINDEX_SYMBOLS = {
    "000001": "上证指数",
    "000688": "科创50",
    "930050": "中证A500",
}


def sync_csindex_valuations():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        for symbol, name in CSINDEX_SYMBOLS.items():
            print(f"Syncing CSIndex valuations for {symbol} ({name}) ...")
            try:
                df = ak.stock_zh_index_value_csindex(symbol=symbol)
            except Exception as e:
                print(f"  -> failed to fetch: {e}")
                continue

            count = 0
            for _, row in df.iterrows():
                date_str = str(row.get("日期", ""))[:10]
                pe_val = row.get("市盈率1")
                if not date_str or not pe_val:
                    continue
                exists = IndexValuation.query.filter_by(
                    symbol=symbol, market="A", date=date_str
                ).first()
                if exists:
                    continue
                val = IndexValuation(
                    symbol=symbol,
                    market="A",
                    date=date_str,
                    pe_ttm=float(pe_val),
                )
                db.session.add(val)
                count += 1
            db.session.commit()
            print(f"  -> inserted {count} records")


if __name__ == "__main__":
    sync_csindex_valuations()
