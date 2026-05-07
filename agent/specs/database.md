# 数据库设计规范

> Strategy Compass 使用 SQLite，本规范定义表设计、索引、迁移和命名约定。

## 1. 命名约定

| 对象 | 命名方式 | 示例 |
|------|---------|------|
| 表名 | `snake_case`，复数形式 | `stock_daily_kline` |
| 列名 | `snake_case` | `financing_balance` |
| 索引名 | `idx_{table}_{column}` | `idx_stock_kline_symbol` |
| 外键约束 | `fk_{table}_{ref_table}` | `fk_board_const_board` |
| 唯一约束 | `{table}_{column}_unique` | — |

## 2. 表设计规范

### 2.1 每个表必须有的字段

```sql
id          INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
created_at  TEXT DEFAULT (datetime('now'))       -- 创建时间
```

### 2.2 时间字段规范

| 场景 | 字段名 | 类型 | 格式 |
|------|--------|------|------|
| 日期（交易日） | `date` | TEXT | `YYYY-MM-DD` |
| 时间戳 | `created_at` / `updated_at` | TEXT | `YYYY-MM-DD HH:MM:SS` |
| 报告期 | `report_date` | TEXT | `YYYY-MM-DD` |

### 2.3 金额/价格字段

- 统一使用 `REAL` 类型
- 单位：元（人民币）
- 存储原始数值，不格式化

### 2.4 枚举字段

使用 CHECK 约束限制取值范围：

```sql
market TEXT NOT NULL CHECK (market IN ('A', 'HK', 'GIDX')),
type   TEXT NOT NULL CHECK (type IN ('industry', 'concept')),
```

## 3. 索引策略

### 3.1 必须加索引的场景

- 外键字段
- 频繁查询的过滤条件字段
- 频繁排序的字段
- 联合唯一约束的字段

### 3.2 索引示例

```sql
-- 单字段索引
CREATE INDEX idx_stock_kline_symbol ON stock_daily_kline(symbol);

-- 复合索引（查询时按 symbol → date 顺序过滤）
CREATE INDEX idx_stock_kline_symbol_date ON stock_daily_kline(symbol, date);

-- 覆盖索引（查询只需要索引中的字段）
CREATE INDEX idx_index_val_symbol_date ON index_valuation(symbol, date, pe_ttm, pb);
```

### 3.3 索引原则

- 索引不是越多越好，写入会变慢
- 优先复合索引，减少单列索引数量
- 定期用 `EXPLAIN QUERY PLAN` 检查查询是否命中索引

## 4. 去重策略

| 数据类型 | 唯一键 | 去重方式 | 说明 |
|---------|--------|---------|------|
| 历史 K 线 | `(symbol, market, date)` | INSERT OR IGNORE | 历史数据不修改 |
| 估值数据 | `(symbol, market, date)` | INSERT OR REPLACE | 当日可能修正 |
| 财务报表 | `(symbol, market, report_date, report_type)` | INSERT OR REPLACE | 财报可能更正 |
| 新闻 | `source_id` | INSERT OR IGNORE | 新闻不会修改 |
| 融资融券 | `date` | INSERT OR REPLACE | 当日可能修正 |
| 板块列表 | `code` | INSERT OR REPLACE | 板块信息更新 |

## 5. 迁移规范

### 5.1 初始迁移

在 `scripts/init_db.py` 中定义所有 CREATE TABLE 语句：

```python
# scripts/init_db.py
import sqlite3

INIT_SQL = """
CREATE TABLE IF NOT EXISTS stock_daily_kline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol      TEXT    NOT NULL,
    market      TEXT    NOT NULL CHECK (market IN ('A', 'HK')),
    date        TEXT    NOT NULL,
    open        REAL    NOT NULL,
    high        REAL    NOT NULL,
    low         REAL    NOT NULL,
    close       REAL    NOT NULL,
    volume      INTEGER NOT NULL DEFAULT 0,
    turnover    REAL    NOT NULL DEFAULT 0,
    change_pct  REAL,
    created_at  TEXT    DEFAULT (datetime('now')),
    UNIQUE (symbol, market, date)
);

CREATE INDEX IF NOT EXISTS idx_stock_kline_symbol ON stock_daily_kline(symbol, market);
CREATE INDEX IF NOT EXISTS idx_stock_kline_date ON stock_daily_kline(date);
"""

def init_db(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.executescript(INIT_SQL)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db('data/strategy_compass.db')
```

### 5.2 增量迁移

新增表或字段时，编写单独的迁移脚本：

```python
# scripts/migrations/20260507_add_margin_table.py
MIGRATION_SQL = """
CREATE TABLE IF NOT EXISTS margin_daily (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    date                    TEXT    NOT NULL UNIQUE,
    financing_balance       REAL    NOT NULL,
    securities_balance      REAL    NOT NULL DEFAULT 0,
    financing_buy_amount    REAL    NOT NULL DEFAULT 0,
    financing_balance_change REAL,
    total_market_cap        REAL,
    leverage_ratio          REAL,
    updated_at              TEXT    DEFAULT (datetime('now')),
    created_at              TEXT    DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_margin_date ON margin_daily(date);
"""
```

## 6. SQLite 优化

### 6.1 WAL 模式

开发环境和生产环境都启用 WAL 模式：

```python
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
```

### 6.2 连接池

使用 SQLAlchemy 的连接池：

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/strategy_compass.db'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'check_same_thread': False,
    },
    'pool_pre_ping': True,
}
```

## 7. 数据清理

### 7.1 TTL 清理

```python
def cleanup_expired_news():
    """清理 72 小时前的新闻。"""
    cutoff = datetime.now() - timedelta(hours=72)
    NewsRaw.query.filter(NewsRaw.publish_time < cutoff).delete()
    db.session.commit()
```

### 7.2 清理时机

- 新闻：每日凌晨清理 72h+ 的数据
- 同步日志：保留最近 30 天
- 错误日志：保留最近 7 天
