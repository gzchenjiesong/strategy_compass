---
title: "Module 4: 估值分析 — 接口与业务逻辑设计"
type: spec
module: module-4
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

## 4. 核心计算逻辑

### 4.1 百分位计算

百分位是 Module 4 最核心的计算。计算公式：

```python
def calc_percentile(current_value: float, history: list[float]) -> float:
    """
    计算 current_value 在 history 序列中的百分位。
    
    返回 0-100 的数值：
    - 0 表示当前值是历史最低
    - 100 表示当前值是历史最高
    - 50 表示处于历史中位数
    """
    if not history:
        return 50.0  # 无历史数据时返回中性值
    
    below_count = sum(1 for v in history if v < current_value)
    equal_count = sum(1 for v in history if v == current_value)
    
    percentile = (below_count + 0.5 * equal_count) / len(history) * 100
    return round(percentile, 1)
```

**百分位计算规则：**
- 历史序列排除空值（NULL）和异常值（PE < 0 或 PE > 1000 时跳过）
- 时间窗口默认 10 年，支持 3/5/10/20 年
- 历史数据不足 1 年时，不计算百分位，返回 `null` 并附带 `insufficient_data` 标记

### 4.2 估值区间标签

```python
def get_zone(percentile: float) -> str:
    """根据百分位返回估值区间标签。"""
    if percentile is None:
        return "unknown"
    if percentile <= 30:
        return "undervalued"    # 低估
    elif percentile <= 70:
        return "neutral"        # 适中
    else:
        return "overvalued"     # 高估
```

**区间阈值：** 30% / 70%，可通过配置文件调整（`ZONE_LOW=30, ZONE_HIGH=70`）。

### 4.3 风险指标计算

所有风险指标基于日 K 线数据计算：

```python
import math
from typing import Optional

ANNUAL_TRADING_DAYS = 252
RISK_FREE_RATE = 0.02  # 无风险利率 2%，可配置

def calc_annualized_volatility(daily_returns: list[float]) -> float:
    """年化波动率 = 日收益率标准差 × √252"""
    if len(daily_returns) < 30:
        return None
    
    mean = sum(daily_returns) / len(daily_returns)
    variance = sum((r - mean) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
    daily_std = math.sqrt(variance)
    return round(daily_std * math.sqrt(ANNUAL_TRADING_DAYS) * 100, 2)


def calc_max_drawdown(prices: list[float]) -> tuple[float, int, int]:
    """
    最大回撤。
    返回：(最大回撤百分比, 峰值索引, 谷值索引)
    """
    if len(prices) < 2:
        return (None, 0, 0)
    
    max_dd = 0
    peak_idx = 0
    peak = prices[0]
    
    for i, p in enumerate(prices):
        if p > peak:
            peak = p
            peak_idx = i
        dd = (peak - p) / peak
        if dd > max_dd:
            max_dd = dd
    
    return (round(max_dd * 100, 2), peak_idx, 0)


def calc_current_drawdown(prices: list[float]) -> float:
    """当前回撤 = (历史最高 - 当前价) / 历史最高"""
    if len(prices) < 2:
        return None
    
    historical_high = max(prices)
    current = prices[-1]
    dd = (historical_high - current) / historical_high
    return round(dd * 100, 2)


def calc_sharpe_ratio(annualized_return: float, annualized_volatility: float) -> float:
    """夏普比率 = (年化收益 - 无风险利率) / 年化波动率"""
    if annualized_volatility is None or annualized_volatility == 0:
        return None
    return round((annualized_return - RISK_FREE_RATE) / (annualized_volatility / 100), 2)


def calc_calmar_ratio(annualized_return: float, max_drawdown: float) -> float:
    """卡玛比率 = 年化收益 / 最大回撤"""
    if max_drawdown is None or max_drawdown == 0:
        return None
    return round(annualized_return / (max_drawdown / 100), 2)


def calc_beta(daily_returns: list[float], benchmark_returns: list[float]) -> float:
    """Beta = Cov(Ri, Rm) / Var(Rm)"""
    if len(daily_returns) != len(benchmark_returns) or len(daily_returns) < 60:
        return None
    
    mean_r = sum(daily_returns) / len(daily_returns)
    mean_b = sum(benchmark_returns) / len(benchmark_returns)
    
    cov = sum((r - mean_r) * (b - mean_b) for r, b in zip(daily_returns, benchmark_returns)) / (len(daily_returns) - 1)
    var_b = sum((b - mean_b) ** 2 for b in benchmark_returns) / (len(benchmark_returns) - 1)
    
    if var_b == 0:
        return None
    return round(cov / var_b, 2)


def calc_volume_ratio(volumes: list[int], window: int = 20) -> float:
    """成交量变化率 = 当日成交量 / 近 N 日均量"""
    if len(volumes) < window + 1:
        return None
    
    current = volumes[-1]
    avg = sum(volumes[-window - 1:-1]) / window
    
    if avg == 0:
        return None
    return round(current / avg, 2)
```

### 4.4 杠杆率计算

```python
def calc_leverage_ratio(financing_balance: float, total_market_cap: float) -> float:
    """杠杆率 = 融资余额 / A 股总市值 × 100%"""
    if total_market_cap == 0:
        return None
    return round(financing_balance / total_market_cap * 100, 4)
```

### 4.5 计算性能优化

百分位计算需要扫描历史序列，是 Module 4 最大的性能瓶颈。优化策略：

| 策略 | 实现方式 | 说明 |
|------|---------|------|
| **内存预计算** | 系统启动时预加载所有已入库标的的估值序列到内存 | 10 个核心指数 + 用户自选标的 |
| **增量更新** | 每日 18:00 估值数据更新后，仅追加当日数据点到内存序列 | 避免全量重算 |
| **缓存结果** | 百分位计算结果缓存 1 小时 | 同一标的短时间内不会变化 |
| **按需计算** | 用户自选标的首次访问时计算，结果持久化 | 避免启动时计算全部标的 |
| **批量接口** | 批量接口使用 IN 查询一次性取出所有估值历史 | 减少数据库查询次数 |

> **预估性能：** 单个指数百分位计算（2500 条历史数据排序）< 5ms，10 个核心指数批量 < 50ms。

