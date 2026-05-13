import re
import json
import html
import logging
from datetime import datetime, timedelta

import requests

from app import db
from app.models.data import NewsRaw

logger = logging.getLogger(__name__)

JIN10_FLASH_URL = "https://www.jin10.com/flash_newest.js"

# 频道映射（基于金十数据 channel 字段）
CHANNEL_MAP = {
    1: "domestic",      # 国内
    2: "international", # 国际
    3: "macro",         # 宏观/债券
    5: "forex",         # 外汇/期货
}


class Jin10Service:
    def fetch_flash(self) -> list[dict]:
        """从金十数据获取最新快讯列表"""
        try:
            resp = requests.get(
                JIN10_FLASH_URL,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Referer": "https://www.jin10.com/",
                },
                timeout=15,
            )
            resp.raise_for_status()
            return self._parse_js_response(resp.text)
        except requests.RequestException as e:
            logger.error("Failed to fetch jin10 flash: %s", e)
            return []

    def _parse_js_response(self, text: str) -> list[dict]:
        """解析 JavaScript 变量格式的响应"""
        match = re.search(r"var newest\s*=\s*(\[.*?\]);", text, re.DOTALL)
        if not match:
            logger.warning("Cannot parse jin10 response: no 'var newest' found")
            return []
        try:
            items = json.loads(match.group(1))
            return [self._normalize_item(item) for item in items if item]
        except json.JSONDecodeError as e:
            logger.error("Failed to parse jin10 JSON: %s", e)
            return []

    def _normalize_item(self, raw: dict) -> dict:
        """将金十原始数据归一化为内部格式"""
        data = raw.get("data", {})
        content = data.get("content", "")
        # 清洗 HTML 标签
        content = self._clean_html(content)
        # 重要性映射：金十 0/1 -> 内部 1/3
        important = raw.get("important", 0)
        importance = 3 if important else 1

        # 频道标签
        channels = raw.get("channel", [])
        tags = [CHANNEL_MAP.get(c, str(c)) for c in channels]

        return {
            "source_id": str(raw.get("id", "")),
            "publish_time": raw.get("time", ""),
            "title": content,
            "content": content,
            "url": data.get("source_link", ""),
            "importance": importance,
            "tags": json.dumps(tags, ensure_ascii=False),
            "source": "jin10",
            "raw_data": json.dumps(raw, ensure_ascii=False),
        }

    def _clean_html(self, text: str) -> str:
        """去除简单 HTML 标签并解码实体"""
        if not text:
            return ""
        # 去除 <b>, <i>, <br> 等常见标签
        text = re.sub(r"<[^>]+>", "", text)
        # 解码 HTML 实体
        text = html.unescape(text)
        return text.strip()

    def sync_to_db(self, items: list[dict]) -> tuple[int, int]:
        """
        将快讯同步到数据库，返回 (新增条数, 重复条数)
        """
        if not items:
            return 0, 0

        new_count = 0
        dup_count = 0

        # 批量查询已有 source_id
        source_ids = [item["source_id"] for item in items]
        existing = {
            r[0] for r in db.session.query(NewsRaw.source_id)
            .filter(NewsRaw.source_id.in_(source_ids))
            .all()
        }

        for item in items:
            if item["source_id"] in existing:
                dup_count += 1
                continue

            news = NewsRaw(
                source=item["source"],
                source_id=item["source_id"],
                title=item["title"],
                content=item["content"],
                url=item["url"] or None,
                publish_time=item["publish_time"],
                importance=item["importance"],
            )
            db.session.add(news)
            new_count += 1

        if new_count > 0:
            db.session.commit()
            logger.info("Jin10 sync: %d new, %d duplicate", new_count, dup_count)

        return new_count, dup_count

    def cleanup_old(self, hours: int = 72) -> int:
        """清理指定小时数之前的数据"""
        cutoff = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")

        result = (
            db.session.query(NewsRaw)
            .filter(NewsRaw.publish_time < cutoff_str)
            .delete(synchronize_session=False)
        )
        db.session.commit()
        if result:
            logger.info("Cleaned up %d old news items (before %s)", result, cutoff_str)
        return result
