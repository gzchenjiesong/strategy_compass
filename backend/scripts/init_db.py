#!/usr/bin/env python3
"""Initialize database tables."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app, db
from app.models.user import (
    User,
    InvitationCode,
    UserWatchlist,
    WatchlistItem,
    UserPreference,
    UserSectorFavorite,
)
from app.models.data import (
    IndexInfo,
    IndexDailyKline,
    StockDailyKline,
    BoardDailyKline,
    IndexValuation,
    StockValuation,
    BoardValuation,
    MarginDaily,
    NewsRaw,
    MacroEvent,
    EventSchedule,
    DataSyncLog,
)


def init_db():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        db.create_all()
        print("Database tables created.")

        # Insert core indices if not exists
        core_indices = [
            {"symbol": "000001", "name": "上证指数", "market": "A", "category": "broad", "is_core": True},
            {"symbol": "000300", "name": "沪深300", "market": "A", "category": "broad", "is_core": True},
            {"symbol": "000905", "name": "中证500", "market": "A", "category": "broad", "is_core": True},
            {"symbol": "399006", "name": "创业板指", "market": "A", "category": "broad", "is_core": True},
            {"symbol": "000688", "name": "科创50", "market": "A", "category": "broad", "is_core": True},
            {"symbol": "930050", "name": "中证A500", "market": "A", "category": "broad", "is_core": True},
            {"symbol": "HSI", "name": "恒生指数", "market": "HK", "category": "broad", "is_core": True},
            {"symbol": "HSTECH", "name": "恒生科技", "market": "HK", "category": "broad", "is_core": True},
            {"symbol": "SPX", "name": "标普500", "market": "US", "category": "broad", "is_core": True},
            {"symbol": "IXIC", "name": "纳斯达克", "market": "US", "category": "broad", "is_core": True},
        ]

        for info in core_indices:
            exists = IndexInfo.query.filter_by(symbol=info["symbol"]).first()
            if not exists:
                idx = IndexInfo(**info)
                db.session.add(idx)

        # Insert a default invitation code for testing
        default_code = InvitationCode.query.filter_by(code="TEST2026").first()
        if not default_code:
            db.session.add(InvitationCode(code="TEST2026", max_uses=-1, status="active"))

        # Insert event schedule rules（MVP 仅利率）
        event_schedules = [
            {
                "event_key": "fed_interest_rate",
                "event_name": "美联储利率决议",
                "country": "USA",
                "event_type": "interest_rate",
                "frequency_desc": "每年8次（约6-7周一次）",
                "next_calc_rule": "next_fomc_date",
                "priority": 10,
            },
            {
                "event_key": "china_lpr",
                "event_name": "LPR报价",
                "country": "CHN",
                "event_type": "interest_rate",
                "frequency_desc": "每月20日",
                "next_calc_rule": "next_month_20th",
                "priority": 10,
            },
            {
                "event_key": "ecb_interest_rate",
                "event_name": "欧洲央行利率决议",
                "country": "EUR",
                "event_type": "interest_rate",
                "frequency_desc": "每年8次",
                "next_calc_rule": "next_ecb_date",
                "priority": 15,
            },
            {
                "event_key": "boj_interest_rate",
                "event_name": "日本央行利率决议",
                "country": "JPN",
                "event_type": "interest_rate",
                "frequency_desc": "每年8次",
                "next_calc_rule": "next_boj_date",
                "priority": 15,
            },
        ]

        inserted_schedules = 0
        for sched in event_schedules:
            exists = EventSchedule.query.filter_by(event_key=sched["event_key"]).first()
            if not exists:
                db.session.add(EventSchedule(**sched))
                inserted_schedules += 1

        db.session.commit()
        print(
            f"Inserted {len(core_indices)} core indices, "
            f"{inserted_schedules} event schedules, and default invitation code."
        )


if __name__ == "__main__":
    init_db()
