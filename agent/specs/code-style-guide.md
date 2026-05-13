---
title: 代码风格规范
created: 2026-05-13
version: 1.0.0
status: active
---

# 代码风格规范

> 所有代码必须遵守的风格标准。保持代码一致性和可维护性。

## 1. 命名规范

### 1.1 Python

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块/包 | 小写 + 下划线 | `data_service.py` |
| 类 | 大驼峰 | `UserService` |
| 函数/方法 | 小写 + 下划线 | `get_user_by_id()` |
| 常量 | 大写 + 下划线 | `MAX_RETRY_COUNT = 3` |
| 私有属性 | 前缀下划线 | `_internal_cache` |
| 变量 | 小写 + 下划线 | `user_list` |

### 1.2 TypeScript/Vue

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件 | 大驼峰 + 多词 | `UserProfileCard.vue` |
| 接口 | 前缀 I | `IUserProfile` |
| 类型 | 前缀 T | `TApiResponse` |
| 枚举 | 大驼峰 | `UserStatus` |
| 函数 | 小驼峰 | `fetchUserData()` |
| 常量 | 大驼峰 | `API_BASE_URL` |

## 2. 注释规范

### 2.1 必须注释的场景
- 复杂的业务逻辑（为什么这么做）
- 非直观的算法
- 临时方案（标注 TODO + 原因 + 预期解决时间）
- 接口的边界条件和副作用

### 2.2 禁止注释的场景
- 显而易见的代码（`i += 1  # 增加 i`）
- 与代码不一致的注释
- 大段被注释掉的代码（删除，用 Git 找回）

### 2.3 文档字符串
Python 函数必须写 docstring：
```python
def calculate_percentile(values: list[float], percentile: float) -> float:
    """计算历史百分位。

    Args:
        values: 历史数据列表，必须非空
        percentile: 目标百分位 (0-100)

    Returns:
        百分位对应的值

    Raises:
        ValueError: values 为空或 percentile 不在 0-100 范围
    """
```

## 3. 错误处理

### 3.1 原则
- 不要吞掉异常（至少记录日志）
- 异常信息要具体，但对外要脱敏
- 区分可恢复错误和不可恢复错误

### 3.2 正确示例
```python
# ❌ 错误：吞掉异常
try:
    result = fetch_data()
except:
    pass

# ✅ 正确：记录并转换
from fastapi import HTTPException

try:
    result = fetch_data()
except ExternalAPIError as e:
    logger.error(f"External API failed: {e}", exc_info=True)
    raise HTTPException(status_code=503, detail="数据服务暂时不可用")
```

## 4. 日志规范

### 4.1 日志级别
| 级别 | 使用场景 |
|------|----------|
| DEBUG | 开发调试，详细流程 |
| INFO | 关键流程节点、状态变更 |
| WARNING | 非预期但可恢复的情况 |
| ERROR | 功能异常，需要处理 |
| CRITICAL | 系统级故障，立即告警 |

### 4.2 日志格式
```python
import structlog

logger = structlog.get_logger()

# ✅ 结构化日志
logger.info(
    "user_login",
    user_id=user.id,
    ip_address=client_ip,
    user_agent=user_agent[:100]
)
```

## 5. 代码组织

### 5.1 文件长度
- 单文件不超过 500 行（特殊情况需注释说明）
- 单函数不超过 50 行
- 嵌套层级不超过 4 层

### 5.2 导入排序
```python
# 1. 标准库
import os
from datetime import datetime

# 2. 第三方库
import httpx
from fastapi import APIRouter

# 3. 项目内部
from app.services import user_service
from app.models import User
```

### 5.3 类型注解
- Python：所有函数参数和返回值必须加类型注解
- TypeScript：开启 strict 模式，禁止 `any`

## 6. 测试规范

### 6.1 测试文件命名
- Python：`test_*.py` 或 `*_test.py`
- 与被测文件同目录或 `tests/` 目录

### 6.2 测试覆盖要求
- 核心业务逻辑：≥ 80%
- 工具函数：≥ 60%
- 错误分支必须覆盖

### 6.3 测试结构
```python
def test_calculate_percentile_with_valid_data():
    """测试正常数据下的百分位计算。"""
    values = [10, 20, 30, 40, 50]
    result = calculate_percentile(values, 50)
    assert result == 30

def test_calculate_percentile_with_empty_data():
    """测试空数据应抛出异常。"""
    with pytest.raises(ValueError):
        calculate_percentile([], 50)
```

## 7. 数据库规范

### 7.1 SQLAlchemy 模型
- 必须定义 `__tablename__`
- 必须定义主键
- 时间戳字段：`created_at`, `updated_at`
- 外键必须加索引

### 7.2 查询规范
- 使用 ORM，禁止原生 SQL（复杂查询除外）
- 批量查询使用 `yield_per()` 或分页
- N+1 查询必须加 `selectinload()`

## 合规检查清单

编码完成后自查：

- [ ] 命名符合规范
- [ ] 复杂逻辑有注释
- [ ] 函数有 docstring
- [ ] 异常被正确处理
- [ ] 日志使用结构化格式
- [ ] 类型注解完整
- [ ] 测试覆盖核心逻辑

## 关联文档

- [代码审查 SOP](../sop/code-review-standard.md) — 审查流程
- [安全编码规范](security-coding-standard.md) — 安全相关要求

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-05-13 | 初始版本，从代码审查 SOP 提取规则部分 |
