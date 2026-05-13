---
title: "Module 1: 数据底座 — 接口与数据模型设计"
type: spec
module: module-1
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

## 3. 数据模型

### 3.1 ER 图

```
┌──────────────────────┐
│ stock_daily_kline    │  个股/ETF/港股日K
│──────────────────────│
│ id (PK)              │
│ symbol               │
│ market               │
│ date                 │
│ open / high / low    │
│ close / volume       │
│ turnover / change_pct│
└──────────────────────┘

┌──────────────────────┐
│ index_daily_kline    │  指数日K
│──────────────────────│
│ id (PK)              │
│ symbol               │
│ market               │
│ date                 │
│ open / high / low    │
│ close / volume       │
│ turnover / change_pct│
└──────────────────────┘

┌──────────────────────┐
│ board_daily_kline    │  板块日K
│──────────────────────│
│ id (PK)              │
│ board_code           │
│ board_type           │
│ date                 │
│ open / high / low    │
│ close / volume       │
│ turnover / change_pct│
└──────────────────────┘

┌──────────────────────┐
│ stock_valuation      │  个股估值指标
│──────────────────────│
│ id (PK)              │
│ symbol / market      │
│ date                 │
│ pe_ttm / pb / ps_ttm │
│ dividend_yield       │
│ market_cap / ...     │
└──────────────────────┘

┌────────────────────────┐
│ index_valuation        │  指数估值
│────────────────────────│
│ id (PK)                │
│ symbol                 │
│ date                   │
│ pe_ttm / pb            │
│ dividend_yield         │
│ total_market_cap       │  ← 新增：指数覆盖总市值
└────────────────────────┘

┌──────────────────────┐
│ board_valuation      │  板块估值
│──────────────────────│
│ id (PK)              │
│ board_code           │
│ date                 │
│ pe_static / pe_ttm   │
│ pb                   │
└──────────────────────┘

┌──────────────────────┐
│ financial_report     │  财务报表
│──────────────────────│
│ id (PK)              │
│ symbol / market      │
│ report_date          │
│ report_type          │
│ revenue / net_profit │
│ roe / eps / ...      │
└──────────────────────┘

┌──────────────────────┐
│ board_info           │  板块信息
│──────────────────────│
│ id (PK)              │
│ code (UNIQUE)        │
│ name / type          │
│ stock_count          │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│ board_constituent    │  板块成分股
│──────────────────────│
│ id (PK)              │
│ board_code (FK)      │
│ symbol               │
│ name / market        │
│ weight               │
└──────────────────────┘

┌──────────────────────┐
│ fund_nav             │  基金净值
│──────────────────────│
│ id (PK)              │
│ fund_code            │
│ nav_date             │
│ nav / acc_nav        │
│ change_pct           │
└──────────────────────┘

┌──────────────────────┐
│ money_flow           │  资金流向
│──────────────────────│
│ id (PK)              │
│ flow_type            │
│ entity_code          │
│ date                 │
│ net_inflow / ...     │
└──────────────────────┘

┌──────────────────────┐
│ news_raw             │  新闻原始数据
│──────────────────────│
│ id (PK)              │
│ source / source_id   │
│ title / content      │
│ important / tags     │
│ publish_time         │
└──────────────────────┘

┌──────────────────────────┐
│ margin_daily             │  融资融券汇总（沪深合计）
│──────────────────────────│
│ id (PK)                  │
│ date (UNIQUE)            │
│ financing_balance        │  合计融资余额
│ securities_balance       │  合计融券余额
│ financing_buy_amount     │  当日融资买入额
│ financing_balance_change │  融资余额日变动
│ total_market_cap         │  当日A股总市值
│ leverage_ratio           │  杠杆率%
└──────────────────────────┘

┌──────────────────────┐
│ data_sync_log        │  数据同步日志
│──────────────────────│
│ id (PK)              │
│ task_id              │
│ task_type            │
│ target               │
│ status / progress    │
│ started_at / ...     │
└──────────────────────┘
```

### 3.2 表结构

#### stock_daily_kline — 个股/ETF/港股日 K 线表

```sql
CREATE TABLE stock_daily_kline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol      TEXT    NOT NULL,
    market      TEXT    NOT NULL,   -- A | HK
    date        TEXT    NOT NULL,   -- YYYY-MM-DD
    open        REAL    NOT NULL,
    high        REAL    NOT NULL,
    low         REAL    NOT NULL,
    close       REAL    NOT NULL,
    volume      INTEGER NOT NULL DEFAULT 0,
    turnover    REAL    NOT NULL DEFAULT 0,
    change_pct  REAL,               -- 涨跌幅 %

    CHECK (market IN ('A', 'HK')),
    UNIQUE (symbol, market, date)
);

CREATE INDEX idx_stock_kline_symbol ON stock_daily_kline(symbol, market);
CREATE INDEX idx_stock_kline_date   ON stock_daily_kline(date);
```

**业务规则：**
- 覆盖 A 股个股、港股个股、场内 ETF（ETF 使用 A 股代码体系）
- 历史深度：个股/ETF 最长 10 年
- 去重：`(symbol, market, date)` 唯一，INSERT OR IGNORE
- 排序：默认 `date ASC`

#### index_daily_kline — 指数日 K 线表

```sql
CREATE TABLE index_daily_kline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol      TEXT    NOT NULL,
    market      TEXT    NOT NULL,   -- A | GIDX
    date        TEXT    NOT NULL,
    open        REAL    NOT NULL,
    high        REAL    NOT NULL,
    low         REAL    NOT NULL,
    close       REAL    NOT NULL,
    volume      INTEGER NOT NULL DEFAULT 0,
    turnover    REAL    NOT NULL DEFAULT 0,
    change_pct  REAL,

    CHECK (market IN ('A', 'GIDX')),
    UNIQUE (symbol, market, date)
);

CREATE INDEX idx_index_kline_symbol ON index_daily_kline(symbol, market);
CREATE INDEX idx_index_kline_date   ON index_daily_kline(date);
```

**业务规则：**
- 覆盖 A 股指数（上证/沪深300/A500/中证2000/科创50/创业板指）和全球指数（恒生/恒生科技/标普/纳指）
- 历史深度：20 年
- 首次部署自动拉取 10 个核心指数

#### board_daily_kline — 板块日 K 线表

```sql
CREATE TABLE board_daily_kline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    board_code  TEXT    NOT NULL,
    board_type  TEXT    NOT NULL,   -- industry | concept
    date        TEXT    NOT NULL,
    open        REAL    NOT NULL,
    high        REAL    NOT NULL,
    low         REAL    NOT NULL,
    close       REAL    NOT NULL,
    volume      INTEGER NOT NULL DEFAULT 0,
    turnover    REAL    NOT NULL DEFAULT 0,
    change_pct  REAL,

    CHECK (board_type IN ('industry', 'concept')),
    UNIQUE (board_code, date)
);

CREATE INDEX idx_board_kline_code ON board_daily_kline(board_code);
CREATE INDEX idx_board_kline_date ON board_daily_kline(date);
```

**业务规则：**
- 覆盖行业板块和概念板块
- 历史深度：15 年
- 按需触发：用户添加板块关注后拉取

#### stock_valuation — 个股估值指标表

```sql
CREATE TABLE stock_valuation (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol          TEXT    NOT NULL,
    market          TEXT    NOT NULL,
    date            TEXT    NOT NULL,
    pe_ttm          REAL,       -- 滚动市盈率
    pb              REAL,       -- 市净率
    ps_ttm          REAL,       -- 滚动市销率
    dividend_yield  REAL,       -- 股息率 %
    market_cap      REAL,       -- 流通市值
    total_market_cap REAL,      -- 总市值

    CHECK (market IN ('A', 'HK')),
    UNIQUE (symbol, market, date)
);

CREATE INDEX idx_stock_val_symbol ON stock_valuation(symbol, market);
CREATE INDEX idx_stock_val_date   ON stock_valuation(date);
```

**业务规则：**
- 覆盖 A 股个股、港股个股、场内 ETF
- 更新频率：每日收盘后
- 去重：`(symbol, market, date)` 唯一，INSERT OR REPLACE（当日可能修正）

#### index_valuation — 指数估值表

```sql
CREATE TABLE index_valuation (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol          TEXT    NOT NULL,
    date            TEXT    NOT NULL,
    pe_ttm          REAL,
    pb              REAL,
    dividend_yield  REAL,
    total_market_cap REAL,      -- 当日指数覆盖范围总市值（用于融资/市值比计算）

    UNIQUE (symbol, date)
);

CREATE INDEX idx_index_val_symbol ON index_valuation(symbol);
CREATE INDEX idx_index_val_date   ON index_valuation(date);
```

**业务规则：**
- 覆盖 A 股主要指数和全球指数（有估值数据的）
- 数据源：国证指数 `index_all_cni()` + 自行计算历史序列
- `total_market_cap`：上证指数（000001）覆盖的总市值，作为 A 股总市值的近似值
- 更新频率：每日收盘后

#### board_valuation — 板块估值表

```sql
CREATE TABLE board_valuation (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    board_code      TEXT    NOT NULL,
    date            TEXT    NOT NULL,
    pe_static       REAL,       -- 静态市盈率
    pe_ttm          REAL,       -- 滚动市盈率
    pb              REAL,       -- 市净率

    UNIQUE (board_code, date)
);

CREATE INDEX idx_board_val_code ON board_valuation(board_code);
CREATE INDEX idx_board_val_date ON board_valuation(date);
```

**业务规则：**
- 数据源：申万宏源 `sw_index_first_info()`
- 覆盖行业板块和概念板块（有估值数据的）
- 更新频率：每日收盘后
- 去重：`(board_code, date)` 唯一，INSERT OR REPLACE

#### financial_report — 财务报表表

```sql
CREATE TABLE financial_report (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol          TEXT    NOT NULL,
    market          TEXT    NOT NULL,
    report_date     TEXT    NOT NULL,   -- 报告期 YYYY-MM-DD
    report_type     TEXT    NOT NULL,   -- annual | semi_annual | quarterly
    revenue         REAL,               -- 营业收入
    net_profit      REAL,               -- 归母净利润
    roe             REAL,               -- 净资产收益率 %
    gross_margin    REAL,               -- 毛利率 %
    eps             REAL,               -- 每股收益
    bvps            REAL,               -- 每股净资产
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (market IN ('A', 'HK')),
    UNIQUE (symbol, market, report_date, report_type)
);

CREATE INDEX idx_fin_symbol ON financial_report(symbol, market);
CREATE INDEX idx_fin_date   ON financial_report(report_date);
```

**业务规则：**
- 更新频率：每周检查一次，季报期可缩短到每日
- 去重：`(symbol, market, report_date, report_type)` 唯一，INSERT OR REPLACE

#### board_info — 板块信息表

```sql
CREATE TABLE board_info (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT    NOT NULL UNIQUE,
    name        TEXT    NOT NULL,
    type        TEXT    NOT NULL,       -- industry | concept
    stock_count INTEGER NOT NULL DEFAULT 0,
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (type IN ('industry', 'concept'))
);

CREATE INDEX idx_board_info_type ON board_info(type);
CREATE INDEX idx_board_info_name ON board_info(name);
```

**业务规则：**
- 全量刷新：每日 18:00
- 支持按名称模糊搜索

#### board_constituent — 板块成分股表

```sql
CREATE TABLE board_constituent (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    board_code  TEXT    NOT NULL,
    symbol      TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    market      TEXT    NOT NULL DEFAULT 'A',
    weight      REAL,               -- 权重 %（如有）
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),

    UNIQUE (board_code, symbol)
);

CREATE INDEX idx_board_const_code   ON board_constituent(board_code);
CREATE INDEX idx_board_const_symbol ON board_constituent(symbol);
```

**业务规则：**
- 覆盖行业板块和概念板块的成分股
- 同时包含指数成分股（通过 `board_code` 前缀区分：`IDX:000300`）
- 更新频率：板块成分股每日 18:00，指数成分股按季度

#### fund_nav — 基金净值表

```sql
CREATE TABLE fund_nav (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code   TEXT    NOT NULL,
    name        TEXT    NOT NULL DEFAULT '',
    nav_date    TEXT    NOT NULL,       -- 净值日期
    nav         REAL    NOT NULL,       -- 单位净值
    acc_nav     REAL,                   -- 累计净值
    change_pct  REAL,                   -- 日涨跌幅 %

    UNIQUE (fund_code, nav_date)
);

CREATE INDEX idx_fund_nav_code ON fund_nav(fund_code);
CREATE INDEX idx_fund_nav_date ON fund_nav(nav_date);
```

**业务规则：**
- 覆盖场内 ETF 和场外基金
- 更新频率：每日晚间
- 去重：`(fund_code, nav_date)` 唯一，INSERT OR IGNORE

#### money_flow — 资金流向表

```sql
CREATE TABLE money_flow (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_type   TEXT    NOT NULL,   -- northbound | industry | concept
    entity_code TEXT    NOT NULL DEFAULT '',  -- 板块代码，northbound 时为空
    date        TEXT    NOT NULL,
    net_inflow  REAL,               -- 净流入
    main_inflow REAL,               -- 主力净流入
    retail_inflow REAL,             -- 散户净流入
    buy_amount  REAL,               -- 买入金额
    sell_amount REAL,               -- 卖出金额

    UNIQUE (flow_type, entity_code, date)
);

CREATE INDEX idx_flow_type ON money_flow(flow_type, entity_code);
CREATE INDEX idx_flow_date ON money_flow(date);
```

**业务规则：**
- `flow_type = 'northbound'` 时 `entity_code` 为空字符串
- 更新频率：交易时段每 5 分钟 / 每日收盘后
- 去重：`(flow_type, entity_code, date)` 唯一，INSERT OR REPLACE

#### margin_daily — 融资融券汇总表

```sql
CREATE TABLE margin_daily (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    date                    TEXT    NOT NULL UNIQUE,   -- 交易日 YYYY-MM-DD
    financing_balance       REAL    NOT NULL,           -- 沪深合计融资余额（元）
    securities_balance      REAL    NOT NULL DEFAULT 0, -- 沪深合计融券余额（元）
    financing_buy_amount    REAL    NOT NULL DEFAULT 0, -- 当日融资买入额（元）
    financing_balance_change REAL,                      -- 融资余额日变动（元）
    total_market_cap        REAL,                       -- 当日A股总市值（元），来自 index_valuation
    leverage_ratio          REAL,                       -- 杠杆率 = financing_balance / total_market_cap × 100%
    updated_at              TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_margin_date ON margin_daily(date);
```

**业务规则：**
- 覆盖 A 股融资融券（沪深合计），每日一条记录
- 历史深度：**10 年**（融资融券业务 2010 年启动）
- 数据源：AKShare `stock_margin_sse()` + `stock_margin_szse()` 合并计算
- `total_market_cap` 取自 `index_valuation` 表中上证指数（000001）当日的 `total_market_cap`
- `leverage_ratio` 在入库时预计算，方便查询
- 去重：`date` 唯一，INSERT OR REPLACE（当日数据可能修正）
- 排序：默认 `date DESC`，百分位计算时切换为 `date ASC`
- 存储估算：10 年 × 250 交易日 ≈ 2500 条

#### news_raw — 新闻原始数据表

```sql
CREATE TABLE news_raw (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    source       TEXT    NOT NULL,       -- jin10
    source_id    TEXT    NOT NULL UNIQUE, -- 金十新闻 ID
    title        TEXT    NOT NULL,
    content      TEXT    NOT NULL DEFAULT '',
    important    INTEGER NOT NULL DEFAULT 0,  -- 0=普通, 1=重要
    tags         TEXT    NOT NULL DEFAULT '[]',  -- JSON 数组
    publish_time TEXT    NOT NULL,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_news_source_id  ON news_raw(source_id);
CREATE INDEX idx_news_publish    ON news_raw(publish_time);
CREATE INDEX idx_news_important  ON news_raw(important);
```

**业务规则：**
- MVP 阶段仅使用金十数据（`source = 'jin10'`）
- TTL：72 小时，超时自动清理
- 去重：`source_id` 唯一，INSERT OR IGNORE
- 排序：`publish_time DESC`

#### macro_event — 宏观经济事件表

```sql
CREATE TABLE macro_event (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT    NOT NULL,   -- interest_rate | economic_data | policy
    country         TEXT    NOT NULL,   -- USA | CHN | JPN | GBR | EUR | KOR | FRA | DEU
    event_name      TEXT    NOT NULL,   -- 美联储利率决议 | 中国CPI | 美国非农就业
    event_date      TEXT    NOT NULL,   -- YYYY-MM-DD
    actual_value    TEXT,               -- 实际值，如 "4.25%"
    forecast_value  TEXT,               -- 预测值
    previous_value  TEXT,               -- 前值
    unit            TEXT,               -- % | 万人 | 亿元
    is_released     INTEGER NOT NULL DEFAULT 0,  -- 0=未发布 1=已发布
    source          TEXT    NOT NULL DEFAULT 'akshare',  -- akshare | jin10 | manual
    source_event_id TEXT,               -- 数据源原始ID（如有）
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (event_type IN ('interest_rate', 'economic_data', 'policy')),
    CHECK (country IN ('USA', 'CHN', 'JPN', 'GBR', 'EUR', 'KOR', 'FRA', 'DEU')),
    UNIQUE (country, event_name, event_date)
);

CREATE INDEX idx_macro_event_date     ON macro_event(event_date);
CREATE INDEX idx_macro_event_country  ON macro_event(country);
CREATE INDEX idx_macro_event_type     ON macro_event(event_type);
CREATE INDEX idx_macro_event_released ON macro_event(is_released, event_date);
```

**业务规则：**
- 数据来源：AKShare 央行利率 + 宏观经济数据接口
- 去重：`(country, event_name, event_date)` 唯一，INSERT OR REPLACE（同一事件可能修正）
- 排序：`event_date DESC`
- 预测事件：`is_released = 0`，`actual_value = NULL`，通过 `event_schedule` 规则表推算
- 历史数据保留：不做 TTL 清理，作为长期参考

#### event_schedule — 事件周期规则配置表

```sql
CREATE TABLE event_schedule (
    event_key       TEXT    PRIMARY KEY,   -- fed_interest_rate | china_lpr | ...
    event_name      TEXT    NOT NULL,      -- 中文名称
    country         TEXT    NOT NULL,      -- USA | CHN | JPN | EUR
    event_type      TEXT    NOT NULL,      -- interest_rate | economic_data
    frequency_desc  TEXT    NOT NULL,      -- 周期描述
    next_calc_rule  TEXT    NOT NULL,      -- 预设规则名
    is_active       INTEGER NOT NULL DEFAULT 1,
    priority        INTEGER NOT NULL DEFAULT 50,
    source          TEXT    NOT NULL DEFAULT 'cron',  -- cron(MVP) | agent(扩展)
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

**业务规则：**
- `source` 字段标识该事件的数据获取方式：`cron` = 后端定时任务直接获取，`agent` = AI Agent 爬取推送
- MVP 阶段仅启用 `source='cron'` 的利率事件（4 个）
- `source='agent'` 的事件预置但不启用，待 Agent 扩展上线后激活
- 规则格式：`next_calc_rule` 存储预设规则名，Python 代码中实现对应函数

**MVP 预置数据（4 个利率事件，source=cron）：**

| event_key | event_name | country | frequency_desc | next_calc_rule | source |
|-----------|-----------|---------|---------------|----------------|--------|
| `fed_interest_rate` | 美联储利率决议 | USA | 每年8次（约6-7周） | `next_fomc_date` | cron |
| `china_lpr` | 中国LPR报价 | CHN | 每月20日 | `next_month_20th` | cron |
| `ecb_interest_rate` | 欧洲央行利率决议 | EUR | 每年8次 | `next_ecb_date` | cron |
| `boj_interest_rate` | 日本央行利率决议 | JPN | 每年8次 | `next_boj_date` | cron |

**Agent 扩展预置数据（8 个指标，source=agent，不启用）：**

| event_key | event_name | country | frequency_desc | next_calc_rule | source |
|-----------|-----------|---------|---------------|----------------|--------|
| `usa_cpi` | 美国CPI | USA | 每月中旬 | `next_month_mid` | agent |
| `usa_unemployment` | 美国失业率 | USA | 每月第一个周五 | `next_first_friday` | agent |
| `china_cpi` | 中国CPI | CHN | 每月中旬 | `next_month_mid` | agent |
| `china_unemployment` | 中国城镇调查失业率 | CHN | 季度 | `next_quarterly` | agent |
| `japan_cpi` | 日本CPI | JPN | 每月下旬 | `next_month_late` | agent |
| `japan_unemployment` | 日本失业率 | JPN | 每月末 | `next_month_end` | agent |
| `euro_cpi` | 欧元区CPI | EUR | 每月初 | `next_month_early` | agent |
| `euro_unemployment` | 欧元区失业率 | EUR | 每月初 | `next_month_early` | agent |

#### data_sync_log — 数据同步日志表

```sql
CREATE TABLE data_sync_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id         TEXT    NOT NULL UNIQUE,
    task_type       TEXT    NOT NULL,   -- init_index | init_symbol | init_board | daily_kline | valuation | financial | news | flow | margin
    target          TEXT    NOT NULL,   -- 标的代码或板块代码
    status          TEXT    NOT NULL DEFAULT 'queued',  -- queued | running | completed | failed
    progress        INTEGER NOT NULL DEFAULT 0,         -- 0-100
    total_records   INTEGER NOT NULL DEFAULT 0,
    loaded_records  INTEGER NOT NULL DEFAULT 0,
    error_message   TEXT,
    started_at      TEXT,
    finished_at     TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),

    CHECK (status IN ('queued', 'running', 'completed', 'failed'))
);

CREATE INDEX idx_sync_log_status ON data_sync_log(status);
CREATE INDEX idx_sync_log_type   ON data_sync_log(task_type);
CREATE INDEX idx_sync_log_target ON data_sync_log(target);
```

**业务规则：**
- 记录每次数据拉取任务的状态和进度
- 支持查询任务进度和历史记录
- 失败任务记录 error_message，便于排查

### 3.3 预置数据

#### 核心指数清单（硬编码，不存数据库）

系统首次部署时自动拉取以下 10 个核心指数的 20 年日 K 线：

| # | 市场 | 指数代码 | 指数名称 | AKShare 接口符号 | 估值数据可用性 | 备注 |
|---|------|---------|---------|-----------------|--------------|------|
| 1 | A股 | 000001 | 上证指数 | `000001` | ✅ PE/PB | 国证指数提供 |
| 2 | A股 | 000300 | 沪深300 | `000300` | ✅ PE/PB | 国证指数提供 |
| 3 | A股 | 000905 | 中证500 | `000905` | ✅ PE/PB | 国证指数提供 |
| 4 | A股 | 399006 | 创业板指 | `399006` | ✅ PE/PB | 国证指数提供 |
| 5 | A股 | 000688 | 科创50 | `000688` | ✅ PE/PB | 国证指数提供 |
| 6 | A股 | 930050 | 中证A500 | `930050` | ✅ PE/PB | 国证指数提供 |
| 7 | 港股 | HSI | 恒生指数 | `恒生指数` | ⚠️ 仅价格 | 无免费 PE/PB 历史接口 |
| 8 | 港股 | HSTECH | 恒生科技 | `恒生科技指数` | ⚠️ 仅价格 | 无免费 PE/PB 历史接口 |
| 9 | 美股 | SPX | 标普500 | `标普500` | ⚠️ 仅价格 | 无免费 PE/PB 历史接口 |
| 10 | 美股 | IXIC | 纳斯达克 | `纳斯达克` | ⚠️ 仅价格 | 无免费 PE/PB 历史接口 |

> **估值数据说明：**
> - A股指数（000001-930050）：通过 AKShare `index_all_cni()` 获取每日 PE/PB，存入 `index_valuation` 表
> - 港股/美股指数（HSI/SPX/IXIC）：AKShare `index_global_hist_em()` 只提供价格数据，无 PE/PB。MVP 阶段以**价格百分位**进行估值判断，后续版本补充 PE/PB 数据

```sql
-- 同步日志示例（首次部署时自动创建）
INSERT INTO data_sync_log (task_id, task_type, target, status)
VALUES ('init_core_indices_20260507', 'init_index', 'core_10', 'queued');
```

