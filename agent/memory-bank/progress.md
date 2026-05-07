# 进度追踪 (Progress)

## 整体状态：架构设计阶段

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

### 🔧 进行中

- [ ] Layer 2 模块层：逐个模块接口与数据模型设计
- [x] **Layer 2: Module 0 用户系统设计**（已确认 & 冻结，2026-05-07）
- [x] **Layer 2: Module 1 数据底座设计**（初稿完成，待确认）
- [x] **Layer 2: Module 2 新闻聚合设计**（初稿完成，2026-05-07）
- [x] **Layer 2: Module 3 市场概览设计**（初稿完成，2026-05-07）
- [x] **Layer 2: Module 4 估值分析设计**（初稿完成，待确认）

### 📋 待开始

- [ ] Layer 2: Module 1 数据底座设计
- [ ] Layer 2: Module 2 新闻聚合设计
- [ ] Layer 2: Module 3 市场概览设计
- [x] Layer 2: Module 4 估值分析设计（初稿完成，待确认）
- [ ] Layer 2: Module 5 板块概念设计
- [ ] Layer 2: Module 6 个股基金详情设计
- [ ] Layer 3: 后端骨架搭建（Flask + SQLite）
- [ ] Layer 3: 前端骨架搭建（Vue 3 + Vite）
- [ ] Layer 3: 部署配置（Docker Compose + Nginx）

## 里程碑

| 里程碑 | 目标 | 状态 |
|--------|------|------|
| M0: 基础设施 | 域名 + 服务器 + 部署可用 | ✅ 完成 |
| M1: 架构设计 | 模块边界 + 接口契约 | 🟡 进行中（Layer 1 完成） |
| M2: 数据底座 | Module 0 + 1 实现 | ⬜ 待开始 |
| M3: 市场分析 | Module 2 + 3 + 4 实现 | ⬜ 待开始 |
| M4: 深度分析 | Module 5 + 6 实现 | ⬜ 待开始 |

## 关键决策记录

| 日期 | 决策 | 理由 |
|------|------|------|
| 2026-05-07 | 模块三层架构（数据层→分析层→应用层） | 估值是分析基础设施，不是应用层消费者 |
| 2026-05-07 | Module 0 定位为横跨数据层的用户隔离层 | 用户自选/偏好/配置都是用户数据 |
| 2026-05-07 | 新闻数据获取归入 Module 1 | 数据获取层统一入口 |
| 2026-05-06 | 采用"分轮次+文件桥接"的架构设计会话模式 | 避免上下文退化，保持决策可追溯 |
| 2026-05-06 | Tolaria + MiMo 作为 Markdown 知识库管理工具 | GUI 审阅 + AI 辅助 + 文件协同 |
| 2026-05-05 | 腾讯云轻量服务器（非 Serverless） | SQLite 持久化需求，定时任务需求 |
| 2026-05-03 | 技术栈 Flask + Vue 3 + SQLite | 团队熟悉度，项目阶段匹配 |

## 已知阻塞

- 无
