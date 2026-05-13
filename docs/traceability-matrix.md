# 可追溯矩阵 (Traceability Matrix)

> 维护需求 → 设计 → 代码 → 测试的完整映射关系。

---

## 矩阵说明

### 状态说明

| 状态 | 含义 |
|------|------|
| ✅ | 已完成 |
| 🔄 | 进行中 |
| ⏳ | 待处理 |
| ❌ | 阻塞 |
| ⬜ | 未开始 |

---

## MVP 模块矩阵

### Module 0: 用户系统

| 需求 ID | 需求文档 | 设计文档 | 后端代码 | 前端代码 | 测试用例 | 状态 |
|---------|----------|----------|----------|----------|----------|------|
| F-001 | [微信授权登录](features/feature-001-wechat-auth.md) | [module-0-user](designs/module-0-user/README.md) | `backend/app/routes/auth.py` | `frontend/src/views/Login.vue` | — | 🔄 编码中 |
| F-002 | [用户管理](features/feature-002-user-management.md) | [module-0-user](designs/module-0-user/README.md) | `backend/app/routes/user.py` | `frontend/src/views/Profile.vue` | — | 🔄 编码中 |

### Module 1: 数据底座

| 需求 ID | 需求文档 | 设计文档 | 后端代码 | 前端代码 | 测试用例 | 状态 |
|---------|----------|----------|----------|----------|----------|------|
| F-003 | [数据底座](features/feature-003-data-service.md) | [module-1-data](designs/module-1-data/README.md) | `backend/app/services/data_service.py` | — | — | 🔄 编码中 |

### Module 2: 新闻聚合

| 需求 ID | 需求文档 | 设计文档 | 后端代码 | 前端代码 | 测试用例 | 状态 |
|---------|----------|----------|----------|----------|----------|------|
| F-004 | [新闻聚合](features/feature-004-news-aggregation.md) | [module-2-news](designs/module-2-news/README.md) | `backend/app/services/news_service.py` | `frontend/src/components/NewsList.vue` | — | 🔄 编码中 |

### Module 3: 市场概览

| 需求 ID | 需求文档 | 设计文档 | 后端代码 | 前端代码 | 测试用例 | 状态 |
|---------|----------|----------|----------|----------|----------|------|
| F-005 | [市场概览](features/feature-005-market-overview.md) | [module-3-market](designs/module-3-market/README.md) | `backend/app/routes/market.py` | `frontend/src/views/Dashboard.vue` | — | 🔄 编码中 |

### Module 4: 估值分析

| 需求 ID | 需求文档 | 设计文档 | 后端代码 | 前端代码 | 测试用例 | 状态 |
|---------|----------|----------|----------|----------|----------|------|
| F-006 | [估值分析](features/feature-006-valuation-analysis.md) | [module-4-valuation](designs/module-4-valuation/README.md) | `backend/app/services/valuation_service.py` | `frontend/src/components/ValuationChart.vue` | `tests/unit/test_percentile.py` | 🔄 编码中 |

---

## 统计汇总

| 模块 | 需求数 | 有需求文档 | 有设计文档 | 有后端代码 | 有前端代码 | 有测试 | 完成率 |
|------|--------|------------|------------|------------|------------|--------|--------|
| Module 0 | 2 | 100% | 100% | 100% | 100% | 0% | — |
| Module 1 | 1 | 100% | 100% | 100% | 0% | 0% | — |
| Module 2 | 1 | 100% | 100% | 100% | 100% | 0% | — |
| Module 3 | 1 | 100% | 100% | 100% | 100% | 0% | — |
| Module 4 | 1 | 100% | 100% | 100% | 100% | 50% | — |
| **总计** | **6** | **100%** | **100%** | **100%** | **80%** | **8%** | — |

---

## 关键缺口

1. **测试覆盖率 8%** — 需要补充 API 测试和前端测试
2. **Module 1 前端** — 纯后端模块，无需前端

---

## 维护规则

| 操作 | 负责角色 |
|------|----------|
| 新增需求 | 产品经理 |
| 更新设计 | 架构师 |
| 更新代码 | 编码者 |
| 更新测试 | 编码者/审查者 |

---

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0.0 | 2026-05-13 | 重构为 LLM 友好格式，更新需求覆盖率至 100% |
| v1.0.0 | 2026-05-13 | 初始版本 |
