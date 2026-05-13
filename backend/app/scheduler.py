import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def register_jobs(app):
    """注册定时任务"""

    def sync_jin10_news():
        with app.app_context():
            from app.services.jin10_service import Jin10Service
            service = Jin10Service()
            try:
                items = service.fetch_flash()
                if items:
                    new_count, dup_count = service.sync_to_db(items)
                    logger.info("Scheduled jin10 sync: %d new, %d duplicate", new_count, dup_count)
            except Exception as e:
                logger.error("Scheduled jin10 sync failed: %s", e)

    def cleanup_old_news():
        with app.app_context():
            from app.services.jin10_service import Jin10Service
            service = Jin10Service()
            try:
                deleted = service.cleanup_old(72)
                logger.info("Scheduled cleanup: %d old news deleted", deleted)
            except Exception as e:
                logger.error("Scheduled cleanup failed: %s", e)

    # 每 5 分钟同步一次快讯
    scheduler.add_job(
        sync_jin10_news,
        trigger=IntervalTrigger(minutes=5),
        id="sync_jin10_news",
        name="Sync Jin10 Flash News",
        replace_existing=True,
    )

    # 每小时清理一次 72h 前的旧数据
    scheduler.add_job(
        cleanup_old_news,
        trigger=IntervalTrigger(hours=1),
        id="cleanup_old_news",
        name="Cleanup Old News",
        replace_existing=True,
    )

    # 每日 08:00 同步宏观利率数据（中美日欧 4 个央行）
    def sync_macro_events():
        with app.app_context():
            from app.services.macro_event_service import MacroEventService
            service = MacroEventService()
            try:
                stats = service.sync_all()
                logger.info("Scheduled macro sync: %s", stats)
            except Exception as e:
                logger.error("Scheduled macro sync failed: %s", e)

    scheduler.add_job(
        sync_macro_events,
        trigger=CronTrigger(hour=8, minute=0),
        id="sync_macro_events",
        name="Sync Interest Rates (Daily 08:00)",
        replace_existing=True,
    )

    logger.info("Scheduler jobs registered: sync_jin10_news (every 5min), cleanup_old_news (every 1h), macro_sync (daily 08:00)")


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Background scheduler started")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler shutdown")
