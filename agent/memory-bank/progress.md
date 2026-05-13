---

---
# 进度追踪 (Progress)

## 整体状态：MVP 编码阶段 — Phase 2/3 已完成

### ✅ 已完成

- [x] 项目命名与品牌（策略罗盘 / Strategy Compass / iCompass）
- [x] 域名注册（i-strategy-compass.com + .cn）
- [x] 服务器购买（腾讯云轻量 4C8G，广州）
- [x] DNS + SSH + Docker 环境验证
- [x] 项目目录结构设计（41 个目录）
- [x] GitHub 仓库创建（gzchenjiesong/strategy_compass）
- [x] 核心文档（SOUL.md, AGENTS.md, README.md）
- [x] Agent 记忆系统（memory-bank 6 件套 + agent/memory/）
- [x] Tolaria + MiMo 双向协作验证
- [x] 架构设计会话框架（session-framework.md）
- [x] **Layer 1 系统层：模块边界划分**（2026-05-07）
- [x] **Layer 2 模块层设计**：Module 0~4 设计文档全部完成
- [x] **Phase 1 编码完成**（2026-05-07）
  - [x] 后端骨架：Flask + SQLAlchemy + SQLite(WAL) + JWT 认证
  - [x] Module 0 用户系统：微信OAuth(mock) + 邀请码 + 自选股 + 板块关注 + 偏好设置
  - [x] Module 1 数据服务：14张表模型 + 10核心指数初始化 + K线/行情/估值API
  - [x] Module 4 估值分析：PE/PB百分位 + 风险指标(回撤/波动率) + 估值区间标签
  - [x] Module 2 新闻聚合：新闻列表API骨架
  - [x] Module 3 市场概览：Dashboard组装API
  - [x] 前端骨架：Vue 3 + Vite + TypeScript + Pinia + Tailwind CSS + ECharts
  - [x] 部署配置：Docker Compose + Nginx + 前后端 Dockerfile
  - [x] API 检查脚本：`scripts/api-check.sh`（7/7 通过）
- [x] **Phase 2/3 编码完成**（2026-05-08）
  - [x] Module 2 新闻聚合：金十数据API对接 + 定时同步（5min）+ 72h TTL清理
  - [x] Module 3 Dashboard 前端：概览/大盘/板块三标签页 + 指数卡片 + 详情弹窗
  - [x] 美股K线数据：SPX/IXIC 各5600+条历史日K（2004至今）
  - [x] 实时行情：A股/港股（腾讯API）+ 美股（AKShare fallback）

### ✅ 工程化优化（2026-05-13）

- [x] **P0问题修复**：
  - [x] 明确双记忆体系边界（memory-bank vs agent/memory）
  - [x] 同步session-framework.md状态
  - [x] 建立需求文档体系（模板 + 补录Module 0/1）
- [x] **P1问题解决**：
  - [x] 建立设计文档同步检查机制
  - [x] 补充核心测试框架和测试用例
  - [x] 定义工作日志管理策略（30天保留 + 自动归档）
- [x] **工具脚本**：
  - [x] 设计文档同步检查脚本
  - [x] 测试运行脚本
  - [x] 日志清理脚本

### 📋 待开始

- [ ] 策略模块（Module 5/6）：网格交易引擎迁移
- [ ] 数据补全：创业板指/中证A500估值数据（CSIndex接口仅20条）
- [ ] 补充更多测试用例（覆盖其他模块）
- [ ] 部署上线：Docker Compose 生产环境验证
- [ ] 建立CI/CD流程（自动化构建和部署）

## 里程碑

| 里程碑 | 目标 | 状态 |
|--------|------|------|
| M0: 基础设施 | 域名 + 服务器 + 部署可用 | ✅ 完成 |
| M1: 架构设计 | 模块边界 + 接口契约 | ✅ 完成 |
| M2: 数据底座 | Module 0 + 1 实现 | ✅ 完成 |
| M3: 市场分析 | Module 2 + 3 + 4 实现 | ✅ 完成 |
| M4: 深度分析 | Module 5 + 6 实现 | ⬜ 待开始 |

## 关键决策记录

| 日期 | 决策 | 理由 |
|------|------|------|
| 2026-05-08 | 美股指数实时行情使用 AKShare fallback | 腾讯API不支持美股指数，AKShare Sina接口有完整历史K线 |
| 2026-05-08 | 港股/美股用价格百分位替代PE/PB | MVP阶段无免费PE/PB数据源，价格百分位足够判断估值区间 |
| 2026-05-08 | 金十数据使用 `flash_newest.js` 无鉴权接口 | 官方API需付费，JS接口公开可用，50条满足MVP |
| 2026-05-07 | 模块三层架构（数据层→分析层→应用层） | 估值是分析基础设施，不是应用层消费者 |
| 2026-05-07 | Module 0 定位为横跨数据层的用户隔离层 | 用户自选/偏好/配置都是用户数据 |
| 2026-05-07 | 新闻数据获取归入 Module 1 | 数据获取层统一入口 |
| 2026-05-06 | 采用"分轮次+文件桥接"的架构设计会话模式 | 避免上下文退化，保持决策可追溯 |
| 2026-05-06 | Tolaria + MiMo 作为 Markdown 知识库管理工具 | GUI 审阅 + AI 辅助 + 文件协同 |
| 2026-05-05 | 腾讯云轻量服务器（非 Serverless） | SQLite 持久化需求，定时任务需求 |
| 2026-05-03 | 技术栈 Flask + Vue 3 + SQLite | 团队熟悉度，项目阶段匹配 |
| 2026-05-10 | 宏观数据 MVP 仅实现利率同步，CPI/失业率等由 Agent 扩展负责 | AKShare 宏观数据滞后 8-9 个月不可用；Agent 爬取方案可解决数据源问题但复杂度高，拆分为两阶段实现 |
| 2026-05-10 | event_schedule 增加 source 字段区分 cron/agent 数据源 | 统一 API 入口，后端不区分数据来源，便于未来 Agent 扩展平滑接入 |

## 已知阻塞

- 无
