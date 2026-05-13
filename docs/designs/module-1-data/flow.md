---
title: "Module 1: 数据底座 — 接口与数据模型设计"
type: spec
module: module-1
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

## 4. 核心业务逻辑

### 4.1 行情获取流程

```python
class QuoteService:

    def get_stock_quote(self, symbol: str, market: str = 'A') -> dict:
        # 1. 查内存缓存
        cache_key = f"quote:{market}:{symbol}"
        cached = memory_cache.get(cache_key)
        if cached and not cached.is_expired(ttl=60):
            return cached

        # 2. 查 SQLite 最新快照
        latest = StockDailyKline.query.filter_by(
            symbol=symbol, market=market
        ).order_by(desc('date')).first()

        # 3. 如果是交易时段且快照超过 60 秒，调用外部源刷新
        if is_trading_hours() and (not latest or latest.date == today()):
            fresh = akshare.get_stock_realtime(symbol, market)
            if fresh:
                # 更新内存缓存
                memory_cache.set(cache_key, fresh, ttl=60)
                # 更新 SQLite 当日快照
                self._upsert_daily_kline(fresh)
                return fresh

        # 4. 非交易时段或无新数据，返回缓存
        return latest.to_dict() if latest else None
```

### 4.2 历史 K 线拉取流程

```python
class KlineService:

    def fetch_historical_klines(self, symbol: str, market: str,
                                 depth_years: int = 10) -> str:
        """
        触发历史 K 线拉取任务。
        返回 task_id，前端可通过任务接口查询进度。
        """
        task_id = generate_task_id()
        # 创建同步日志
        DataSyncLog.create(task_id=task_id, task_type='init_symbol',
                          target=f"{market}:{symbol}", status='queued')

        # 提交到后台任务队列
        task_queue.enqueue(self._do_fetch_klines,
                          task_id, symbol, market, depth_years)
        return task_id

    def _do_fetch_klines(self, task_id, symbol, market, depth_years):
        log = DataSyncLog.query.filter_by(task_id=task_id).first()
        log.status = 'running'
        log.started_at = now()
        log.save()

        try:
            # 调用 AKShare 拉取历史数据
            df = akshare.get_stock_hist(symbol, market,
                                        years=depth_years)
            log.total_records = len(df)

            for i, row in df.iterrows():
                # INSERT OR IGNORE 去重
                StockDailyKline.insert_or_ignore(
                    symbol=symbol, market=market,
                    date=row['date'], open=row['open'],
                    high=row['high'], low=row['low'],
                    close=row['close'], volume=row['volume'],
                    turnover=row['turnover']
                )
                log.loaded_records = i + 1
                log.progress = int((i + 1) / len(df) * 100)
                if i % 100 == 0:
                    log.save()  # 每 100 条更新一次进度

                # 限流：每条间隔 0.5 秒
                time.sleep(0.5)

            log.status = 'completed'
            log.finished_at = now()
            log.save()

        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)
            log.finished_at = now()
            log.save()
```

### 4.3 定时刷新调度

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# 每日 16:30 — K 线增量更新
scheduler.add_job(daily_kline_update, 'cron',
                  hour=16, minute=30, day_of_week='mon-fri')

# 每日 18:00 — 估值 + 板块刷新
scheduler.add_job(daily_valuation_update, 'cron',
                  hour=18, minute=0, day_of_week='mon-fri')

# 每 30 分钟 — 新闻拉取
scheduler.add_job(news_fetch_incremental, 'interval',
                  minutes=30)

# 每日 08:00 — 宏观利率同步（MVP 仅利率，CPI/失业率等由 Agent 扩展负责）
scheduler.add_job(macro_event_sync, 'cron',
                  hour=8, minute=0)

# 每周一 10:00 — 财务报表检查
scheduler.add_job(weekly_financial_check, 'cron',
                  hour=10, minute=0, day_of_week='mon')

def daily_kline_update():
    """增量更新所有已入库标的的日 K"""
    # 1. 更新 10 个核心指数
    for idx in CORE_INDICES:
        fetch_latest_kline(idx.symbol, idx.market, type='index')

    # 2. 更新所有用户自选股（从 Module 0 获取）
    symbols = get_all_user_watchlist_symbols()
    for sym in symbols:
        fetch_latest_kline(sym.symbol, sym.market, type='stock')
        time.sleep(0.5)  # 限流

    # 3. 更新所有用户关注板块
    boards = get_all_user_sector_favorites()
    for board in boards:
        fetch_latest_kline(board.code, type='board')
        time.sleep(0.5)
```

#### 宏观利率同步流程（MVP — 仅利率）

```python
def macro_event_sync():
    """
    MVP 阶段：仅同步中美日欧央行利率决议。
    CPI/失业率等宏观经济指标由 Agent 扩展负责（见 4.5 节）。
    """
    import akshare as ak

    # 1. 央行利率决议同步（中美日欧 4 个）
    interest_rates = [
        ('USA', '美联储利率决议', ak.macro_bank_usa_interest_rate),
        ('CHN', 'LPR报价', ak.macro_china_lpr),
        ('JPN', '日本央行利率决议', ak.macro_bank_japan_interest_rate),
        ('EUR', '欧洲央行利率决议', ak.macro_bank_euro_interest_rate),
    ]

    for country, name, func in interest_rates:
        try:
            df = func()
            for _, row in df.iterrows():
                MacroEvent.insert_or_replace(
                    event_type='interest_rate',
                    country=country,
                    event_name=name,
                    event_date=row['日期'],
                    actual_value=str(row['今值']),
                    forecast_value=str(row['预测值']) if pd.notna(row['预测值']) else None,
                    previous_value=str(row['前值']) if pd.notna(row['前值']) else None,
                    unit='%',
                    is_released=1,
                    source='akshare'
                )
        except Exception as e:
            logger.error(f"同步 {name} 失败: {e}")

    # 2. 推算下一次利率决议时间（仅利率事件）
    schedules = EventSchedule.query.filter_by(
        is_active=1, event_type='interest_rate'
    ).all()
    for sched in schedules:
        latest = MacroEvent.query.filter_by(
            country=sched.country,
            event_name=sched.event_name,
            is_released=1
        ).order_by(MacroEvent.event_date.desc()).first()

        if latest:
            next_date = calc_next_date(sched.next_calc_rule, latest.event_date)
            if next_date:
                MacroEvent.insert_or_replace(
                    event_type='interest_rate',
                    country=sched.country,
                    event_name=sched.event_name,
                    event_date=next_date,
                    actual_value=None,
                    forecast_value=None,
                    previous_value=latest.actual_value,
                    unit=latest.unit,
                    is_released=0,
                    source='predicted'
                )
```

### 4.4 用户添加自选触发流程

```python
def on_user_add_watchlist_item(user_id: int, symbol: str,
                                market: str, asset_type: str):
    """
    Module 0 添加自选股后，触发 Module 1 数据初始化。
    通过事件机制或直接调用实现。
    """
    # 检查该标的是否已有历史数据
    exists = StockDailyKline.query.filter_by(
        symbol=symbol, market=market
    ).first()

    if not exists:
        # 首次添加，触发历史数据拉取
        task_id = kline_service.fetch_historical_klines(
            symbol=symbol, market=market, depth_years=10
        )
        return {"status": "data_loading", "task_id": task_id}

    return {"status": "data_ready"}
```

### 4.5 Agent 扩展：宏观数据智能采集（v2.0）

> 本节为设计预留，v2.0 版本实现。MVP 阶段仅实现利率同步（4.3 节）。

#### 背景

MVP 阶段验证发现：AKShare 等直接 API 的宏观数据（CPI/失业率等）普遍滞后 8-9 个月，不可用于生产展示。因此采用 AI Agent 爬取方案替代：

| 对比维度 | 直连 API（MVP 利率） | Agent 爬取（v2.0 扩展） |
|---------|---------------------|------------------------|
| 数据及时性 | 依赖 API 更新频率 | Agent 从权威网站实时抓取 |
| 数据源 | 单一 API | TradingEconomics / 官方统计局等 |
| 可靠性 | 高（结构化数据） | 中（需 LLM 解析 + sanity check） |
| 扩展成本 | 新指标需写代码 | 新指标只需更新 Agent 采集指令 |
| 实现方式 | 后端 cron 定时任务 | OpenClaw cron + agentTurn |

#### 架构

```
┌──────────────────────┐
│ 后端 cron 定时任务    │──→ 利率同步（MVP，AKShare/FRED）
│ macro_event_sync()   │──→ POST /api/v1/data/macro/events
└──────────────────────┘

┌──────────────────────┐
│ OpenClaw Agent       │──→ 爬取网页 + LLM 解析（v2.0）
│ (isolated agentTurn) │──→ POST /api/v1/data/macro/events
└──────────────────────┘
```

两者共用同一个 API 入口，后端不区分数据来源。

#### Agent 工作流程

1. 查询后端 `GET /api/v1/data/macro/events/latest`，检查各指标上次更新时间
2. 根据 `event_schedule` 中 `source='agent'` 的条目，判断哪些指标需要更新
3. 针对需要更新的指标，用 `web_fetch` 抓取数据源网页
4. LLM 解析提取数值、日期、单位
5. Sanity check 验证（范围检查 + 变化量限制）
6. 通过 POST 推送到后端 API

#### 数据源清单

| 指标 | 爬取目标 | 更新频率 |
|------|---------|---------|
| 🇺🇸 CPI YoY | TradingEconomics / investing.com | 月度，每月 10-15 日 |
| 🇺🇸 失业率 | TradingEconomics / BLS | 月度，每月第 1 个周五 |
| 🇨🇳 CPI YoY | 国家统计局 / 东方财富 | 月度，每月 9-10 日 |
| 🇨🇳 城镇调查失业率 | 国家统计局 | 季度，季后发布 |
| 🇯🇵 CPI YoY | TradingEconomics | 月度，每月 20-25 日 |
| 🇯🇵 失业率 | TradingEconomics | 月度，每月最后一周周五 |
| 🇪🇺 CPI YoY | TradingEconomics | 月度，每月初 |
| 🇪🇺 失业率 | TradingEconomics | 月度 |

#### Sanity Check 规则

```python
SANITY_RULES = {
    "cpi_yoy":      {"min": -5,  "max": 20,  "max_delta": 3.0},
    "unemployment": {"min": 0,   "max": 30,  "max_delta": 2.0},
    "interest_rate": {"min": -1, "max": 20,  "max_delta": 1.0},
}
```

#### 后端 API 扩展

v2.0 新增统一宏观数据写入接口（Agent 和 cron 共用）：

**POST /api/v1/data/macro/events**

```json
{
  "indicator": "cpi_yoy",
  "country": "USA",
  "value": 2.6,
  "unit": "percent",
  "ref_date": "2026-03",
  "release_date": "2026-04-10",
  "source": "tradingeconomics",
  "confidence": 0.95
}
```

后端验证：indicator 白名单 → value 范围检查 → 变化量检查 → UPSERT。

