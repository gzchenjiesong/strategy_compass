---
title: "Module 2: 新闻聚合 — 接口与业务逻辑设计"
type: spec
module: module-2
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

## 3. 核心业务逻辑

### 3.1 新闻加工流程

Module 1 每 30 分钟拉取新闻并写入 `news_raw` 表。Module 2 查询时进行实时加工：

```python
class NewsService:

    def get_news_list(self, user_id: int, filter_type: str = "all",
                      limit: int = 30, before_id: int = None) -> dict:
        """
        获取新闻列表。
        
        1. 从 Module 1 查询 news_raw
        2. 应用过滤条件
        3. 生成分类标签和摘要
        4. 返回前端格式
        """
        # 1. 构建查询
        query = self._build_query(filter_type, before_id)

        # 2. 获取用户关注标的（用于关联匹配）
        if filter_type == "related":
            watchlist = self._get_user_watchlist(user_id)
            # 关联过滤在查询时应用
            query = self._apply_related_filter(query, watchlist)

        # 3. 执行查询
        news_items = query.order_by(desc("id")).limit(limit).all()

        # 4. 加工为前端格式
        items = []
        for item in news_items:
            processed = {
                "id": item.id,
                "source": item.source,
                "title": item.title,
                "summary": self._generate_summary(item.content),
                "important": bool(item.important),
                "related": self._check_related(item, user_id),
                "tags": json.loads(item.tags) if item.tags else [],
                "publish_time": item.publish_time,
                "time_ago": self._format_time_ago(item.publish_time)
            }
            items.append(processed)

        return {
            "items": items,
            "has_more": len(items) == limit,
            "next_before_id": items[-1]["id"] if items else None
        }

    def get_news_detail(self, news_id: int, user_id: int) -> dict:
        """获取新闻详情。"""
        item = NewsRaw.query.get(news_id)
        if not item:
            raise NotFound("NEWS_NOT_FOUND")

        return {
            "id": item.id,
            "source": item.source,
            "source_id": item.source_id,
            "title": item.title,
            "content": item.content,
            "important": bool(item.important),
            "related": self._check_related(item, user_id),
            "related_symbols": self._extract_related_symbols(item),
            "tags": json.loads(item.tags) if item.tags else [],
            "publish_time": item.publish_time,
            "time_ago": self._format_time_ago(item.publish_time)
        }
```

### 3.2 关联标的匹配

MVP 阶段采用**简单关键词匹配**：

```python
def _check_related(self, news_item: NewsRaw, user_id: int) -> bool:
    """
    检查新闻是否关联用户关注的标的。
    MVP 阶段：关键词匹配（标的名称出现在新闻标题或内容中）。
    """
    # 获取用户关注标的
    watchlist = self._get_user_watchlist(user_id)
    if not watchlist:
        return False

    # 构建关键词集合（标的名称）
    keywords = {item.name for item in watchlist}

    # 在标题和内容中匹配
    text = f"{news_item.title} {news_item.content}"
    return any(keyword in text for keyword in keywords)


def _extract_related_symbols(self, news_item: NewsRaw) -> list[str]:
    """
    提取新闻关联的标的代码列表。
    MVP 阶段：简单关键词匹配。
    未来：NLP 实体识别。
    """
    # 从全量标的中匹配
    all_symbols = self._get_all_symbols()
    text = f"{news_item.title} {news_item.content}"

    related = []
    for symbol, name in all_symbols.items():
        if name in text:
            related.append(symbol)

    return related[:5]  # 最多返回 5 个关联标的
```

**匹配规则：**

| 规则 | 说明 |
|------|------|
| 匹配范围 | 新闻标题 + 内容全文 |
| 匹配关键词 | 标的名称（如"贵州茅台"、"小米集团"） |
| 优先级 | 标题匹配 > 内容匹配 |
| 结果限制 | 最多返回 5 个关联标的 |

> **注意：** MVP 阶段的关联匹配是简化实现，可能出现误匹配（如"小米"匹配到"小米集团"和"小米产业链"）。未来通过 NLP 实体识别提升精度。

### 3.3 摘要生成

```python
def _generate_summary(self, content: str, max_length: int = 50) -> str:
    """生成新闻摘要，截取前 N 个字符。"""
    if not content:
        return ""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."
```

### 3.4 相对时间格式化

```python
def _format_time_ago(self, publish_time: str) -> str:
    """将发布时间格式化为相对时间（中文）。"""
    dt = parse_iso_datetime(publish_time)
    now = datetime.now(timezone.utc)
    delta = now - dt

    if delta < timedelta(minutes=1):
        return "刚刚"
    elif delta < timedelta(hours=1):
        return f"{delta.seconds // 60}分钟前"
    elif delta < timedelta(days=1):
        return f"{delta.seconds // 3600}小时前"
    else:
        return f"{delta.days}天前"
```

### 3.5 分页策略

采用**游标分页**（Cursor-based Pagination）：

```python
# 请求第一页
GET /api/v2/news?filter=all&limit=30

# 请求下一页
GET /api/v2/news?filter=all&limit=30&before_id=12340
```

**优点：**
- 新闻按时间倒序，id 自增，游标分页性能优于 offset
- 避免高并发时数据漂移（新数据插入导致 offset 偏移）

