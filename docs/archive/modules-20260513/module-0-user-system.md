---
title: "Module 0: 用户系统 — 接口与数据模型设计"
type: spec
module: module-0
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

# Module 0: 用户系统

## 1. 职责边界

**做：**
- 微信 OAuth 登录认证（仅支持微信，不引入其他第三方平台）
- 邀请码注册校验
- 用户基本信息管理
- JWT Token 签发与验证（7 天有效期，无 refresh token）
- 用户自选股（Watchlist）管理（个股/基金，单列表上限 100）
- 用户行业/概念板块关注管理（独立于自选股，独立数据源）
- 用户偏好设置管理

**不做：**
- 角色权限管理（MVP 只有一种用户角色）
- 管理后台（邀请码直接操作数据库，管理后台作为未来扩展模块）
- 微信消息推送（归 Module 7）
- 用户行为分析 / 埋点

## 2. 认证流程

### 2.1 登录时序

```
用户               前端                后端                 微信
 │                  │                   │                    │
 │  点击微信登录     │                   │                    │
 │─────────────────>│                   │                    │
 │                  │  重定向到微信授权   │                    │
 │                  │────────────────────────────────────────>│
 │                  │                   │                    │
 │  扫码/确认授权    │                   │                    │
 │<──────────────────────────────────────────────────────────│
 │                  │                   │                    │
 │                  │  回调 /auth/wechat/callback?code=xxx    │
 │                  │──────────────────>│                    │
 │                  │                   │  用 code 换 token   │
 │                  │                   │───────────────────>│
 │                  │                   │  access_token +    │
 │                  │                   │  openid + unionid  │
 │                  │                   │<───────────────────│
 │                  │                   │                    │
 │                  │                   │  查 unionid        │
 │                  │                   │  ├── 已注册 → 签发 JWT
 │                  │                   │  └── 新用户 → 返回
 │                  │                   │      {status:      │
 │                  │                   │       "need_code"} │
 │                  │<──────────────────│                    │
 │                  │                   │                    │
 │  [新用户]         │                   │                    │
 │  输入邀请码       │                   │                    │
 │─────────────────>│  POST /auth/bind  │                    │
 │                  │──────────────────>│                    │
 │                  │                   │  验证邀请码         │
 │                  │                   │  创建用户           │
 │                  │                   │  签发 JWT           │
 │                  │<──────────────────│                    │
 │  登录成功 🎉      │                   │                    │
```

### 2.2 后续请求认证

```
客户端                         后端
 │  Authorization: Bearer <JWT>
 │─────────────────────────────>│
 │                               │  验证签名 + 过期时间
 │                               │  注入 user_id 到请求上下文
 │  响应数据                      │
 │<─────────────────────────────│
```

### 2.3 Token 设计

```json
{
  "user_id": 42,
  "exp": 1715136000,
  "iat": 1715049600
}
```

- **有效期：** 7 天
- **签发：** 登录成功时
- **刷新：** 暂不支持 Token 刷新，过期后重新走登录流程
- **密钥：** JWT_SECRET 环境变量，不在代码中硬编码

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

## 4. 数据模型

### 4.1 ER 图

```
┌──────────────────┐
│   users          │
│──────────────────│
│ id (PK)          │
│ openid (UNIQUE)  │
│ unionid (UNIQUE) │
│ nickname         │
│ avatar_url       │
│ invitation_code  │──> invitation_codes.code
│ status           │
│ created_at       │
│ updated_at       │
│ last_login_at    │
└────────┬─────────┘
         │
         │ 1:N
         ├──────────────────────┬──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────────┐  ┌──────────────────────────┐
│ user_watchlists  │  │ user_preferences     │  │ user_sector_favorites    │
│──────────────────│  │──────────────────────│  │──────────────────────────│
│ id (PK)          │  │ id (PK)              │  │ id (PK)                  │
│ user_id (FK)     │  │ user_id (FK)         │  │ user_id (FK)             │
│ name             │  │ pref_key             │  │ sector_code              │
│ sort_order       │  │ pref_value (TEXT)    │  │ sector_name              │
│ created_at       │  │ updated_at           │  │ sector_type              │
└────────┬─────────┘  └──────────────────────┘  │ sort_order               │
         │                                       │ added_at                 │
         │ 1:N                                   └──────────────────────────┘
         ▼
┌──────────────────────┐
│ watchlist_items      │
│──────────────────────│
│ id (PK)              │
│ watchlist_id (FK)    │
│ symbol               │
│ name                 │
│ market               │
│ sort_order           │
│ added_at             │
└──────────────────────┘


┌──────────────────────┐
│ invitation_codes     │
│──────────────────────│
│ id (PK)              │
│ code (UNIQUE)        │
│ max_uses             │
│ used_count           │
│ status               │
│ created_at           │
│ expires_at           │
└──────────────────────┘
```

### 4.2 表结构

#### users — 用户表

```sql
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    openid          TEXT    NOT NULL UNIQUE,
    unionid         TEXT            UNIQUE,
    nickname        TEXT    NOT NULL DEFAULT '用户',
    avatar_url      TEXT    NOT NULL DEFAULT '',
    invitation_code TEXT,
    status          TEXT    NOT NULL DEFAULT 'active',  -- active | banned
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    last_login_at   TEXT,

    CHECK (status IN ('active', 'banned'))
);

CREATE INDEX idx_users_openid   ON users(openid);
CREATE INDEX idx_users_unionid  ON users(unionid);
CREATE INDEX idx_users_status   ON users(status);
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| openid | 微信应用内唯一标识（每个公众号/小程序不同） |
| unionid | 微信开放平台统一标识（跨应用同一用户一致） |
| invitation_code | 注册时使用的邀请码（冗余存储，便于审计） |
| status | active=正常, banned=封禁 |

#### invitation_codes — 邀请码表

```sql
CREATE TABLE invitation_codes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT    NOT NULL UNIQUE,
    max_uses    INTEGER NOT NULL DEFAULT 1,
    used_count  INTEGER NOT NULL DEFAULT 0,
    status      TEXT    NOT NULL DEFAULT 'active',  -- active | disabled
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at  TEXT,

    CHECK (status IN ('active', 'disabled')),
    CHECK (max_uses > 0),
    CHECK (used_count >= 0)
);

CREATE INDEX idx_invitation_codes_code ON invitation_codes(code);
```

**业务规则：**
- 邀请码格式：8 位字母数字混合（如 `A3K9X7M2`），由管理员生成
- `max_uses` 可设为 -1 表示无限次使用
- `used_count >= max_uses` 且 `max_uses != -1` 时不可再用
- `expires_at` 为 NULL 表示永不过期

#### user_watchlists — 自选列表表

```sql
CREATE TABLE user_watchlists (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    name        TEXT    NOT NULL DEFAULT '默认自选',
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (length(name) <= 20)
);

CREATE INDEX idx_watchlists_user_id ON user_watchlists(user_id);
```

**业务规则：**
- 每个用户最多 10 个自选列表
- 注册时自动创建一个「默认自选」列表
- `name` 最长 20 个字符

#### watchlist_items — 自选股项表

```sql
CREATE TABLE watchlist_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    watchlist_id    INTEGER NOT NULL REFERENCES user_watchlists(id) ON DELETE CASCADE,
    symbol          TEXT    NOT NULL,
    name            TEXT    NOT NULL,
    market          TEXT    NOT NULL,  -- A | HK | US
    sort_order      INTEGER NOT NULL DEFAULT 0,
    added_at        TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (market IN ('A', 'HK', 'US')),
    UNIQUE (watchlist_id, symbol)
);

CREATE INDEX idx_items_watchlist_id ON watchlist_items(watchlist_id);
CREATE INDEX idx_items_symbol       ON watchlist_items(symbol);
```

**业务规则：**
- 同一 watchlist 内 symbol 不重复
- 单个列表最多 100 个标的
- 删除 watchlist 时级联删除 items（ON DELETE CASCADE）

#### user_preferences — 用户偏好表

```sql
CREATE TABLE user_preferences (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    pref_key    TEXT    NOT NULL,
    pref_value  TEXT    NOT NULL,  -- JSON 字符串
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),

    UNIQUE (user_id, pref_key)
);

CREATE INDEX idx_preferences_user_id ON user_preferences(user_id);
```

**预置偏好 Key：**

| Key | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| theme | string | `"light"` | 主题：light / dark / auto |
| default_market | string | `"A"` | 默认市场：A / HK / US |
| home_widgets | array | `["index_quote","temperature","watchlist"]` | 首页展示的组件 |
| valuation_default_period | string | `"10y"` | 估值图表默认时间段 |
| notification_enabled | boolean | `true` | 是否开启通知 |

**存储策略：**
- 偏好值统一存为 JSON 字符串
- 读取时 `json.loads(pref_value)`，写入时 `json.dumps(value)`
- 不在数据库层面做类型校验，由 Service 层处理

#### user_sector_favorites — 行业/概念板块关注表

```sql
CREATE TABLE user_sector_favorites (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    sector_code TEXT    NOT NULL,
    sector_name TEXT    NOT NULL,
    sector_type TEXT    NOT NULL,  -- industry | concept
    sort_order  INTEGER NOT NULL DEFAULT 0,
    added_at    TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (sector_type IN ('industry', 'concept')),
    UNIQUE (user_id, sector_code)
);

CREATE INDEX idx_sector_favorites_user_id ON user_sector_favorites(user_id);
CREATE INDEX idx_sector_favorites_code    ON user_sector_favorites(sector_code);
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| sector_code | 板块代码（如 `BK0477`，来自 Module 1 数据底座） |
| sector_name | 板块名称（冗余存储，便于直接展示，避免每次都查 Module 1） |
| sector_type | `industry`（行业）/ `concept`（概念），影响下游 Module 5 的分析策略 |

**业务规则：**
- 每个用户最多关注 50 个板块
- 同一板块不重复添加（`UNIQUE (user_id, sector_code)`）
- 与自选股（watchlist_items）完全独立，互不影响
- 下游消费者：Module 5（板块概念趋势追踪）

### 4.3 默认数据

用户注册时自动创建：

```sql
-- 1. 创建用户
INSERT INTO users (openid, unionid, nickname, avatar_url, invitation_code, status)
VALUES (?, ?, ?, ?, ?, 'active');

-- 2. 创建默认自选列表
INSERT INTO user_watchlists (user_id, name, sort_order)
VALUES (?, '默认自选', 0);

-- 3. 写入默认偏好
INSERT INTO user_preferences (user_id, pref_key, pref_value) VALUES
    (?, 'theme', '"light"'),
    (?, 'default_market', '"A"'),
    (?, 'home_widgets', '["index_quote","temperature","watchlist"]'),
    (?, 'valuation_default_period', '"10y"'),
    (?, 'notification_enabled', 'true');
```

## 5. 核心业务逻辑

### 5.1 微信登录流程（Service 伪代码）

```python
class AuthService:

    def wechat_callback(self, code: str, invitation_code: str | None = None):
        # 1. 用 code 换 access_token
        token_resp = wechat_api.get_access_token(code)
        if token_resp.error:
            raise AppError("INVALID_CODE")

        openid = token_resp.openid
        unionid = token_resp.get("unionid")

        # 2. 查是否已注册
        user = User.query.filter(
            (User.openid == openid) | (User.unionid == unionid)
        ).first()

        if user:
            # 老用户 → 更新登录时间，签发 JWT
            user.last_login_at = now()
            user.save()
            return {"token": jwt_encode(user.id), "user": user}

        # 3. 新用户
        user_info = wechat_api.get_user_info(token_resp.access_token, openid)

        if not invitation_code:
            # 未提供邀请码 → 返回"需要邀请码"
            return {
                "status": "need_invitation_code",
                "openid": openid,
                "nickname": user_info.nickname,
                "avatar_url": user_info.avatar_url
            }

        # 4. 有邀请码 → 校验
        code_record = InvitationCode.validate(invitation_code)
        if not code_record:
            raise AppError("INVALID_INVITATION_CODE")

        # 5. 创建用户
        user = User.create(
            openid=openid,
            unionid=unionid,
            nickname=user_info.nickname,
            avatar_url=user_info.avatar_url,
            invitation_code=invitation_code
        )
        code_record.use()

        # 6. 创建默认数据
        Watchlist.create_default(user.id)
        Preference.create_defaults(user.id)

        return {"token": jwt_encode(user.id), "user": user}
```

### 5.2 邀请码校验逻辑

```python
class InvitationCode:

    @classmethod
    def validate(cls, code: str) -> 'InvitationCode | None':
        record = cls.query.filter_by(code=code, status='active').first()
        if not record:
            return None
        # 检查过期
        if record.expires_at and record.expires_at < now():
            return None
        # 检查次数
        if record.max_uses != -1 and record.used_count >= record.max_uses:
            return None
        return record

    def use(self):
        self.used_count += 1
        if self.max_uses != -1 and self.used_count >= self.max_uses:
            self.status = 'disabled'
        self.save()
```

### 5.3 JWT 认证中间件

```python
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise AppError("UNAUTHORIZED", status=401)

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AppError("TOKEN_EXPIRED", status=401)
        except jwt.InvalidTokenError:
            raise AppError("INVALID_TOKEN", status=401)

        user = User.query.get(payload["user_id"])
        if not user or user.status != "active":
            raise AppError("USER_INACTIVE", status=403)

        g.current_user = user
        return f(*args, **kwargs)
    return decorated
```

## 6. 与上下游模块的接口契约

### 6.1 对其他模块暴露的能力

| 消费者模块 | 调用方式 | 用途 |
|-----------|---------|------|
| 所有模块 | `@auth_required` 装饰器 | 获取当前用户 `g.current_user` |
| 所有模块 | `g.current_user.id` | 数据隔离，按 user_id 过滤 |
| Module 3 | GET /api/v1/users/me/preferences | 首页组件布局配置 |
| Module 3 | GET /api/v1/watchlists/:id/items | 首页展示自选行情 |
| Module 4 | 偏好 `valuation_default_period` | 估值图表默认时间段 |
| Module 5 | GET /api/v1/sectors/favorites | 获取用户关注的板块列表，展示板块趋势 |
| Module 6 | GET /api/v1/watchlists/:id/items | 显示个股/基金是否已加入自选 |

### 6.2 依赖的上游模块

**Module 0 不依赖任何其他业务模块。**

唯一外部依赖：
- **微信开放平台 API** — OAuth token 换取 + 用户信息获取
  - `https://api.weixin.qq.com/sns/oauth2/access_token`
  - `https://api.weixin.qq.com/sns/userinfo`

## 7. 错误处理规范

### 统一错误响应格式

```json
{
  "error": {
    "code": "INVALID_INVITATION_CODE",
    "message": "邀请码不存在或已失效"
  }
}
```

### Module 0 错误码清单

| HTTP 状态码 | 错误码 | 说明 |
|-------------|--------|------|
| 401 | UNAUTHORIZED | 未提供 Token |
| 401 | TOKEN_EXPIRED | Token 已过期 |
| 401 | INVALID_TOKEN | Token 无效 |
| 403 | USER_INACTIVE | 用户被封禁 |
| 400 | INVALID_CODE | 微信授权 code 无效 |
| 400 | INVALID_INVITATION_CODE | 邀请码无效 |
| 400 | DUPLICATE_ITEM | 自选股重复添加 |
| 400 | ITEM_LIMIT_EXCEEDED | 超过列表容量限制 |
| 404 | WATCHLIST_NOT_FOUND | 自选列表不存在 |
| 400 | DUPLICATE_SECTOR | 板块已在关注列表中 |
| 400 | SECTOR_LIMIT_EXCEEDED | 超过板块关注上限（50 个） |
| 409 | BIND_FAILED | 绑定失败（openid 冲突） |

## 8. 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| JWT_SECRET | 是 | JWT 签名密钥 |
| WECHAT_APPID | 是 | 微信开放平台 AppID |
| WECHAT_SECRET | 是 | 微信开放平台 AppSecret |
| JWT_EXPIRE_DAYS | 否 | Token 有效期天数，默认 7 |

## 9. 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 认证方式 | 微信 OAuth + 邀请码 | 控制用户增长，避免机器人注册 |
| Session 管理 | JWT（无 refresh token） | MVP 简化，7 天有效期够用，过期重新登录可接受 |
| 用户标识 | unionid 优先 | 跨应用统一身份；openid 作为 fallback。未来只支持微信登录，不引入其他第三方平台 |
| 偏好存储 | Key-Value + JSON 值 | 灵活扩展，不需改表结构 |
| 自选列表上限 | 10 列表 × 100 标的（个股/基金） | 防止滥用，个人投资者够用 |
| 板块关注上限 | 50 个行业/概念板块 | 与自选股独立，服务不同的下游模块（Module 5 vs Module 6） |
| Token 刷新 | 暂不支持 | 减少复杂度，7 天重登成本低 |
| 邀请码管理 | 直接操作数据库 | MVP 阶段通过后台脚本初始化邀请码；管理后台作为未来扩展模块（含系统配置、监控等） |
| 板块关注独立建表 | user_sector_favorites 独立于 watchlist_items | 行业/概念板块与个股/基金是不同数据源，下游分析逻辑完全不同，解耦更合理 |

## 10. 待确认项

> ✅ 以下问题已于 2026-05-07 确认，结论已反映在上述设计中。

- [x] **unionid** — 保留为可选字段。未来只支持微信登录，openid 为主标识
- [x] **邀请码管理** — 直接操作数据库，管理后台作为未来扩展模块
- [x] **数量限制** — 个股/基金单列表 100 上限，行业/概念板块 50 上限（独立表）
- [x] **Token 有效期** — 7 天确认合适

### 未来扩展方向（MVP 后置）

- 管理后台模块：邀请码管理界面、系统配置、监控信息展示
- Token 刷新机制（如用户反馈频繁登录影响体验）
