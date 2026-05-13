---
title: "Module 0: 用户系统 — 接口与数据模型设计"
type: spec
module: module-0
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

## 3. API 接口定义

### 认证相关

#### POST /api/v1/auth/wechat/callback

微信授权回调，处理登录逻辑。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 微信授权临时 code |
| invitation_code | string | 否 | 新用户注册时传入 |

**响应（已注册用户）：**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "nickname": "张三",
    "avatar_url": "https://...",
    "created_at": "2026-05-01T10:00:00Z"
  }
}
```

**响应（新用户，未传邀请码）：**

```json
{
  "status": "need_invitation_code",
  "openid": "oXXX",  // 前端缓存，绑定时传回
  "nickname": "微信用户",
  "avatar_url": "https://..."
}
```

**错误码：**

| code | 含义 |
|------|------|
| `INVALID_CODE` | 微信授权 code 无效或已过期 |
| `INVALID_INVITATION_CODE` | 邀请码不存在或已用完 |
| `BIND_FAILED` | 绑定失败（可能是 openid 已关联其他用户） |

#### POST /api/v1/auth/wechat/bind

新用户使用邀请码完成注册。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| openid | string | 是 | 微信 openid（从回调接口获取） |
| nickname | string | 否 | 用户昵称 |
| avatar_url | string | 否 | 头像 URL |
| invitation_code | string | 是 | 邀请码 |

**响应：** 同 wechat/callback 成功响应

#### GET /api/v1/auth/me

获取当前登录用户信息。

**Headers：** `Authorization: Bearer <token>`

**响应：**

```json
{
  "id": 1,
  "openid": "oXXX",
  "nickname": "张三",
  "avatar_url": "https://...",
  "status": "active",
  "created_at": "2026-05-01T10:00:00Z",
  "last_login_at": "2026-05-07T09:30:00Z"
}
```

---

### 用户信息

#### GET /api/v1/users/me

获取当前用户详细信息（包含偏好设置摘要）。

**响应：**

```json
{
  "id": 1,
  "nickname": "张三",
  "avatar_url": "https://...",
  "status": "active",
  "created_at": "2026-05-01T10:00:00Z",
  "last_login_at": "2026-05-07T09:30:00Z",
  "watchlist_count": 3,
  "preferences": {
    "theme": "light",
    "default_market": "A",
    "home_widgets": ["index_quote", "temperature", "watchlist"]
  }
}
```

#### PATCH /api/v1/users/me

更新用户信息。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| nickname | string | 否 | 修改昵称 |

---

### 偏好设置

#### GET /api/v1/users/me/preferences

获取全部偏好设置。

**响应：**

```json
{
  "theme": "light",
  "default_market": "A",
  "home_widgets": ["index_quote", "temperature", "watchlist"],
  "valuation_default_period": "10y",
  "notification_enabled": true
}
```

#### PUT /api/v1/users/me/preferences

批量更新偏好设置（覆盖模式）。

**请求体：**

```json
{
  "theme": "dark",
  "default_market": "A"
}
```

**响应：** 返回更新后的完整偏好对象

#### GET /api/v1/users/me/preferences/:key

获取单个偏好。

#### PUT /api/v1/users/me/preferences/:key

设置单个偏好。

**请求体：**

```json
{
  "value": "dark"
}
```

---

### 自选股（Watchlist）

#### GET /api/v1/watchlists

获取当前用户所有自选列表。

**响应：**

```json
{
  "items": [
    {
      "id": 1,
      "name": "默认自选",
      "item_count": 12,
      "sort_order": 0,
      "created_at": "2026-05-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "港股关注",
      "item_count": 5,
      "sort_order": 1,
      "created_at": "2026-05-03T14:00:00Z"
    }
  ]
}
```

#### POST /api/v1/watchlists

创建新的自选列表。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 列表名称（≤20 字符） |

**响应：** 返回新建的 watchlist 对象

#### PATCH /api/v1/watchlists/:id

修改自选列表。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 新名称 |
| sort_order | integer | 否 | 排序位置 |

#### DELETE /api/v1/watchlists/:id

删除自选列表（同时删除所有 items）。

**限制：** 至少保留一个自选列表，不允许删除最后一个。

---

### 自选股项（Watchlist Item）

#### GET /api/v1/watchlists/:id/items

获取自选列表中的所有标的。

**响应：**

```json
{
  "watchlist_id": 1,
  "items": [
    {
      "id": 1,
      "symbol": "600519",
      "name": "贵州茅台",
      "market": "A",
      "sort_order": 0,
      "added_at": "2026-05-01T10:00:00Z"
    }
  ]
}
```

#### POST /api/v1/watchlists/:id/items

添加标的到自选列表。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| symbol | string | 是 | 股票/基金代码 |
| name | string | 是 | 标的名称 |
| market | string | 是 | 市场类型 (A/HK/US) |

**错误码：**

| code | 含义 |
|------|------|
| `DUPLICATE_ITEM` | 该标的已在列表中 |
| `WATCHLIST_NOT_FOUND` | 列表不存在 |
| `ITEM_LIMIT_EXCEEDED` | 超过单列表最大数量（100） |

#### PUT /api/v1/watchlists/:id/items/reorder

批量更新排序。

**请求体：**

```json
{
  "order": [3, 1, 2]  // item_id 数组，按新顺序排列
}
```

#### DELETE /api/v1/watchlists/:id/items/:itemId

从自选列表移除标的。

---

### 行业/概念板块关注（Sector Favorites）

> 独立于自选股（Watchlist）。自选股管理个股/基金标的，板块关注管理行业/概念板块（如半导体、新能源、化工）。
> 两者数据源不同，下游消费者也不同：自选股服务于 Module 6（个股基金详情），板块关注服务于 Module 5（板块概念）。

#### GET /api/v1/sectors/favorites

获取当前用户关注的所有行业/概念板块。

**响应：**

```json
{
  "items": [
    {
      "id": 1,
      "sector_code": "BK0477",
      "sector_name": "半导体",
      "sector_type": "industry",
      "sort_order": 0,
      "added_at": "2026-05-07T10:00:00Z"
    },
    {
      "id": 2,
      "sector_code": "BK0478",
      "sector_name": "新能源",
      "sector_type": "concept",
      "sort_order": 1,
      "added_at": "2026-05-07T10:00:00Z"
    }
  ]
}
```

#### POST /api/v1/sectors/favorites

添加行业/概念板块到关注列表。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sector_code | string | 是 | 板块代码（如 `BK0477`） |
| sector_name | string | 是 | 板块名称 |
| sector_type | string | 是 | 类型：`industry`（行业）/ `concept`（概念） |

**错误码：**

| code | 含义 |
|------|------|
| `DUPLICATE_SECTOR` | 该板块已在关注列表中 |
| `SECTOR_LIMIT_EXCEEDED` | 超过关注上限（50 个） |

#### PUT /api/v1/sectors/favorites/reorder

批量更新板块关注排序。

**请求体：**

```json
{
  "order": [3, 1, 2]  // favorite_id 数组，按新顺序排列
}
```

#### DELETE /api/v1/sectors/favorites/:id

取消关注某板块。

