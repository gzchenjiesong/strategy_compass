# Strategy Compass — 编码阶段启动提示词

## 项目背景

**Strategy Compass** 是一个面向 A 股投资者的策略分析平台，核心功能包括：市场概览（指数估值与行情）、估值分析（历史百分位与多维度评分）、板块跟踪、个股分析、新闻快讯。当前处于 **MVP 编码阶段**。

## 当前状态

- ✅ 模块设计完成（Module 0~4 设计文档已冻结）
- ✅ 编码 SOP 与 Spec 已完善
- ⏳ 尚未开始任何编码工作（数据库、API、前端均从零开始）
- ⏳ Docker / Nginx 配置尚未创建

## 技术栈

- **后端**：Python 3.12 + Flask + SQLite(WAL) + Gunicorn + APScheduler
- **前端**：Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS + ECharts
- **部署**：Docker Compose + Nginx（腾讯云轻量 4C8G）
- **数据源**：AKShare（主）+ 腾讯财经 API（实时行情辅助）+ 金十数据（新闻）

## 编码顺序（三阶段）

### Phase 1（并行）
- **Module 0 用户系统**：注册 / 登录 / JWT / 密码哈希
- **Module 1 数据服务**：数据库初始化（14 张表）+ 10 核心指数数据拉取 + 定时任务 + 基础 API

### Phase 2（并行）
- **Module 4 估值分析**：A 股指数完整估值卡片 + 港股/美股简化卡片（仅价格百分位+回撤）
- **Module 2 行情中心**：K 线图表 + 实时行情展示

### Phase 3
- **Module 3 市场概览**：Dashboard 首页组装（整合 Module 1/2/4 的数据）

## 核心设计文件索引

读取以下文件以理解设计细节：

| 文件路径 | 内容 |
|---------|------|
| `docs/modules/module-0-user-system.md` | 用户系统模块设计（已冻结） |
| `docs/modules/module-1-data-service.md` | 数据服务模块设计（14 张表、10 核心指数） |
| `docs/modules/module-4-valuation-analysis.md` | 估值分析模块设计（四维度指标体系） |
| `docs/modules/module-2-market-data.md` | 行情中心模块设计 |
| `docs/modules/module-3-market-overview.md` | 市场概览模块设计（Dashboard） |

## 编码规范（必读）

| 文件路径 | 内容 |
|---------|------|
| `agent/specs/backend-architecture.md` | 后端分层规范（Model/Service/Route） |
| `agent/specs/frontend-architecture.md` | 前端项目结构与组件规范 |
| `agent/specs/api-design.md` | URL 设计、请求/响应规范、错误码 |
| `agent/specs/database.md` | 命名约定、索引策略、去重规则 |
| `agent/specs/testing.md` | 测试策略与 pytest fixtures |
| `agent/sop/new-feature.md` | 新功能开发 SOP（开发前→开发中→开发后） |
| `agent/sop/bug-fix.md` | Bug 修复 SOP（含"扫雷"步骤） |
| `agent/sop/deployment.md` | Docker/Nginx 部署与运维 SOP |

## MVP 关键约束

1. **A 股优先**：港股/美股指数仅展示价格百分位 + 回撤，不展示 PE/PB（AKShare 无免费历史接口）
2. **10 核心指数**：
   - A 股 6 个：000001(上证)/000300(沪深300)/000905(中证500)/399006(创业板)/000688(科创50)/930050(A500)
   - 港股 2 个：HSI(恒生)/HSTECH(恒生科技)
   - 美股 2 个：SPX(标普500)/IXIC(纳斯达克)
3. **K 线存储**：只存日 K，周/月 K 按需聚合
4. **估值去重**：INSERT OR REPLACE（当日可能修正）；K 线去重：INSERT OR IGNORE
5. **新闻 TTL**：72 小时自动清理，金十数据单一来源

## 推荐第一步

请从 **Phase 1 的 Module 1 数据服务** 开始：

1. 创建数据库模型（SQLAlchemy）—— 参照 `module-1-data-service.md` 第 3 节
2. 创建数据库迁移脚本（Flask-Migrate 或纯 SQL）
3. 实现指数基础数据导入（10 核心指数）
4. 实现历史 K 线拉取任务（AKShare）
5. 实现基础 API（指数列表、K 线查询）

完成后按 `new-feature.md` SOP 沉淀技能。

---

**开发原则**：严格遵循 SOP，编码前确认模块归属，编码中按分层顺序实现（Model → Service → Route），编码后更新文档并扫描同类场景。
