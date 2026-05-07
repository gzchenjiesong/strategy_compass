# 测试规范

> Strategy Compass 测试策略：单元测试覆盖核心计算逻辑，集成测试覆盖 API 接口，手动测试覆盖用户流程。

## 1. 测试策略

| 测试类型 | 范围 | 工具 | 优先级 |
|---------|------|------|--------|
| 单元测试 | Service 层核心函数 | pytest | P0 |
| API 测试 | 接口响应格式/状态码 | pytest + Flask test client | P0 |
| 集成测试 | 模块间调用 | pytest | P1 |
| 前端测试 | 组件渲染 | Vitest | P1 |
| E2E 测试 | 用户流程 | Playwright | P2（MVP 后置） |

## 2. 单元测试

### 2.1 测试目录

```
tests/
├── __init__.py
├── conftest.py              # pytest 全局配置和 fixtures
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_valuation_calc.py   # 估值计算
│   ├── test_risk_metrics.py     # 风险指标
│   └── test_percentile.py       # 百分位计算
├── api/                     # API 测试
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_data.py
│   ├── test_news.py
│   ├── test_market.py
│   └── test_valuation.py
└── integration/             # 集成测试
    ├── __init__.py
    └── test_data_flow.py
```

### 2.2 百分位计算测试

```python
# tests/unit/test_percentile.py
import pytest
from app.services.valuation_service import calc_percentile

class TestCalcPercentile:
    def test_exact_match(self):
        """当前值等于历史值时的百分位。"""
        history = [10, 20, 30, 40, 50]
        assert calc_percentile(30, history) == 50.0

    def test_minimum(self):
        """当前值为历史最小值。"""
        history = [10, 20, 30, 40, 50]
        assert calc_percentile(5, history) == 0.0

    def test_maximum(self):
        """当前值为历史最大值。"""
        history = [10, 20, 30, 40, 50]
        assert calc_percentile(60, history) == 100.0

    def test_empty_history(self):
        """无历史数据时返回中性值。"""
        assert calc_percentile(50, []) == 50.0

    def test_negative_pe_skipped(self):
        """负 PE 不参与百分位计算。"""
        history = [-10, 10, 20, 30]
        # -10 应该被跳过
        assert calc_percentile(15, history) == 50.0

    def test_extreme_pe_skipped(self):
        """极端 PE (>1000) 不参与百分位计算。"""
        history = [10, 20, 30, 5000]
        # 5000 应该被跳过
        assert calc_percentile(20, history) == 50.0
```

### 2.3 风险指标测试

```python
# tests/unit/test_risk_metrics.py
import pytest
from app.services.valuation_service import (
    calc_max_drawdown,
    calc_current_drawdown,
    calc_annualized_volatility,
)

class TestRiskMetrics:
    def test_max_drawdown(self):
        """计算最大回撤。"""
        prices = [100, 120, 90, 110, 80, 100]
        max_dd, _, _ = calc_max_drawdown(prices)
        # 从 120 跌到 80，回撤 33.33%
        assert round(max_dd, 2) == 33.33

    def test_current_drawdown(self):
        """计算当前回撤。"""
        prices = [100, 120, 110, 115, 112]
        # 历史最高 120，当前 112
        assert calc_current_drawdown(prices) == round((120 - 112) / 120 * 100, 2)

    def test_annualized_volatility(self):
        """计算年化波动率。"""
        returns = [0.01, -0.02, 0.015, -0.01, 0.005] * 50  # 250 天
        vol = calc_annualized_volatility(returns)
        assert vol is not None
        assert vol > 0
```

## 3. API 测试

### 3.1 Flask Test Client

```python
# tests/api/test_valuation.py
import pytest

class TestValuationAPI:
    def test_get_index_valuation_success(self, client, auth_headers):
        """获取指数估值成功。"""
        response = client.get(
            '/api/v4/valuation/index/000300',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert data['data']['symbol'] == '000300'
        assert 'valuation' in data['data']
        assert 'risk' in data['data']

    def test_get_index_valuation_not_found(self, client, auth_headers):
        """指数代码不存在。"""
        response = client.get(
            '/api/v4/valuation/index/999999',
            headers=auth_headers
        )
        assert response.status_code == 404
        data = response.get_json()
        assert data['error']['code'] == 'SYMBOL_NOT_FOUND'

    def test_get_index_valuation_unauthorized(self, client):
        """未认证访问。"""
        response = client.get('/api/v4/valuation/index/000300')
        assert response.status_code == 401
```

### 3.2 Fixtures

```python
# tests/conftest.py
import pytest
from app import create_app

@pytest.fixture
def app():
    """创建测试应用。"""
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """创建测试客户端。"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """获取认证头。"""
    # 模拟登录获取 token
    response = client.post('/api/v1/auth/wechat/callback', json={
        'code': 'test_code',
    })
    token = response.get_json()['data']['token']
    return {'Authorization': f'Bearer {token}'}
```

## 4. 测试数据

### 4.1 Mock 数据

```python
# tests/fixtures/sample_klines.py
SAMPLE_KLINES = [
    {"date": "2026-01-02", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000000},
    {"date": "2026-01-03", "open": 101, "high": 103, "low": 100, "close": 102, "volume": 1200000},
    # ... 更多数据
]

SAMPLE_VALUATIONS = [
    {"date": "2026-01-02", "pe_ttm": 15.0, "pb": 1.5},
    {"date": "2026-01-03", "pe_ttm": 15.2, "pb": 1.52},
    # ... 更多数据
]
```

## 5. 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行 API 测试
pytest tests/api/

# 带覆盖率报告
pytest --cov=app --cov-report=html

# 前端测试
npm run test:unit
```

## 6. 测试 checklist

每个功能开发完成后检查：

- [ ] 核心计算函数有单元测试覆盖
- [ ] API 接口有响应格式测试
- [ ] 边界情况有测试（空数据、异常值）
- [ ] 错误码有对应的测试用例
- [ ] 测试通过后才合并代码
