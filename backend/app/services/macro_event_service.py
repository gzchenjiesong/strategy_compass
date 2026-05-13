"""
宏观经济事件同步服务

从 AKShare 拉取央行利率、宏观经济数据，
根据 event_schedule 规则推算下一次事件时间。
"""

import calendar
import logging
from datetime import datetime, timedelta

from app import db
from app.models.data import MacroEvent, EventSchedule

logger = logging.getLogger(__name__)

# AKShare 央行利率接口映射（MVP 仅 4 个利率）
AKSHARE_BANK_RATE_FUNCS = {
    "fed_interest_rate": "macro_bank_usa_interest_rate",
    "china_lpr": "macro_china_lpr",
    "ecb_interest_rate": "macro_bank_euro_interest_rate",
    "boj_interest_rate": "macro_bank_japan_interest_rate",
}


class MacroEventService:
    """宏观经济事件同步服务"""

    def sync_all(self) -> dict:
        """
        同步所有宏观事件：央行利率 + 经济数据 + 推算下一次。

        Returns:
            同步统计 {"interest_rate": x, "predicted": y}
        """
        stats = {"interest_rate": 0, "predicted": 0}

        # 1. 同步央行利率决议（MVP 仅利率，CPI/失业率等由 Agent 扩展负责）
        stats["interest_rate"] = self._sync_interest_rates()

        # 2. 推算并生成下一次事件
        stats["predicted"] = self._generate_predictions()

        logger.info(
            "MacroEvent sync done: interest_rate=%d, predicted=%d",
            stats["interest_rate"],
            stats["predicted"],
        )
        return stats

    def _sync_interest_rates(self) -> int:
        """同步央行利率决议历史数据，返回新增/更新条数。"""
        import akshare as ak

        total = 0
        bank_configs = [
            ("fed_interest_rate", "USA", "美联储利率决议", "macro_bank_usa_interest_rate"),
            ("china_lpr", "CHN", "LPR报价", "macro_china_lpr"),
            ("ecb_interest_rate", "EUR", "欧洲央行利率决议", "macro_bank_euro_interest_rate"),
            ("boj_interest_rate", "JPN", "日本央行利率决议", "macro_bank_japan_interest_rate"),
        ]

        for event_key, country, event_name, func_name in bank_configs:
            try:
                func = getattr(ak, func_name)
                df = func()
                if df is None or df.empty:
                    logger.warning("Empty data for %s", event_name)
                    continue

                count = 0
                for _, row in df.iterrows():
                    event_date = str(row.get("日期", "")).strip()
                    if not event_date or len(event_date) < 6:
                        continue

                    actual = str(row.get("今值", "")).strip() if pd_notna(row.get("今值")) else None
                    forecast = str(row.get("预测值", "")).strip() if pd_notna(row.get("预测值")) else None
                    previous = str(row.get("前值", "")).strip() if pd_notna(row.get("前值")) else None

                    # 跳过实际值为空的记录（数据源未更新或缺失）
                    if not actual or actual.lower() in ("nan", "none", ""):
                        logger.debug("Skip %s on %s: actual_value empty", event_name, event_date)
                        continue

                    # 日期标准化
                    event_date = self._normalize_date(event_date)
                    if not event_date:
                        continue

                    self._upsert_event(
                        event_type="interest_rate",
                        country=country,
                        event_name=event_name,
                        event_date=event_date,
                        actual_value=actual,
                        forecast_value=forecast if forecast else None,
                        previous_value=previous if previous else None,
                        unit="%",
                        is_released=True,
                        source="akshare",
                    )
                    count += 1

                total += count
                logger.info("Synced %d records for %s", count, event_name)

            except Exception as e:
                logger.error("Failed to sync %s: %s", event_name, e)

        return total

    def _generate_predictions(self) -> int:
        """根据 event_schedule 规则推算下一次事件，返回新增/更新条数。"""
        total = 0
        schedules = EventSchedule.query.filter_by(is_active=True).all()

        for sched in schedules:
            try:
                # 获取该事件最新已发布记录
                latest = (
                    MacroEvent.query.filter_by(
                        country=sched.country,
                        event_name=sched.event_name,
                        is_released=True,
                    )
                    .order_by(MacroEvent.event_date.desc())
                    .first()
                )

                if not latest:
                    logger.info("No history for %s, skip prediction", sched.event_name)
                    continue

                next_date = self._calc_next_date(sched.next_calc_rule, latest.event_date)
                if not next_date:
                    logger.warning("Failed to calc next date for %s", sched.event_name)
                    continue

                # 如果推算日期已过去，以今天为基准继续推算
                today = datetime.now().strftime("%Y-%m-%d")
                while next_date and next_date < today:
                    next_date = self._calc_next_date(
                        sched.next_calc_rule, next_date
                    )

                # 获取上一次实际值作为前值（过滤掉 nan 字符串）
                previous_value = latest.actual_value
                if previous_value and str(previous_value).lower() == "nan":
                    previous_value = None

                self._upsert_event(
                    event_type=sched.event_type,
                    country=sched.country,
                    event_name=sched.event_name,
                    event_date=next_date,
                    actual_value=None,
                    forecast_value=None,
                    previous_value=previous_value,
                    unit=latest.unit,
                    is_released=False,
                    source="predicted",
                )
                total += 1
                logger.info(
                    "Predicted next %s on %s (last was %s)",
                    sched.event_name,
                    next_date,
                    latest.event_date,
                )

            except Exception as e:
                logger.error("Failed to predict %s: %s", sched.event_name, e)

        return total

    def _upsert_event(
        self,
        event_type: str,
        country: str,
        event_name: str,
        event_date: str,
        actual_value: str | None = None,
        forecast_value: str | None = None,
        previous_value: str | None = None,
        unit: str | None = None,
        is_released: bool = False,
        source: str = "akshare",
    ) -> None:
        """插入或更新宏观事件记录。"""
        existing = (
            MacroEvent.query.filter_by(
                country=country,
                event_name=event_name,
                event_date=event_date,
            )
            .first()
        )

        if existing:
            # 已存在，更新数值（预测记录可能后续被实际数据覆盖）
            if actual_value is not None:
                existing.actual_value = actual_value
            if forecast_value is not None:
                existing.forecast_value = forecast_value
            if previous_value is not None:
                existing.previous_value = previous_value
            if unit is not None:
                existing.unit = unit
            existing.is_released = is_released
            existing.source = source
            existing.updated_at = db.func.datetime("now")
        else:
            event = MacroEvent(
                event_type=event_type,
                country=country,
                event_name=event_name,
                event_date=event_date,
                actual_value=actual_value,
                forecast_value=forecast_value,
                previous_value=previous_value,
                unit=unit,
                is_released=is_released,
                source=source,
            )
            db.session.add(event)

        db.session.commit()

    def _normalize_date(self, raw: str) -> str | None:
        """将各种日期格式标准化为 YYYY-MM-DD。"""
        raw = str(raw).strip()
        if not raw:
            return None

        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
            "%Y年%m月%d日",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(raw, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # 尝试从更复杂的格式提取
        import re
        m = re.search(r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})", raw)
        if m:
            try:
                dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        logger.warning("Cannot parse date: %s", raw)
        return None

    def _calc_next_date(self, rule: str, last_date: str) -> str | None:
        """根据规则计算下一次事件日期。"""
        try:
            last = datetime.strptime(str(last_date), "%Y-%m-%d")
        except ValueError:
            logger.warning("Invalid last_date: %s", last_date)
            return None

        if rule == "next_fomc_date":
            # FOMC 约每6周（42天）一次，MVP简化：+42天
            next_dt = last + timedelta(days=42)
            return next_dt.strftime("%Y-%m-%d")

        if rule == "next_month_20th":
            # 每月20日
            return self._next_month_day(last, 20)

        if rule == "next_month_mid":
            # 每月中旬（15日）
            return self._next_month_day(last, 15)

        if rule == "next_first_friday":
            # 下个月第一个周五
            return self._next_first_friday(last)

        if rule == "next_ecb_date":
            # 欧洲央行约每6周一次
            next_dt = last + timedelta(days=42)
            return next_dt.strftime("%Y-%m-%d")

        if rule == "next_boe_date":
            # 英国央行约每6周一次
            next_dt = last + timedelta(days=42)
            return next_dt.strftime("%Y-%m-%d")

        if rule == "next_boj_date":
            # 日本央行约每6周一次
            next_dt = last + timedelta(days=42)
            return next_dt.strftime("%Y-%m-%d")

        logger.warning("Unknown calc rule: %s", rule)
        return None

    def _next_month_day(self, last: datetime, day: int) -> str:
        """计算下个月的指定日期。"""
        year = last.year
        month = last.month + 1
        if month > 12:
            month = 1
            year += 1
        # 处理月末（如2月没有30日）
        last_day = calendar.monthrange(year, month)[1]
        day = min(day, last_day)
        return datetime(year, month, day).strftime("%Y-%m-%d")

    def _next_first_friday(self, last: datetime) -> str:
        """计算下个月第一个周五。"""
        year = last.year
        month = last.month + 1
        if month > 12:
            month = 1
            year += 1

        # 找第一个周五
        for day in range(1, 8):
            dt = datetime(year, month, day)
            if dt.weekday() == 4:  # Friday
                return dt.strftime("%Y-%m-%d")

        return datetime(year, month, 7).strftime("%Y-%m-%d")  # fallback


def pd_notna(value) -> bool:
    """兼容 pandas 的 notna 判断。"""
    try:
        import pandas as pd
        return pd.notna(value)
    except ImportError:
        return value is not None and str(value) != "nan"
