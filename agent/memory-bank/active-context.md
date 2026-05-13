# 当前焦点 (Active Context)

## 当前阶段

**MVP 编码阶段 — Phase 2/3 已完成，准备进入 M4（策略模块）**

### Phase 2/3 编码成果（2026-05-08）

- **Module 2 新闻聚合**：金十数据 `flash_newest.js` 接口对接（无鉴权，50条）+ HTML标签清洗 + 重要性映射 + 定时同步（5min）+ 72h TTL清理
- **Module 3 Dashboard 前端**：概览/大盘/板块三标签页
  - 概览页：估值区间分布统计 + 核心指数卡片网格 + 重要快讯
  - 大盘页：A股/港股/美股分组，详细指数卡片（价格/涨跌幅/估值/回撤）
  - 指数卡片点击 → 详情弹窗（K线图表 + 估值指标 + 风险指标）
- **数据补全**：美股 SPX/IXIC 历史K线各5600+条（2004至今，AKShare Sina接口）
- **实时行情**：A股/港股（腾讯API）+ 美股（AKShare fallback）

### API 验证状态

- GET /health ✅
- POST /api/v1/auth/wechat/callback ✅
- GET /api/v1/auth/me ✅
- GET /api/v1/users/me ✅
- GET /api/v1/data/indices ✅
- GET /api/v3/market/overview ✅
- GET /api/v3/market/indices ✅
- GET /api/v2/news ✅
- GET /api/v2/news/important ✅
- GET /api/v2/news/stats ✅

### 数据状态

| 标的 | K线 | 估值 | 实时行情 |
|------|-----|------|----------|
| 上证指数 | 4858条 | 20条 | ✅ |
| 沪深300 | 4858条 | 5119条 | ✅ |
| 中证500 | 4858条 | 4690条 | ✅ |
| 创业板指 | 3866条 | 0条 | ✅ |
| 科创50 | 1535条 | 20条 | ✅ |
| 中证A500 | 2754条 | 20条 | ✅ |
| 恒生指数 | 3126条 | 0条 | ✅ |
| 恒生科技 | 1403条 | 0条 | ✅ |
| 标普500 | 5625条 | — | ✅ |
| 纳斯达克 | 5622条 | — | ✅ |
| 新闻快讯 | — | — | 50条 |

## 下一步行动

### M4: 策略模块（待开始）
- **Module 5 网格交易**：从 codes-trading-py 迁移网格交易引擎
- **Module 6 策略管理**：策略CRUD + 持仓管理 + 交易记录

### 工程化优化（已完成）
- [x] 明确双记忆体系边界（memory-bank vs agent/memory）
- [x] 同步session-framework.md状态
- [x] 建立需求文档体系（模板 + 补录）
- [x] 建立设计文档同步检查机制
- [x] 补充核心测试框架和测试用例
- [x] 定义工作日志管理策略
- [x] **Phase 1 工程化基础**（2026-05-13）：
  - [x] 创建角色启动模板（agent/sub-agents/startup-templates.md）
  - [x] 定义 active-context.md Schema（agent/specs/active-context-schema.md）
  - [x] 建立可追溯矩阵（docs/traceability-matrix.md）
  - [x] 增加版本控制规范（agent/specs/document-versioning.md）

### 技术债务
- [ ] 创业板指/中证A500估值数据不足（CSIndex仅20条，需寻找历史数据源）
- [ ] 补充更多测试用例（覆盖其他模块）
- [ ] 部署上线：Docker Compose 生产环境验证
- [ ] 建立CI/CD流程（自动化构建和部署）

## 已知阻塞

- 无
