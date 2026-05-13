#!/usr/bin/env python3
"""Fetch and store historical K-lines for core indices."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app, db
from app.models.data import IndexInfo
from app.services.kline_service import KlineService


def main():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        indices = IndexInfo.query.filter_by(is_core=True).all()
        for idx in indices:
            if idx.market not in ("A", "HK"):
                continue
            print(f"Syncing {idx.symbol} ({idx.name}) ...")
            try:
                count = KlineService.sync_index_klines(
                    idx.symbol, idx.market, years=20
                )
                print(f"  -> inserted {count} records")
            except Exception as e:
                print(f"  -> error: {e}")


if __name__ == "__main__":
    main()
