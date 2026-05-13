---
title: "Module 2: 新闻聚合 — 接口与业务逻辑设计"
type: spec
module: module-2
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

## 2. API 接口定义

> 所有接口需通过 `@auth_required` 认证（依赖 Module 0）。
> Module 2 直接暴露给前端，是前端新闻页面的唯一数据来源。

### 2.1 新闻列表

#### GET /api/v2/news

获取新闻列表，支持按标签过滤。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filter | string | 否 | 过滤标签：`all`（默认）/ `normal` / `important` / `macro` / `related` |
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
| `macro` | 只返回宏观经济事件（央行利率决议、经济数据发布等） |
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

