---
title: "Module 2: 新闻聚合 — 接口与业务逻辑设计"
type: spec
module: module-2
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

# Module 2: 新闻聚合

> 前置文档：
> - `docs/modules/module-1-data-service.md`（新闻原始数据获取）
>
> 本文档聚焦：Module 2 的接口定义 + 新闻加工逻辑 + 与上下游的契约。
>
> **核心定位：** Module 2 是应用层的新闻加工与展示模块，从 Module 1 获取原始新闻数据，进行清洗、分类、关联匹配，为前端提供过滤查询和详情展示能力。

## 1. 职责边界

**做：**
- 新闻数据加工（去重、格式化、摘要生成）
- 新闻分类标签（普通/重要/关联）
- 关联标的匹配（用户关注标的与新闻的关联）
- 新闻列表过滤查询（全部/普通/重要/关联）
- 新闻详情展示

**不做：**
- 新闻数据获取（归 Module 1）
- 新闻情绪分析/NLP（MVP 后置）
- 用户关注管理（归 Module 0）
- 数据持久化（复用 Module 1 的 news_raw 表，不新建表）

**核心约束：** 新闻加工唯一出口 — 所有新闻展示相关的过滤、分类、关联逻辑通过 Module 2 提供。

## 2. API 接口定义

> 所有接口需通过 `@auth_required` 认证（依赖 Module 0）。
> Module 2 直接暴露给前端，是前端新闻页面的唯一数据来源。

### 2.1 新闻列表

#### GET /api/v2/news

获取新闻列表，支持按标签过滤。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filter | string | 否 | 过滤标签：`all`（默认）/ `normal` / `important` / `related` |
| limit | integer | 否 | 返回数量，默认 30，最大 100 |
| before_id | integer | 否 | 分页游标，返回 id < before_id 的新闻 |

**响应：**

```json
{
  "items": [
    {
      "id": 12345,
      "source": "jin10",
      "title": "美联储主席鲍威尔发表讲话",
      "summary": "美联储主席鲍威尔表示...",
      "important": true,
      "related": false,
      "tags": ["美联储", "利率"],
      "publish_time": "2026-05-07T08:30:00Z",
      "time_ago": "10分钟前"
    }
  ],
  "has_more": true,
  "next_before_id": 12340
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `summary` | 内容前 50 字摘要 |
| `important` | 是否重要快讯（来自 Module 1 原始数据） |
| `related` | 是否关联用户关注标的 |
| `time_ago` | 相对时间（中文，如"10分钟前"） |
| `has_more` | 是否有更多数据 |
| `next_before_id` | 下一页游标 |

**过滤规则：**

| filter 值 | 说明 |
|-----------|------|
| `all` | 返回全部新闻（按时间倒序） |
| `normal` | 只返回普通新闻（`important = false`） |
| `important` | 只返回重要新闻（`important = true`） |
| `related` | 只返回关联用户关注标的的新闻 |

---

### 2.2 新闻详情

#### GET /api/v2/news/:id

获取单条新闻的完整内容。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 新闻 ID |

**响应：**

```json
{
  "id": 12345,
  "source": "jin10",
  "source_id": "j10_20260507_001",
  "title": "美联储主席鲍威尔发表讲话",
  "content": "美联储主席鲍威尔在今日的新闻发布会上表示...",
  "important": true,
  "related": false,
  "related_symbols": [],
  "tags": ["美联储", "利率"],
  "publish_time": "2026-05-07T08:30:00Z",
  "time_ago": "10分钟前"
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `content` | 完整内容 |
| `related_symbols` | 关联的标的代码列表（MVP 阶段可能为空） |

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

## 4. 与上下游模块的接口契约

### 4.1 依赖的上游模块

| 上游模块 | 依赖内容 | 调用方式 | 用途 |
|---------|---------|---------|------|
| Module 0 用户系统 | `@auth_required` 认证 | 装饰器 | 接口鉴权 |
| Module 0 用户系统 | 用户关注列表 | 内部调用 | 关联新闻匹配 |
| Module 1 数据底座 | `news_raw` 表 | 直接查询 | 新闻原始数据 |

### 4.2 对下游暴露的能力

| 消费者 | 调用的 API | 用途 |
|--------|-----------|------|
| 前端新闻页面 | GET /api/v2/news | 新闻列表展示 |
| 前端新闻页面 | GET /api/v2/news/:id | 新闻详情弹窗 |
| Module 3 市场概览 | GET /api/v2/news?filter=important&limit=5 | 首页重要快讯 |

## 5. 错误处理

### 统一错误响应格式

```json
{
  "error": {
    "code": "NEWS_NOT_FOUND",
    "message": "新闻不存在"
  }
}
```

### Module 2 错误码清单

| HTTP 状态码 | 错误码 | 说明 |
|-------------|--------|------|
| 401 | UNAUTHORIZED | 未提供 Token |
| 404 | NEWS_NOT_FOUND | 新闻 ID 不存在 |
| 400 | INVALID_FILTER | 过滤参数无效 |

## 6. 性能考虑

| 优化点 | 实现方式 | 说明 |
|--------|---------|------|
| 新闻列表查询 | `news_raw` 表按 `publish_time` 索引 | 倒序查询性能 |
| 关联匹配 | 用户关注标的缓存 | 减少重复查询用户关注列表 |
| 摘要生成 | 实时截取，不存储 | 减少存储冗余 |
| 分页 | 游标分页 | 避免 OFFSET 性能问题 |

## 7. 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 不新建新闻表 | 复用 Module 1 的 `news_raw` | 避免数据冗余，Module 2 只做加工 |
| 关联匹配用关键词 | MVP 简化实现 | NLP 实体识别开发成本高，后续迭代 |
| 游标分页 | `before_id` 游标 | 新闻按时间倒序，id 自增，游标分页最适合 |
| 摘要实时生成 | 不存储摘要字段 | 摘要简单，实时截取即可 |
| 相对时间服务端生成 | `time_ago` 字段 | 避免前端处理时区问题 |
| 关联过滤在服务端 | 非前端过滤 | 减少数据传输，保护用户隐私 |

## 8. 未来扩展（非 MVP）

| 功能 | 说明 |
|------|------|
| NLP 实体识别 | 用模型提取新闻中的公司/人名/事件，替代关键词匹配 |
| 新闻情绪分析 | 给新闻打上正面/负面/中性标签 |
| 新闻与标的深度关联 | 关联到具体业务事件（财报、产品发布、诉讼等） |
| 新闻推送 | 重要关联新闻实时推送给用户 |
| 多源新闻聚合 | 接入财联社、华尔街见闻等来源 |
