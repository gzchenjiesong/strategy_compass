#!/usr/bin/env python3
"""
宏观经济事件同步脚本

用法:
    python scripts/sync_macro_events.py           # 同步所有宏观事件
    python scripts/sync_macro_events.py --predict-only  # 仅推算下一次事件
"""

import sys
import argparse

sys.path.insert(0, "/Users/tencent-code/GitHub/strategy_compass/backend")

from app import create_app
from app.services.macro_event_service import MacroEventService


def main():
    parser = argparse.ArgumentParser(description="Sync macro economic events")
    parser.add_argument(
        "--predict-only",
        action="store_true",
        help="Only generate predictions, skip AKShare sync",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        service = MacroEventService()

        if args.predict_only:
            print("Generating predictions only...")
            count = service._generate_predictions()
            print(f"Generated {count} predicted events")
            return

        print("Syncing macro events from AKShare...")
        stats = service.sync_all()
        print(
            f"Sync done: interest_rate={stats['interest_rate']}, "
            f"economic_data={stats['economic_data']}, predicted={stats['predicted']}"
        )


if __name__ == "__main__":
    main()
