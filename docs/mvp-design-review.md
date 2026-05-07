---
title: "MVP 设计完整性检查报告"
type: review
status: draft
created: 2026-05-07
author: 顾清辞
---

# MVP 设计完整性检查报告

> 检查范围：Module 0（用户系统）/ Module 1（数据底座）/ Module 2（新闻聚合）/ Module 3（市场概览）/ Module 4（估值分析）
> 检查维度：功能覆盖 / 接口闭环 / 数据链路 / 编码就绪度 / 阻塞项

---

## 1. 检查结论

| 维度 | 状态 | 说明 |
|------|------|------|
| 功能覆盖 | 🟡 基本完整 | 1 个关键数据源缺口需决策 |
| 接口契约闭环 | ✅ 完整 | 模块间调用关系已全部对齐 |
| 前端页面 → API 映射 | ✅ 完整 | 所有页面都有对应的 API 支撑 |
| 数据模型 | ✅ 完整 | 14 + 5 张表覆盖全部需求 |
| 编码就绪度 | 🟡 基本就绪 | 2 项需补充决策后可进入编码 |

**总体判断：设计达到 90% 完整度，修复 2 个关键缺口后可正式进入编码阶段。**

---

## 2. 功能覆盖检查

### 2.1 MVP 功能清单 vs 设计覆盖

| 功能 | 归属模块 | 设计状态 | 说明 |
|------|---------|---------|------|
| 微信 OAuth 登录 | Module 0 | ✅ | 含邀请码校验、Token 机制 |
| 用户自选股管理 | Module 0 | ✅ | 上限 100，多列表支持 |
| 用户板块关注管理 | Module 0 | ✅ | 上限 50，独立表 |
| 用户偏好设置 | Module 0 | ✅ | 主题/默认市场等 |
| 实时行情获取 | Module 1 | ✅ | A股/港股/ETF/指数/板块 |
| 历史 K 线获取 | Module 1 | ✅ | 日 K 存储，周/月聚合 |
| 估值数据获取 | Module 1 | ✅ | A股指数/行业/个股 |
| 板块数据获取 | Module 1 | ✅ | 行业+概念，含成分股 |
| 资金流向获取 | Module 1 | ✅ | 北向+板块资金 |
| 融资融券获取 | Module 1 | ✅ | 沪深汇总，10 年历史 |
| 新闻原始数据获取 | Module 1 | ✅ | 金十数据，72h TTL |
| 新闻列表+过滤 | Module 2 | ✅ | 全部/普通/重要/关联 |
| 新闻详情展示 | Module 2 | ✅ | 弹窗浮层 |
| 首页概览 | Module 3 | ✅ | 情绪+区间分布+指数速览+快讯 |
| 大盘指数展示 | Module 3 | ✅ | A股/港股/美股分组卡片 |
| 板块展示 | Module 3 | ✅ | 用户关注板块卡片 |
| 指数/板块详情弹窗 | Module 3 | ✅ | 聚合行情+估值+风险+热度 |
| 估值百分位计算 | Module 4 | ✅ | PE/PB/PS/价格/融资余额/杠杆率 |
| 风险指标计算 | Module 4 | ✅ | 回撤/波动率/夏普/卡玛/Beta |
| 历史估值曲线 | Module 4 | ✅ | PE/PB 时间序列，图表数据 |
| 估值区间统计 | Module 4 | ✅ | 低估/适中/高估分布 |

### 2.2 未覆盖的功能（已确认非 MVP）

| 功能 | 原因 |
|------|------|
| 个股/ETF 详情页 | Module 6，MVP 后置 |
| 基金定投策略 | Module 6，MVP 后置 |
| 策略回测 | 技术复杂度高，后置 |
| 通知推送 | Module 7，MVP 后置 |
| 管理后台 | 直接操作数据库，后置 |
| 多用户支持 | 一期只有单用户模式 |

---

## 3. 接口契约闭环检查

### 3.1 Module 3（市场概览）依赖检查

| 依赖的接口 | 提供方 | 状态 |
|-----------|--------|------|
| `GET /api/v4/valuation/market` | Module 4 | ✅ 3.5 节 |
| `GET /api/v4/valuation/zone-summary` | Module 4 | ✅ 3.6 节 |
| `GET /api/v4/valuation/indices` | Module 4 | ✅ 3.1 节 |
| `GET /api/v4/valuation/index/:symbol` | Module 4 | ✅ 3.1 节 |
| `GET /api/v4/valuation/board/:code` | Module 4 | ✅ 3.2 节 |
| `GET /api/v4/valuation/boards` | Module 4 | ✅ 3.2 节 |
| `GET /api/v2/news?filter=important` | Module 2 | ✅ 2.1 节 |
| 用户关注板块列表 | Module 0 | ✅ |

### 3.2 Module 2（新闻聚合）依赖检查

| 依赖的接口/表 | 提供方 | 状态 |
|--------------|--------|------|
| `news_raw` 表 | Module 1 | ✅ 3.2 节 |
| 用户关注列表 | Module 0 | ✅ |

### 3.3 Module 4（估值分析）依赖检查

| 依赖的接口 | 提供方 | 状态 |
|-----------|--------|------|
| `GET /api/v1/data/klines/*` | Module 1 | ✅ 2.2 节 |
| `GET /api/v1/data/valuations/*` | Module 1 | ✅ 2.3 节 |
| `GET /api/v1/data/margin/summary` | Module 1 | ✅ 2.8 节 |
| `GET /api/v1/data/flows/*` | Module 1 | ✅ 2.6 节 |
| `GET /api/v1/data/quotes/*` | Module 1 | ✅ 2.1 节 |

### 3.4 Module 1（数据底座）依赖检查

| 依赖的接口 | 提供方 | 状态 |
|-----------|--------|------|
| `@auth_required` 认证 | Module 0 | ✅ |
| 用户自选股列表 | Module 0 | ✅ |
| 用户板块关注列表 | Module 0 | ✅ |

**结论：所有模块间依赖关系均已对齐，无悬空接口。**

---

## 4. 前端页面 → API → 数据表 完整链路

### 4.1 资讯页面（Module 2）

| 页面状态 | API | 数据表 |
|---------|-----|--------|
| 全部新闻 | `GET /api/v2/news?filter=all` | `news_raw` |
| 普通新闻 | `GET /api/v2/news?filter=normal` | `news_raw` |
| 重要新闻 | `GET /api/v2/news?filter=important` | `news_raw` |
| 关联新闻 | `GET /api/v2/news?filter=related` | `news_raw` + `user_watchlist` |
| 新闻详情弹窗 | `GET /api/v2/news/:id` | `news_raw` |

### 4.2 市场页面（Module 3）

| 页面状态 | API | 数据来源 |
|---------|-----|---------|
| 概览 | `GET /api/v3/market/overview` | Module 4 + Module 2 |
| 大盘-A股 | `GET /api/v3/market/indices` → a_share | Module 4 |
| 大盘-港股 | `GET /api/v3/market/indices` → hk | Module 4 |
| 大盘-美股 | `GET /api/v3/market/indices` → us | Module 4 |
| 板块 | `GET /api/v3/market/boards` | Module 4 + Module 0 |
| 指数详情弹窗 | `GET /api/v3/market/index/:symbol/detail` | Module 4 + Module 1 |
| 板块详情弹窗 | `GET /api/v3/market/board/:code/detail` | Module 4 + Module 1 |

### 4.3 用户页面（Module 0）

| 功能 | API | 数据表 |
|------|-----|--------|
| 微信登录 | `POST /api/v1/auth/wechat/callback` | `user` |
| 用户信息 | `GET /api/v1/users/me` | `user` |
| 自选股管理 | `GET/POST/DELETE /api/v1/watchlists/*` | `user_watchlist` |
| 板块关注管理 | `GET/POST/DELETE /api/v1/sectors/favorites` | `user_sector_favorites` |
| 偏好设置 | `GET/PUT /api/v1/users/me/preferences` | `user_preference` |

---

## 5. 数据模型完整性

### 5.1 Module 1 数据底座（14 张表）

| 表名 | 用途 | 状态 |
|------|------|------|
| `stock_daily_kline` | 个股/ETF/港股日 K | ✅ |
| `index_daily_kline` | 指数日 K | ✅ |
| `board_daily_kline` | 板块日 K | ✅ |
| `stock_valuation` | 个股估值 | ✅ |
| `index_valuation` | 指数估值 | ✅ |
| `board_valuation` | 板块估值 | ✅ |
| `financial_report` | 财务报表 | ✅ |
| `board_info` | 板块信息 | ✅ |
| `board_constituent` | 板块成分股 | ✅ |
| `fund_nav` | 基金净值 | ✅ |
| `money_flow` | 资金流向 | ✅ |
| `news_raw` | 新闻原始数据 | ✅ |
| `margin_daily` | 融资融券汇总 | ✅ |
| `data_sync_log` | 同步任务日志 | ✅ |

### 5.2 Module 0 用户系统（5 张表）

| 表名 | 用途 | 状态 |
|------|------|------|
| `user` | 用户信息 | ✅ |
| `user_watchlist` | 自选股 | ✅ |
| `user_sector_favorites` | 板块关注 | ✅ |
| `user_preference` | 偏好设置 | ✅ |
| `invite_code` | 邀请码 | ✅ |

---

## 6. 发现的问题（按优先级排序）

### ⚠️ P0：港股/美股指数 PE/PB 估值数据来源缺失

**问题描述：**
- Module 3 大盘页设计中，港股（恒生/恒生科技）和美股（标普500/纳指）指数卡片包含 `pe_ttm`、`pe_percentile`、`pb`、`pb_percentile` 字段
- Module 1 数据源分析中，A 股指数估值通过 AKShare `index_all_cni()`（国证指数）获取
- **但 AKShare 没有提供港股/美股指数的 PE/PB 历史数据接口**
- 实际验证：`stock_index_pe_lg(symbol='恒生指数')` 和 `stock_index_pe_lg(symbol='标普500')` 均报错

**影响范围：**
- Module 3 大盘页 — 港股/美股指数卡片无法展示 PE/PB 百分位
- Module 4 — 港股/美股指数无法计算估值百分位

**建议方案（三选一）：**

| 方案 | 说明 | 工作量 | 推荐度 |
|------|------|--------|--------|
| A | MVP 阶段港股/美股指数只展示价格百分位+回撤，不展示 PE/PB | 小 | ⭐⭐⭐ 推荐 |
| B | 从其他免费数据源获取（如网页爬取恒生指数公司官网、Shiller PE 数据） | 中 | ⭐⭐ |
| C | 手动维护港股/美股指数历史 PE/PB（数据量小，定期更新） | 中 | ⭐⭐ |

> **建议采用方案 A**：港股/美股指数的 PE/PB 对 A 股投资者决策影响有限，价格百分位+回撤已足够判断市场位置。后续版本再补充 PE/PB。

---

### ⚠️ P1：ETF → 指数映射表未定义

**问题描述：**
- Module 4 提到 ETF 估值通过关联指数实现，需要 ETF→指数映射关系
- 但文档中未定义映射表结构，只在 Module 4 中提及"可通过 `board_constituent` 表或硬编码实现"

**影响范围：**
- MVP 阶段影响有限，因为 Module 6（ETF 详情页）MVP 后置
- 但如果用户在自选股中添加了 ETF，大盘页/关注页需要展示其估值

**建议：**
- MVP 阶段硬编码核心 ETF→指数映射（如 510300→000300）
- 后续版本再建表支持动态映射

---

### ⚠️ P1：核心指数清单未在文档中明确列出

**问题描述：**
- Module 1 多次提到"10 个核心指数"，但具体是哪 10 个未在设计文档中列出
- Module 1 说"硬编码在代码中，不存数据库"

**建议补充到 Module 1 文档：**

| 市场 | 指数代码 | 指数名称 | 估值数据可用性 |
|------|---------|---------|--------------|
| A股 | 000001 | 上证指数 | ✅ PE/PB |
| A股 | 000300 | 沪深300 | ✅ PE/PB |
| A股 | 000905 | 中证500 | ✅ PE/PB |
| A股 | 399006 | 创业板指 | ✅ PE/PB |
| A股 | 000688 | 科创50 | ✅ PE/PB |
| A股 | 930050 | 中证A500 | ✅ PE/PB |
| 港股 | HSI | 恒生指数 | ⚠️ 仅价格 |
| 港股 | HSTECH | 恒生科技 | ⚠️ 仅价格 |
| 美股 | SPX | 标普500 | ⚠️ 仅价格 |
| 美股 | IXIC | 纳斯达克 | ⚠️ 仅价格 |

---

### ⚠️ P1：Module 4 定时触发机制未明确定义

**问题描述：**
- Module 4 提到"每日 18:00 估值数据更新后增量计算"，但定时任务的调度定义在 Module 1 中
- Module 4 的百分位计算触发时机（是 Module 1 更新估值后自动触发，还是 Module 4 自己定时扫描？）未明确

**建议：**
- 在 Module 1 的定时任务中，每日 18:00 估值更新完成后，调用 Module 4 的刷新接口
- 或在 Module 4 中独立定义调度器，监听 Module 1 的数据更新事件

---

### ℹ️ P2：4 项待确认项（Module 1 文档）

| 待确认项 | 当前状态 | 是否阻塞编码 |
|---------|---------|------------|
| 金十 API 具体接口格式 | 需获取 API Key 后确认 | 🟡 阻塞新闻模块编码 |
| 港股实时行情数据源 | 已确认用 AKShare + 腾讯财经 | ✅ 不阻塞 |
| 板块搜索是否支持拼音 | 前端优化项，不阻塞 | ✅ 不阻塞 |
| 数据同步失败是否告警 | MVP 后置 | ✅ 不阻塞 |

**结论：只有金十 API 格式确认会轻微阻塞 Module 2 编码，其他不阻塞。**

---

### ℹ️ P2：板块页空状态未设计

**问题描述：**
- Module 3 板块页只展示用户关注的板块
- 新用户首次登录时，板块关注为空，页面需要空状态设计

**建议：**
- 空状态展示提示文案 + "去发现板块"按钮
- 点击跳转到板块搜索页面（Module 1 `GET /api/v1/data/boards`）

---

## 7. 编码就绪度评估

### 7.1 每个模块的编码准备度

| 模块 | 就绪度 | 说明 |
|------|--------|------|
| Module 0 用户系统 | 95% | 接口/表/逻辑均完整，可直接编码 |
| Module 1 数据底座 | 85% | 数据源选型清晰，但金十 API 格式待确认 |
| Module 2 新闻聚合 | 90% | 逻辑简单，依赖 Module 1 的 news_raw 表 |
| Module 3 市场概览 | 85% | 数据聚合逻辑清晰，需确认港股/美股估值方案 |
| Module 4 估值分析 | 85% | 计算逻辑完整，需确认触发机制 |

### 7.2 推荐编码顺序

```
Phase 1（并行）：
  ├── Module 0 用户系统（基础最先）
  └── Module 1 数据底座（SQLite 表创建 + 基础接口骨架）

Phase 2（依赖 Phase 1）：
  ├── Module 4 估值分析（计算引擎）
  └── Module 2 新闻聚合（加工层）

Phase 3（依赖 Phase 2）：
  └── Module 3 市场概览（数据聚合层 + 前端对接）
```

---

## 8. 建议的下一步行动

1. **确认港股/美股指数估值方案**（P0）
   - 建议采用方案 A：MVP 阶段只展示价格百分位+回撤
   - 需要修改 Module 3 和 Module 4 的设计文档

2. **补充核心指数清单**（P1）
   - 将 10 个核心指数的具体列表写入 Module 1 文档

3. **明确 Module 4 触发机制**（P1）
   - 在 Module 1 或 Module 4 文档中补充定时调度说明

4. **确认金十 API 格式**（P2）
   - 获取 API Key 后补充到 Module 1 文档

5. **正式进入编码**
   - 按 Phase 1 → Phase 2 → Phase 3 顺序开始实现
