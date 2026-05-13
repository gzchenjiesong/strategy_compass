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


## 子文档

| 文档 | 说明 |
|------|------|
| [api.md](api.md) | 认证相关接口 |
| [data-model.md](data-model.md) | User 表结构 |
| [flow.md](flow.md) | 登录/注册流程 |

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

