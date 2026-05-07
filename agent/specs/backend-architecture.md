# 后端架构规范

> Strategy Compass 后端采用 Flask + SQLite 架构，本规范定义代码组织方式和分层职责。

## 1. 项目结构

```
backend/
├── app/                    # 应用核心
│   ├── __init__.py         # Flask 应用工厂
│   ├── models/             # 数据模型层（SQLAlchemy）
│   │   ├── __init__.py
│   │   ├── user.py         # Module 0 用户相关模型
│   │   ├── data.py         # Module 1 数据相关模型
│   │   └── valuation.py    # Module 4 估值相关模型
│   ├── services/           # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Module 0 认证
│   │   ├── watchlist_service.py  # Module 0 自选股
│   │   ├── quote_service.py      # Module 1 行情
│   │   ├── kline_service.py      # Module 1 K线
│   │   ├── data_sync_service.py  # Module 1 数据同步
│   │   ├── news_service.py       # Module 2 新闻
│   │   ├── market_service.py     # Module 3 市场概览
│   │   └── valuation_service.py  # Module 4 估值计算
│   ├── routes/             # API 路由层（Flask Blueprint）
│   │   ├── __init__.py
│   │   ├── auth.py         # Module 0 认证路由
│   │   ├── user.py         # Module 0 用户路由
│   │   ├── data.py         # Module 1 数据路由
│   │   ├── news.py         # Module 2 新闻路由
│   │   ├── market.py       # Module 3 市场路由
│   │   └── valuation.py    # Module 4 估值路由
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── cache.py        # 内存缓存
│   │   ├── decorators.py   # 装饰器（@auth_required 等）
│   │   ├── response.py     # 统一响应格式
│   │   └── validators.py   # 参数校验
│   └── config.py           # 配置管理
├── data/                   # SQLite 数据文件目录
│   └── strategy_compass.db
├── scripts/                # 管理脚本
│   ├── init_db.py          # 数据库初始化
│   └── daily_sync.py       # 每日数据同步
├── tests/                  # 测试
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_data.py
│   └── test_valuation.py
├── requirements.txt        # Python 依赖
├── Dockerfile
└── wsgi.py                 # 入口文件
```

## 2. 分层职责

### 2.1 Model 层（数据访问）

- 定义 SQLAlchemy 模型类
- 封装基础 CRUD 操作
- **不做业务逻辑**

```python
# app/models/data.py
from app import db

class IndexDailyKline(db.Model):
    __tablename__ = 'index_daily_kline'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, default=0)
    turnover = db.Column(db.Float, default=0)
    change_pct = db.Column(db.Float)

    __table_args__ = (
        db.UniqueConstraint('symbol', 'market', 'date'),
        db.Index('idx_index_kline_symbol', 'symbol', 'market'),
        db.Index('idx_index_kline_date', 'date'),
    )
```

### 2.2 Service 层（业务逻辑）

- 实现核心业务逻辑
- 协调多个 Model 的操作
- 封装外部 API 调用（AKShare 等）
- **不直接处理 HTTP 请求/响应**

```python
# app/services/valuation_service.py
class ValuationService:

    def get_index_valuation(self, symbol: str, window_years: int = 10) -> dict:
        """获取单个指数的完整估值分析。"""
        # 1. 获取历史 K 线
        klines = self._get_klines(symbol, window_years)
        # 2. 获取历史估值
        valuations = self._get_valuations(symbol, window_years)
        # 3. 计算百分位
        pe_percentile = self._calc_percentile(valuations[-1].pe_ttm, [v.pe_ttm for v in valuations])
        # 4. 计算风险指标
        risk = self._calc_risk_metrics(klines)
        # 5. 组装结果
        return {
            "symbol": symbol,
            "valuation": { ... },
            "risk": risk,
        }
```

### 2.3 Route 层（API 路由）

- 定义 Flask Blueprint 路由
- 解析请求参数
- 调用 Service 层
- 格式化响应
- **不做业务逻辑**

```python
# app/routes/valuation.py
from flask import Blueprint, request, g
from app.services.valuation_service import ValuationService
from app.utils.decorators import auth_required
from app.utils.response import success, error

bp = Blueprint('valuation', __name__, url_prefix='/api/v4/valuation')
valuation_service = ValuationService()

@bp.route('/index/<symbol>')
@auth_required
def get_index_valuation(symbol: str):
    window_years = request.args.get('window_years', 10, type=int)
    try:
        result = valuation_service.get_index_valuation(symbol, window_years)
        return success(result)
    except SymbolNotFound:
        return error("SYMBOL_NOT_FOUND", "标的代码不存在", 404)
    except InsufficientData:
        return error("INSUFFICIENT_DATA", "历史数据不足", 422)
```

## 3. 模块间调用规范

### 3.1 同进程内调用

模块间调用使用 Service 实例直接调用：

```python
# Module 3 调用 Module 4
from app.services.valuation_service import ValuationService

class MarketService:
    def __init__(self):
        self.valuation_service = ValuationService()

    def get_overview(self, user_id: int):
        # 直接调用 Module 4 Service
        market_val = self.valuation_service.get_market_valuation()
        ...
```

### 3.2 跨模块数据流

```
Route (Module 3) → Service (Module 3) → Service (Module 4) → Service (Module 1) → Model (Module 1) → SQLite
```

## 4. 配置管理

使用 Python 类管理配置：

```python
# app/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data/strategy_compass.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRE_DAYS = 7
    CACHE_TTL = 60
    AKSHARE_CALL_INTERVAL = 0.5

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
```

## 5. 工具函数规范

### 5.1 统一响应格式

```python
# app/utils/response.py
from flask import jsonify

def success(data, message="success"):
    return jsonify({"data": data, "message": message})

def error(code, message, status_code=400):
    response = jsonify({"error": {"code": code, "message": message}})
    response.status_code = status_code
    return response
```

### 5.2 认证装饰器

```python
# app/utils/decorators.py
from functools import wraps
from flask import request, g
import jwt

class auth_required:
    def __call__(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return error("UNAUTHORIZED", "未提供 Token", 401)
            try:
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                g.current_user = User.query.get(payload['user_id'])
            except jwt.ExpiredSignatureError:
                return error("TOKEN_EXPIRED", "Token 已过期", 401)
            except jwt.InvalidTokenError:
                return error("UNAUTHORIZED", "Token 无效", 401)
            return f(*args, **kwargs)
        return decorated
```

## 6. 错误处理

### 6.1 自定义异常

```python
# app/utils/exceptions.py
class AppException(Exception):
    def __init__(self, code, message, status_code=400):
        self.code = code
        self.message = message
        self.status_code = status_code

class SymbolNotFound(AppException):
    def __init__(self):
        super().__init__("SYMBOL_NOT_FOUND", "标的代码不存在", 404)

class DataNotReady(AppException):
    def __init__(self):
        super().__init__("DATA_NOT_READY", "数据正在初始化中", 409)

class InsufficientData(AppException):
    def __init__(self):
        super().__init__("INSUFFICIENT_DATA", "历史数据不足", 422)
```

### 6.2 全局错误处理

```python
# app/__init__.py
@app.errorhandler(AppException)
def handle_app_exception(e):
    return error(e.code, e.message, e.status_code)

@app.errorhandler(500)
def handle_internal_error(e):
    app.logger.error(f"Internal error: {e}")
    return error("INTERNAL_ERROR", "服务器内部错误", 500)
```

## 7. 缓存使用

### 7.1 内存缓存

```python
# app/utils/cache.py
import time
from threading import Lock

class MemoryCache:
    def __init__(self):
        self._cache = {}
        self._lock = Lock()

    def get(self, key):
        with self._lock:
            item = self._cache.get(key)
            if item and item['expire_at'] > time.time():
                return item['value']
            return None

    def set(self, key, value, ttl=60):
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expire_at': time.time() + ttl,
            }

memory_cache = MemoryCache()
```

### 7.2 使用场景

| 数据类型 | 缓存方式 | TTL |
|---------|---------|-----|
| 实时行情 | 内存缓存 | 60s |
| 估值计算结果 | 内存缓存 | 1h |
| 板块列表 | 内存缓存 | 1h |
| 历史 K 线 | SQLite（永久） | 无 |

## 8. 定时任务

使用 APScheduler：

```python
# app/tasks/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def daily_kline_update():
    """每日 16:30 增量更新 K 线。"""
    pass

def daily_valuation_update():
    """每日 18:00 更新估值数据。"""
    pass

scheduler.add_job(daily_kline_update, 'cron', hour=16, minute=30, day_of_week='mon-fri')
scheduler.add_job(daily_valuation_update, 'cron', hour=18, minute=0, day_of_week='mon-fri')
```
