# API 设计规范

> 本规范适用于 Strategy Compass 所有 RESTful API 的设计与实现。

## 1. URL 设计

### 1.1 基础格式

```
/api/v{version}/{module}/{resource}/{action}
```

### 1.2 版本策略

- 当前版本：`v1`
- 版本号在 URL 路径中体现
- 重大变更时升级版本号

### 1.3 模块前缀

| 模块 | 前缀 | 示例 |
|------|------|------|
| Module 0 用户系统 | `/api/v1` | `/api/v1/auth/wechat/callback` |
| Module 1 数据底座 | `/api/v1/data` | `/api/v1/data/quotes/stock/600519` |
| Module 2 新闻聚合 | `/api/v2` | `/api/v2/news` |
| Module 3 市场概览 | `/api/v3` | `/api/v3/market/overview` |
| Module 4 估值分析 | `/api/v4` | `/api/v4/valuation/index/000300` |

> **说明：** 版本号与模块号一致（Module N → vN），便于独立演进。

### 1.4 资源命名

- 使用名词复数形式
- 使用 kebab-case（短横线连接）
- 不使用动词，动词通过 HTTP Method 表达

```
✅ GET /api/v1/data/quotes/stocks
❌ GET /api/v1/data/get-stock-quote

✅ GET /api/v2/news
❌ GET /api/v2/get-news-list
```

### 1.5 URL 结构示例

```
GET    /api/v1/data/quotes/stock/:symbol      # 获取个股实时行情
GET    /api/v1/data/klines/stock/:symbol      # 获取个股历史 K 线
GET    /api/v4/valuation/index/:symbol        # 获取指数估值分析
POST   /api/v1/watchlists                     # 创建自选列表
PATCH  /api/v1/watchlists/:id                 # 修改自选列表
DELETE /api/v1/watchlists/:id                 # 删除自选列表
```

## 2. HTTP Method 语义

| Method | 用途 | 幂等性 |
|--------|------|--------|
| GET | 获取资源 | ✅ |
| POST | 创建资源 | ❌ |
| PUT | 全量更新 | ✅ |
| PATCH | 部分更新 | ✅ |
| DELETE | 删除资源 | ✅ |

## 3. 请求规范

### 3.1 请求格式

- Content-Type: `application/json`
- 所有请求体使用 JSON 格式
- 字段名使用 `snake_case`

### 3.2 认证

- 在请求头中携带 Token
- Header 格式：`Authorization: Bearer <token>`

```http
GET /api/v3/market/overview HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
```

### 3.3 查询参数

- 使用 `snake_case`
- 布尔值使用 `true`/`false` 字符串
- 日期格式：`YYYY-MM-DD`
- 时间格式：ISO 8601（UTC）

```
GET /api/v1/data/klines/stock/600519?market=A&start_date=2026-01-01&end_date=2026-05-07&limit=250
```

### 3.4 分页

两种分页方式：

**偏移分页（Offset-based）**

```
GET /api/v1/data/boards?offset=0&limit=20
```

**游标分页（Cursor-based）**

```
GET /api/v2/news?limit=30&before_id=12340
```

> 游标分页适用于时间序列数据（如新闻列表），避免数据漂移。

## 4. 响应规范

### 4.1 成功响应

```json
{
  "data": { ... },
  "message": "success"
}
```

或

```json
{
  "items": [ ... ],
  "has_more": true,
  "next_before_id": 12340
}
```

### 4.2 错误响应

统一格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

### 4.3 HTTP 状态码

| 状态码 | 使用场景 |
|--------|---------|
| 200 OK | GET/PUT/PATCH 成功 |
| 201 Created | POST 创建成功 |
| 204 No Content | DELETE 成功 |
| 400 Bad Request | 请求参数错误 |
| 401 Unauthorized | 未认证或 Token 过期 |
| 403 Forbidden | 无权限 |
| 404 Not Found | 资源不存在 |
| 409 Conflict | 资源冲突（如重复创建） |
| 422 Unprocessable Entity | 业务逻辑错误（如数据不足） |
| 429 Too Many Requests | 请求过于频繁 |
| 500 Internal Server Error | 服务器内部错误 |

### 4.4 字段命名

- 使用 `snake_case`
- 布尔值字段不加 `is_` 前缀（除非语义不清）
- 时间字段加 `_at` 后缀：`created_at`, `updated_at`
- 日期字段加 `_date` 后缀：`report_date`

### 4.5 数值格式

- 价格/金额：保留 2 位小数
- 百分比：保留 2 位小数（不带 % 符号）
- 涨跌幅：带符号，`1.25` 表示 +1.25%
- 大金额：使用原始数值（单位：元），前端格式化

## 5. 错误码规范

### 5.1 错误码格式

统一使用大写下划线格式：`MODULE_ACTION_ERROR`

### 5.2 全局错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| UNAUTHORIZED | 401 | 未提供 Token 或 Token 无效 |
| TOKEN_EXPIRED | 401 | Token 已过期 |
| FORBIDDEN | 403 | 无权访问 |
| NOT_FOUND | 404 | 资源不存在 |
| RATE_LIMITED | 429 | 请求过于频繁 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 5.3 模块特定错误码

各模块在各自设计文档中定义。命名规则：`{MODULE}_{RESOURCE}_{ERROR}`

示例：
- `SYMBOL_NOT_FOUND` — 标的代码不存在
- `DATA_NOT_READY` — 数据正在初始化
- `INSUFFICIENT_DATA` — 历史数据不足

## 6. 认证与授权

### 6.1 JWT Token

- 签发：登录成功后返回
- 有效期：7 天
- 无 Refresh Token（MVP 简化）

### 6.2 认证流程

```
1. 前端调用微信登录 → 获取 code
2. 后端用 code 换 openid → 签发 JWT Token
3. 前端存储 Token（localStorage）
4. 后续请求携带 Authorization: Bearer <token>
```

### 6.3 认证装饰器

所有需要认证的接口使用 `@auth_required` 装饰器：

```python
@app.route("/api/v3/market/overview")
@auth_required
def market_overview():
    user_id = g.current_user.id
    ...
```

## 7. 版本演进

### 7.1 兼容策略

- 同一版本内保持向后兼容
- 重大变更升级版本号
- 旧版本保留至少 3 个月过渡期

### 7.2 弃用标记

```json
{
  "data": { ... },
  "deprecated": {
    "field": "old_field",
    "replacement": "new_field",
    "removed_at": "2026-08-01"
  }
}
```

## 8. 文档维护

- 每个模块的 API 定义在 `docs/modules/module-N-*.md` 中
- 全局 API 变更更新 `docs/api.md`
- 接口变更必须同步更新文档
