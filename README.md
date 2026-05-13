# Strategy Compass 策略罗盘

> Your personal investment compass — 为个人投资者打造的多策略投资管理平台。
> 
> 🌐 https://i-strategy-compass.com

## 项目定位

Strategy Compass（策略罗盘）是一个面向个人投资者的投资决策辅助平台。它将市场数据、估值分析、策略管理整合在一个"罗盘"上，帮助投资者看清全局、做出更理性的决策。

**不是给量化基金用的，不是给高频交易用的。** 是给有工作、有存款、想让钱生钱，但没时间盯盘、没精力学金融工程的人用的。

### Compass（罗盘）的隐喻

- **方向** — 在市场噪音中找到自己的方向
- **稳定** — 不管市场怎么晃，指针始终指向北方
- **简单** — 一个盘面，一眼看懂

---

## 开发哲学

> **人类只管想象，LLM 负责实现。**
>
> 文档和提示词是真正的源代码，LLM 是编译器，生成的代码只是中间产物。人的价值在定义意图，不在堆砌实现。

本项目采用 **Vibe Coding 原生设计**——由 AI Agent 主导开发，人类负责方向把控和最终决策。这种协作模式要求项目的信息架构与代码架构同等重要。

**三条并行轨道，同级对等：**

| 轨道 | 目录 | 格式 | 用途 |
|------|------|------|------|
| 代码轨道 | `backend/` `frontend/` | .py / .ts | 可执行的代码 |
| 知识轨道 | `docs/` | .md | 结构化的设计文档与需求 |
| Agent 轨道 | `agent/` | .md | 驱动 AI 开发的上下文与流程 |

改代码要同时改文档，改了文档 Agent 才能用。三者同等重要。

---

## 目录结构

```
strategy_compass/
│
│   # ── 根目录：项目入口 ──
├── SOUL.md                    # 项目灵魂：核心定位、开发理念
├── AGENTS.md                  # Agent 操作手册：会话启动流程
├── README.md                  # 本文件：项目对外介绍
│
│   # ── 代码轨道 ──
├── backend/                   # Python 后端（Flask）
│   ├── app/                   #   API 路由、业务逻辑、数据模型
│   ├── tests/                 #   测试代码
│   ├── scripts/               #   后端专用脚本
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                  # Web 前端（Vue 3 + Vite + TS）
│   ├── src/                   #   页面组件、API 调用、状态管理
│   ├── package.json
│   └── Dockerfile
│
├── deploy/                    # 部署配置
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── scripts/                   # 项目级脚本
│   ├── api-check.sh           #   API 端点遍历检查
│   ├── local-deploy.sh        #   本地一键部署
│   └── run-tests.sh           #   运行测试套件
│
│   # ── 知识轨道 ──
├── docs/                      # 设计文档与需求
│   ├── features/              #   需求文档（feature-001 ~ feature-006）
│   ├── designs/               #   技术设计 + UI 设计
│   │   ├── module-0-user/     #     用户系统设计
│   │   ├── module-1-data/     #     数据底座设计
│   │   ├── module-2-news/     #     新闻聚合设计
│   │   ├── module-3-market/   #     市场概览设计
│   │   ├── module-4-valuation/#     估值分析设计
│   │   ├── design-system.md   #     UI 设计规范
│   │   ├── wireframes/        #     线框图
│   │   ├── mockups/           #     视觉稿
│   │   └── interactions/      #     交互原型
│   ├── acceptance/            #   验收报告
│   └── archive/               #   归档文件
│
│   # ── Agent 轨道 ──
├── agent/
│   ├── memory-bank/           # 项目级长期记忆
│   │   ├── projectbrief.md    #   项目概要
│   │   ├── active-context.md  #   当前开发焦点
│   │   ├── progress.md        #   进度追踪
│   │   ├── system-patterns.md #   架构模式
│   │   ├── tech-context.md    #   技术环境
│   │   └── product-context.md #   产品上下文
│   │
│   ├── sub-agents/            # 子代理角色定义
│   │   ├── startup-templates.md   # 4 角色启动模板
│   │   ├── product-manager.md
│   │   ├── architect.md
│   │   ├── coder.md
│   │   └── reviewer.md
│   │
│   ├── specs/                 # 开发规范
│   │   ├── api-design.md
│   │   ├── coding-style.md
│   │   ├── code-style-guide.md
│   │   ├── security-coding-standard.md
│   │   ├── backend-architecture.md
│   │   ├── frontend-architecture.md
│   │   ├── database.md
│   │   ├── testing.md
│   │   └── git-flow.md
│   │
│   ├── sop/                   # 开发流程 SOP
│   │   ├── new-feature.md
│   │   ├── bug-fix.md
│   │   ├── code-review-standard.md
│   │   ├── security-review.md
│   │   ├── deployment.md
│   │   └── ...
│   │
│   ├── skills/                # 经验与技能库
│   └── memory/                # 会话级工作日志
│
│   # ── 构建产物（.gitignore）──
└── build/
    ├── dist/                  # 前端构建产物
    └── test-results/          # 测试结果
```

---

## 模块状态

| 模块 | 名称 | 层级 | 状态 | 说明 |
|------|------|------|------|------|
| Module 0 | 用户系统 | 横跨 | ✅ 完成 | 微信OAuth + 邀请码 + 自选股 + 偏好设置 |
| Module 1 | 数据底座 | 数据层 | ✅ 完成 | 14张表 + 10核心指数 + K线/行情/估值API |
| Module 2 | 新闻聚合 | 数据层 | ✅ 完成 | 金十数据对接 + 5min同步 + 72h TTL |
| Module 3 | 市场概览 | 应用层 | ✅ 完成 | Dashboard 三标签页 + 指数卡片 + 详情弹窗 |
| Module 4 | 估值分析 | 分析层 | ✅ 完成 | PE/PB百分位 + 风险指标 + 估值区间标签 |
| Module 5 | 网格交易 | 应用层 | 📋 待开始 | 从 codes-trading-py 迁移 |
| Module 6 | 策略管理 | 应用层 | 📋 待开始 | 策略配置、监控、告警 |
| Module 7 | 通知服务 | 后置 | 📋 待开始 | 推送、邮件、Webhook |

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Python 3.12 + Flask + SQLAlchemy | API 服务 + ORM |
| 数据库 | SQLite (WAL模式) | 初期轻量，后期按需迁 PostgreSQL |
| 前端 | Vue 3 + Vite + TypeScript + Tailwind CSS + ECharts | 响应式 Web 界面 |
| 部署 | Docker Compose + Nginx | 容器化部署，反向代理 |
| SSL | Let's Encrypt | 免费 HTTPS 证书 |
| 服务器 | 腾讯云轻量应用服务器 | 4核8G / 广州 |

---

## Quick Start

```bash
# 克隆仓库
git clone https://github.com/gzchenjiesong/strategy_compass.git
cd strategy_compass

# 启动本地开发环境（后端 + 前端热重载）
./scripts/local-deploy.sh

# 验证 API 是否正常
./scripts/api-check.sh

# 运行测试
./scripts/run-tests.sh
```

---

## 域名

- 生产环境：https://i-strategy-compass.com
- 备用：https://www.i-strategy-compass.com

## License

MIT
