from app import db


class IndexInfo(db.Model):
    __tablename__ = "index_info"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(20))
    description = db.Column(db.Text)
    is_core = db.Column(db.Boolean, default=False)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.CheckConstraint("market IN ('A', 'HK', 'US', 'GIDX')"),
    )


class IndexDailyKline(db.Model):
    __tablename__ = "index_daily_kline"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Text, nullable=False)
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, default=0)
    turnover = db.Column(db.Float, default=0)
    change_pct = db.Column(db.Float)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.UniqueConstraint("symbol", "market", "date"),
        db.Index("idx_index_kline_symbol", "symbol", "market"),
        db.Index("idx_index_kline_date", "date"),
    )


class StockDailyKline(db.Model):
    __tablename__ = "stock_daily_kline"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Text, nullable=False)
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, default=0)
    turnover = db.Column(db.Float, default=0)
    change_pct = db.Column(db.Float)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.UniqueConstraint("symbol", "market", "date"),
        db.Index("idx_stock_kline_symbol", "symbol", "market"),
        db.Index("idx_stock_kline_date", "date"),
    )


class BoardDailyKline(db.Model):
    __tablename__ = "board_daily_kline"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Text, nullable=False)
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, default=0)
    turnover = db.Column(db.Float, default=0)
    change_pct = db.Column(db.Float)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.UniqueConstraint("symbol", "market", "date"),
        db.Index("idx_board_kline_symbol", "symbol", "market"),
        db.Index("idx_board_kline_date", "date"),
    )


class IndexValuation(db.Model):
    __tablename__ = "index_valuation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Text, nullable=False)
    pe_ttm = db.Column(db.Float)
    pb = db.Column(db.Float)
    ps = db.Column(db.Float)
    dividend_yield = db.Column(db.Float)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.UniqueConstraint("symbol", "market", "date"),
        db.Index("idx_index_val_symbol", "symbol", "market"),
        db.Index("idx_index_val_date", "date"),
    )


class StockValuation(db.Model):
    __tablename__ = "stock_valuation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Text, nullable=False)
    pe_ttm = db.Column(db.Float)
    pb = db.Column(db.Float)
    ps = db.Column(db.Float)
    dividend_yield = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.UniqueConstraint("symbol", "market", "date"),
        db.Index("idx_stock_val_symbol", "symbol", "market"),
        db.Index("idx_stock_val_date", "date"),
    )


class BoardValuation(db.Model):
    __tablename__ = "board_valuation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Text, nullable=False)
    pe_ttm = db.Column(db.Float)
    pb = db.Column(db.Float)
    ps = db.Column(db.Float)
    dividend_yield = db.Column(db.Float)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.UniqueConstraint("symbol", "market", "date"),
        db.Index("idx_board_val_symbol", "symbol", "market"),
        db.Index("idx_board_val_date", "date"),
    )


class MarginDaily(db.Model):
    __tablename__ = "margin_daily"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Text, nullable=False, unique=True)
    financing_balance = db.Column(db.Float, nullable=False)
    securities_balance = db.Column(db.Float, default=0)
    financing_buy_amount = db.Column(db.Float, default=0)
    financing_balance_change = db.Column(db.Float)
    total_market_cap = db.Column(db.Float)
    leverage_ratio = db.Column(db.Float)
    updated_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )


class NewsRaw(db.Model):
    __tablename__ = "news_raw"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source = db.Column(db.String(32), nullable=False, default="jin10")
    source_id = db.Column(db.String(64), nullable=False, unique=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    url = db.Column(db.Text)
    publish_time = db.Column(db.Text, nullable=False)
    importance = db.Column(db.Integer, default=1)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.Index("idx_news_publish_time", "publish_time"),
        db.Index("idx_news_source", "source"),
    )


class MacroEvent(db.Model):
    """宏观经济事件：央行利率决议、经济数据发布等。"""

    __tablename__ = "macro_event"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(32), nullable=False)
    country = db.Column(db.String(16), nullable=False)
    event_name = db.Column(db.String(128), nullable=False)
    event_date = db.Column(db.Text, nullable=False)
    actual_value = db.Column(db.Text)
    forecast_value = db.Column(db.Text)
    previous_value = db.Column(db.Text)
    unit = db.Column(db.String(16))
    is_released = db.Column(db.Boolean, nullable=False, default=False)
    source = db.Column(db.String(32), nullable=False, default="akshare")
    source_event_id = db.Column(db.Text)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )
    updated_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.CheckConstraint(
            "event_type IN ('interest_rate', 'economic_data', 'policy')"
        ),
        db.CheckConstraint(
            "country IN ('USA', 'CHN', 'JPN', 'GBR', 'EUR', 'KOR', 'FRA', 'DEU')"
        ),
        db.UniqueConstraint("country", "event_name", "event_date"),
        db.Index("idx_macro_event_date", "event_date"),
        db.Index("idx_macro_event_country", "country"),
        db.Index("idx_macro_event_type", "event_type"),
        db.Index(
            "idx_macro_event_released", "is_released", "event_date"
        ),
    )


class EventSchedule(db.Model):
    """事件周期规则配置：定义各类宏观事件的发布周期，用于推算下一次事件时间。"""

    __tablename__ = "event_schedule"

    event_key = db.Column(db.String(32), primary_key=True)
    event_name = db.Column(db.String(128), nullable=False)
    country = db.Column(db.String(16), nullable=False)
    event_type = db.Column(db.String(32), nullable=False)
    frequency_desc = db.Column(db.Text, nullable=False)
    next_calc_rule = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.Integer, nullable=False, default=50)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.CheckConstraint(
            "event_type IN ('interest_rate', 'economic_data', 'policy')"
        ),
        db.CheckConstraint(
            "country IN ('USA', 'CHN', 'JPN', 'GBR', 'EUR', 'KOR', 'FRA', 'DEU')"
        ),
    )


class DataSyncLog(db.Model):
    __tablename__ = "data_sync_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_name = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(16), nullable=False)
    detail = db.Column(db.Text)
    started_at = db.Column(db.Text, nullable=False)
    finished_at = db.Column(db.Text)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.CheckConstraint("status IN ('running', 'success', 'failed')"),
    )
