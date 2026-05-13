from app import db
from app.models.data import NewsRaw, MacroEvent
from app.utils.exceptions import DataNotReady


class NewsService:
    VALID_FILTERS = {"all", "normal", "important", "macro", "related"}

    def get_news(self, limit=30, before_id=None, filter_type="all"):
        """
        获取新闻列表，支持 filter 过滤和宏观事件混合。

        :param filter_type: all | normal | important | macro | related
        """
        if filter_type not in self.VALID_FILTERS:
            filter_type = "all"

        if filter_type == "macro":
            return self._get_macro_events(limit)

        if filter_type == "all":
            return self._get_mixed_timeline(limit, before_id)

        # 原有新闻逻辑
        query = NewsRaw.query.order_by(NewsRaw.publish_time.desc())

        if filter_type == "normal":
            query = query.filter(NewsRaw.importance < 3)
        elif filter_type == "important":
            query = query.filter(NewsRaw.importance >= 3)

        if before_id:
            ref = NewsRaw.query.get(before_id)
            if ref:
                query = query.filter(NewsRaw.publish_time < ref.publish_time)

        rows = query.limit(limit).all()
        if not rows:
            raise DataNotReady()

        items = [self._format_news_item(r) for r in rows]
        has_more = len(rows) >= limit
        next_before_id = rows[-1].id if rows else None

        return {
            "items": items,
            "has_more": has_more,
            "next_before_id": next_before_id,
        }

    def _get_macro_events(self, limit=30) -> dict:
        """
        获取精简宏观事件列表。
        每个 (country, event_name) 组合只保留：
        - 最新已发布记录（含实际值/预测值/前值）
        - 下一条预计发布时间
        """
        from sqlalchemy import func

        # 1. 找出每个组合最新且有实际值的已发布记录
        # 过滤掉 actual_value 为空 / 'nan' / '' 的记录
        latest_released_subq = (
            db.session.query(
                MacroEvent.country,
                MacroEvent.event_name,
                func.max(MacroEvent.event_date).label("max_date"),
            )
            .filter(
                MacroEvent.is_released == True,
                MacroEvent.actual_value.isnot(None),
                MacroEvent.actual_value != "",
                MacroEvent.actual_value != "nan",
                MacroEvent.actual_value != "NaN",
            )
            .group_by(MacroEvent.country, MacroEvent.event_name)
            .subquery()
        )

        latest_released = (
            MacroEvent.query
            .join(
                latest_released_subq,
                (MacroEvent.country == latest_released_subq.c.country)
                & (MacroEvent.event_name == latest_released_subq.c.event_name)
                & (MacroEvent.event_date == latest_released_subq.c.max_date),
            )
            .filter(
                MacroEvent.is_released == True,
                MacroEvent.actual_value.isnot(None),
                MacroEvent.actual_value != "",
                MacroEvent.actual_value != "nan",
                MacroEvent.actual_value != "NaN",
            )
            .all()
        )

        # 2. 找出每个组合最近的预计记录
        next_predicted_subq = (
            db.session.query(
                MacroEvent.country,
                MacroEvent.event_name,
                func.min(MacroEvent.event_date).label("min_date"),
            )
            .filter(MacroEvent.is_released == False)
            .group_by(MacroEvent.country, MacroEvent.event_name)
            .subquery()
        )

        next_predicted = (
            MacroEvent.query
            .join(
                next_predicted_subq,
                (MacroEvent.country == next_predicted_subq.c.country)
                & (MacroEvent.event_name == next_predicted_subq.c.event_name)
                & (MacroEvent.event_date == next_predicted_subq.c.min_date),
            )
            .filter(MacroEvent.is_released == False)
            .all()
        )

        # 3. 合并并排序：未发布的在前（按日期升序），已发布的在后（按日期降序）
        all_items = []
        for r in latest_released:
            all_items.append(self._format_macro_item(r))
        for r in next_predicted:
            all_items.append(self._format_macro_item(r))

        unreleased = [i for i in all_items if not i.get("is_released")]
        released = [i for i in all_items if i.get("is_released")]

        unreleased.sort(key=lambda x: x.get("event_date", ""))
        released.sort(key=lambda x: x.get("event_date", ""), reverse=True)

        items = (unreleased + released)[:limit]
        has_more = len(items) >= limit

        return {
            "items": items,
            "has_more": has_more,
            "next_before_id": None,
        }

    def _get_mixed_timeline(self, limit=30, before_id=None) -> dict:
        """
        只返回新闻资讯，不混入宏观事件。
        '全部'标签仅包含全部资讯内容。
        """
        query = NewsRaw.query.order_by(NewsRaw.publish_time.desc())

        if before_id:
            ref = NewsRaw.query.get(before_id)
            if ref:
                query = query.filter(NewsRaw.publish_time < ref.publish_time)

        rows = query.limit(limit).all()
        items = [self._format_news_item(r) for r in rows]
        has_more = len(rows) >= limit
        next_before_id = rows[-1].id if rows else None

        return {
            "items": items,
            "has_more": has_more,
            "next_before_id": next_before_id,
        }

    def get_macro_events(self, limit=30, country=None, upcoming=None):
        """
        获取宏观事件列表（独立接口）。

        :param country: 国家过滤
        :param upcoming: 是否只返回未发布事件
        """
        query = MacroEvent.query

        if country:
            query = query.filter(MacroEvent.country == country.upper())

        if upcoming:
            query = query.filter(MacroEvent.is_released == False)

        rows = (
            query.order_by(
                MacroEvent.is_released.asc(),
                MacroEvent.event_date.desc(),
            )
            .limit(limit)
            .all()
        )

        items = [self._format_macro_item(r) for r in rows]
        return {
            "items": items,
            "has_more": len(rows) >= limit,
            "next_before_id": None,
        }

    def _format_news_item(self, r: NewsRaw) -> dict:
        """将 NewsRaw 格式化为前端需要的格式。"""
        return {
            "id": f"news_{r.id}",
            "type": "news",
            "source": r.source,
            "title": r.title,
            "content": r.content,
            "url": r.url,
            "publish_time": r.publish_time,
            "event_date": r.publish_time,
            "importance": r.importance,
            "is_released": True,
            "is_macro": False,
        }

    def _format_macro_item(self, r: MacroEvent) -> dict:
        """将 MacroEvent 格式化为前端需要的格式。"""
        if r.is_released:
            title = f"[最新发布] {r.event_name}"
        else:
            title = f"[预计发布] {r.event_date} {r.event_name}"

        return {
            "id": f"macro_{r.id}",
            "type": "macro",
            "source": r.source,
            "title": title,
            "event_name": r.event_name,
            "country": r.country,
            "event_type": r.event_type,
            "event_date": r.event_date,
            "actual_value": r.actual_value,
            "forecast_value": r.forecast_value,
            "previous_value": r.previous_value,
            "unit": r.unit,
            "publish_time": r.event_date,
            "is_released": r.is_released,
            "is_macro": True,
        }

    def get_important_news(self, limit=10):
        """获取重要快讯（importance >= 3）"""
        return self.get_news(limit=limit, filter_type="important")

    def get_stats(self):
        """获取新闻统计"""
        from sqlalchemy import func

        total = NewsRaw.query.count()
        today = db.func.date("now")
        today_count = (
            NewsRaw.query.filter(db.func.date(NewsRaw.publish_time) == today)
            .count()
        )
        important_count = (
            NewsRaw.query.filter(NewsRaw.importance >= 3).count()
        )
        # 宏观统计：有有效数据的指标组合数（每个组合展示最新已发布+预计）
        macro_count = (
            db.session.query(MacroEvent.country, MacroEvent.event_name)
            .group_by(MacroEvent.country, MacroEvent.event_name)
            .count()
        )
        return {
            "total": total,
            "today": today_count,
            "important": important_count,
            "macro": macro_count,
        }
