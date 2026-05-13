---
title: "Module 1: 数据底座 — 接口与数据模型设计"
type: spec
module: module-1
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---


# Module 1: 数据底座

> 前置文档：[`docs/archive/modules-20260513/module-1-data-source-analysis.md`](../../archive/modules-20260513/module-1-data-source-analysis.md)（数据源选型、缓存、去重、排序策略）
> 本文档聚焦：接口定义 + 数据表结构 + 核心业务逻辑。

## 1. 职责边界

**做：**
- 统一获取所有外部金融数据（行情/估值/财务/板块/基金/新闻）
- SQLite 持久化缓存 + 进程内内存缓存
- 数据清洗、去重、标准化
- 提供标准化数据 API 供下游模块消费
- 系统首次部署时初始化 10 个核心指数 20 年日 K
- 用户添加自选/关注后按需触发历史数据拉取

**不做：**
- 估值百分位计算（归 Module 4）
- 新闻加工处理（归 Module 2）
- 用户数据管理（归 Module 0）
- 直接对外展示（归 Module 3/5/6）

**核心约束：** 数据获取唯一入口 — 其他模块不直接调用外部 API。


## 子文档

| 文档 | 说明 |
|------|------|
| [api.md](api.md) | 数据服务接口 |
| [data-model.md](data-model.md) | 数据表结构 |
| [flow.md](flow.md) | 数据同步流程 |

## 5. 与上下游模块的接口契约

### 5.1 对下游暴露的能力

| 消费者模块 | 调用的 API | 用途 |
|-----------|-----------|------|
| Module 2 新闻聚合 | GET /api/v1/data/news | 获取金十原始快讯 |
| Module 3 市场概览 | GET /api/v1/data/quotes/indices | 首页指数行情 |
| Module 3 市场概览 | GET /api/v1/data/quotes/boards | 板块涨跌排行 |
| Module 3 市场概览 | GET /api/v1/data/flows/northbound | 北向资金流向 |
| Module 4 估值分析 | GET /api/v1/data/valuations/index/:symbol | 指数 PE/PB |
| Module 4 估值分析 | GET /api/v1/data/klines/index/:symbol | 历史 K 线（计算 PE 百分位） |
| Module 4 估值分析 | GET /api/v1/data/boards/indices/:symbol/constituents | 指数成分股 |
| Module 4 估值分析 | GET /api/v1/data/margin/summary | 融资融券历史+百分位（杠杆率分析） |
| Module 5 板块概念 | GET /api/v1/data/klines/board/:code | 板块历史 K 线 |
| Module 5 板块概念 | GET /api/v1/data/boards/:code/constituents | 板块成分股 |
| Module 5 板块概念 | GET /api/v1/data/flows/board/:code | 板块资金流向 |
| Module 6 个股详情 | GET /api/v1/data/klines/stock/:symbol | 个股历史 K 线 |
| Module 6 个股详情 | GET /api/v1/data/valuations/stock/:symbol | 个股估值 |
| Module 6 个股详情 | GET /api/v1/data/financials/:symbol | 个股财务 |

### 5.2 依赖的上游模块

| 上游模块 | 依赖内容 | 调用方式 |
|---------|---------|---------|
| Module 0 用户系统 | `@auth_required` 认证 | 装饰器 |
| Module 0 用户系统 | 用户自选股列表 | GET /api/v1/watchlists/:id/items |
| Module 0 用户系统 | 用户板块关注列表 | GET /api/v1/sectors/favorites |


## 6. 错误处理规范

### 统一错误响应格式

```json
{
  "error": {
    "code": "SYMBOL_NOT_FOUND",
    "message": "标的代码不存在"
  }
}
```

### Module 1 错误码清单

| HTTP 状态码 | 错误码 | 说明 |
|-------------|--------|------|
| 401 | UNAUTHORIZED | 未提供 Token |
| 404 | SYMBOL_NOT_FOUND | 标的代码不存在 |
| 404 | BOARD_NOT_FOUND | 板块代码不存在 |
| 404 | DATA_NOT_FOUND | 无可用数据 |
| 409 | DATA_NOT_READY | 该标的数据正在初始化中 |
| 400 | INVALID_DATE_RANGE | 日期范围无效 |
| 400 | INVALID_PERIOD | K 线周期参数无效 |
| 429 | RATE_LIMITED | 请求过于频繁 |
| 500 | FETCH_FAILED | 外部数据源获取失败 |
| 500 | TASK_FAILED | 数据任务执行失败 |


## 7. 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| JIN10_API_KEY | 是 | 金十数据 API Key |
| DATA_CACHE_DIR | 否 | SQLite 数据文件目录，默认 `./data` |
| MEMORY_CACHE_TTL | 否 | 内存缓存默认 TTL（秒），默认 60 |
| AKSHARE_CALL_INTERVAL | 否 | AKShare 调用间隔（秒），默认 0.5 |
| SYNC_WORKER_COUNT | 否 | 后台同步 Worker 数量，默认 1 |
| CORE_INDICES | 否 | 核心指数清单（JSON），默认内置 10 个 |


## 8. 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| K 线表按类型分表 | stock / index / board 三张表 | 不同历史深度、不同查询模式、不同索引策略 |
| K 线只存日 K | 日 K 存储，周/月 K 按需聚合 | 减少存储冗余，聚合逻辑简单 |
| 估值数据 INSERT OR REPLACE | 当日覆盖更新 | 估值数据可能在盘后修正 |
| K 线数据 INSERT OR IGNORE | 已存在不覆盖 | 历史数据不会修正，避免重复写入 |
| 新闻 TTL 72 小时 | 自动清理过期新闻 | 新闻时效性强，控制数据量 |
| 初始化按需触发 | 用户添加后异步拉取 | 不预拉全量数据，减少无意义存储和外部源压力 |
| 任务状态持久化 | data_sync_log 表 | 重启后可恢复任务状态，支持进度查询 |
| 内存缓存用进程内 dict | MVP 够用 | 无需引入 Redis，单机部署场景足够 |
| 融资融券纳入数据底座 | 沪深汇总级别，10 年历史 | 杠杆率百分位是市场热度核心指标，数据量极小（~2500 条） |
| 融资融券入库时预计算杠杆率 | leverage_ratio 字段冗余存储 | 避免每次查询时重复计算，百分位查询更高效 |
| A 股总市值近似 | 上证指数 total_market_cap | 覆盖 90%+ 市值，精度足够；避免全市场扫描的性能开销 |


## 9. 待确认项

- [ ] 金十数据 API 的具体接口路径和返回格式？（需确认 API Key 后对接）
- [ ] 港股实时行情是否也需要从 AKShare 获取？还是只用腾讯财经？
- [ ] 板块搜索是否需要支持拼音首字母搜索？（如输入 `bdt` 匹配 `半导体`）
- [ ] 数据同步失败时是否需要告警通知？（MVP 后置？）

