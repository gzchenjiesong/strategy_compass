---
title: "Module 0: 用户系统 — 接口与数据模型设计"
type: spec
module: module-0
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

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

