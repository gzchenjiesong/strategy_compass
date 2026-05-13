#!/usr/bin/env python3
"""
金十数据快讯同步脚本
用法:
    python scripts/sync_jin10_news.py           # 同步最新快讯
    python scripts/sync_jin10_news.py --cleanup # 同步并清理 72h 前旧数据
"""

import sys
import argparse

sys.path.insert(0, "/Users/tencent-code/GitHub/strategy_compass/backend")

from app import create_app
from app.services.jin10_service import Jin10Service


def main():
    parser = argparse.ArgumentParser(description="Sync Jin10 flash news")
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Cleanup news older than 72 hours after sync",
    )
    parser.add_argument(
        "--cleanup-only",
        action="store_true",
        help="Only cleanup old news, do not sync",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        service = Jin10Service()

        if args.cleanup_only:
            deleted = service.cleanup_old(72)
            print(f"Cleaned up {deleted} old news items")
            return

        print("Fetching jin10 flash news...")
        items = service.fetch_flash()
        print(f"Fetched {len(items)} items from jin10")

        if items:
            new_count, dup_count = service.sync_to_db(items)
            print(f"Sync result: {new_count} new, {dup_count} duplicate")
        else:
            print("No items fetched, skip sync")

        if args.cleanup:
            deleted = service.cleanup_old(72)
            print(f"Cleaned up {deleted} old news items")


if __name__ == "__main__":
    main()
