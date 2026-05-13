#!/usr/bin/env python3
"""Fetch and store historical index valuations (PE/PB)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import akshare as ak
from app import create_app, db
from app.models.data import IndexValuation

INDEX_NAME_MAP = {
    "000001": "上证指数",
    "000300": "沪深300",
    "000905": "中证500",
    "399006": "创业板指",
    "000688": "科创50",
    "930050": "中证A500",
}


def sync_valuations():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        for symbol, name in INDEX_NAME_MAP.items():
            print(f"Syncing valuations for {symbol} ({name}) ...")
            try:
                pe_df = ak.stock_index_pe_lg(symbol=name)
                pb_df = ak.stock_index_pb_lg(symbol=name)
            except Exception as e:
                print(f"  -> failed to fetch: {e}")
                continue

            # Build date -> {pe, pb} mapping
            pe_map = {}
            for _, row in pe_df.iterrows():
                date_str = str(row.get("日期", ""))[:10]
                pe_val = row.get("滚动市盈率")
                if date_str and pe_val and pe_val > 0:
                    pe_map[date_str] = float(pe_val)

            pb_map = {}
            for _, row in pb_df.iterrows():
                date_str = str(row.get("日期", ""))[:10]
                pb_val = row.get("市净率")
                if date_str and pb_val and pb_val > 0:
                    pb_map[date_str] = float(pb_val)

            dates = sorted(set(pe_map.keys()) | set(pb_map.keys()))
            count = 0
            for date_str in dates:
                exists = IndexValuation.query.filter_by(
                    symbol=symbol, market="A", date=date_str
                ).first()
                if exists:
                    continue
                val = IndexValuation(
                    symbol=symbol,
                    market="A",
                    date=date_str,
                    pe_ttm=pe_map.get(date_str),
                    pb=pb_map.get(date_str),
                )
                db.session.add(val)
                count += 1
                if count % 500 == 0:
                    db.session.commit()
            db.session.commit()
            print(f"  -> inserted {count} records")


if __name__ == "__main__":
    sync_valuations()
