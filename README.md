# Strategy Compass 策略罗盘

> Your personal investment compass — multi-strategy portfolio management for grid trading, DCA, asset allocation, and beyond.

## 项目定位

Strategy Compass 不只是一个交易工具，而是一个**个人投资决策辅助平台**。它把多种投资策略、市场信号、资产分布整合在一个"罗盘"上，帮助个人投资者看清全局、做出更理性的决策。

## 设计哲学

### "代码是写给人看的，顺便让机器能执行。"

本项目采用 **Vibe Coding 原生设计**——由 AI Agent（Claude）主导开发，人类负责方向把控和最终决策。这种协作模式要求项目的信息架构与代码架构同等重要。

**三条并行轨道，同级对等：**

| 轨道 | 目录 | 格式 | 用途 |
|------|------|------|------|
| 代码轨道 | `backend/` `frontend/` | .py / .ts | 可执行的代码 |
| 知识轨道 | `docs/` `designs/` | .md / .png | 结构化的设计文档 |
| Agent 轨道 | `agent/` + 根目录 .md | .md | 驱动 AI 开发的上下文 |

改代码要同时改文档，改了文档 Agent 才能用。三者同等重要。

### LLM 友好性设计

本项目从第一天起就为 AI Agent 开发而设计，核心原则：

**1. 所有验证结果输出为文件，而非终端**

Agent 无法可靠地解析终端输出，但可以可靠地读取文件。因此：
- API 测试结果 → `build/test-results/api-check.json`
- 接口响应 → `build/test-results/api-responses/`
- 页面截图 → `build/test-results/screenshots/`
- 运行日志 → `build/local/logs/`

**2. 一个命令，全自动验证**

```bash
./scripts/api-check.sh        # 遍历所有 API，输出 JSON 汇总
./scripts/screenshot.py        # 截图所有页面
./scripts/setup-test-env.sh    # 初始化本地测试环境
```

Agent 执行完读取输出文件即可判断 pass/fail，无需解析复杂的测试框架报错。

**3. Markdown 是一等公民**

所有 Agent 上下文文件（memory-bank、specs、skills、sop）均使用 Markdown 格式，支持 RAG 检索和语义理解。

**4. 结构化记忆，而非无限对话**

通过 `agent/memory-bank/` 的 6 个文件形成信息漏斗，Agent 从上往下按需读取，节省 token。

## 目录结构

```
strategy_compass/
│
│   # ── 根目录：永远需要的文件（Agent 每次会话必读）──
├── SOUL.md                        # 项目灵魂：核心定位、开发理念、协作契约
├── AGENTS.md                      # Agent 操作手册：会话启动流程、行为规范
├── README.md                      # 本文件：项目对外介绍
├── .gitignore                     # Git 忽略规则
│
│   # ── 代码轨道 ──
├── backend/                       # Python 后端（Flask / FastAPI）
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py              # 配置（环境变量驱动）
│   │   ├── models/                # 数据模型（SQLite ORM / 原生 SQL）
│   │   ├── services/              # 业务逻辑层
│   │   │   ├── grid.py            #   网格交易引擎
│   │   │   ├── dca.py             #   定投策略
│   │   │   ├── allocation.py      #   资产配置
│   │   │   ├── dividend.py        #   红利现金流
│   │   │   ├── market.py          #   行情数据服务
│   │   │   └── news.py            #   财经资讯服务
│   │   ├── api/                   # API 路由
│   │   └── utils/                 # 工具函数
│   ├── data/                      # SQLite 数据库文件（gitignore）
│   ├── requirements.txt
│   ├── run.py
│   └── Dockerfile
│
├── frontend/                      # Web 前端
│   ├── src/
│   │   ├── views/                 # 页面组件
│   │   ├── components/            # 通用组件
│   │   └── api/                   # API 调用层
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── deploy/                        # 部署配置
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── ssl/                       # Let's Encrypt 证书
│
├── scripts/                       # 开发 + 测试脚本（LLM 友好）
│   ├── local-dev.sh               #   一键启动本地开发环境
│   ├── setup-test-env.sh          #   初始化测试环境（建库 + 种子数据）
│   ├── seed-data.py               #   种子数据生成器
│   ├── mock-market.py             #   行情数据模拟器
│   ├── api-check.sh               #   API 端点遍历检查（核心验证工具）
│   ├── screenshot.py              #   页面截图工具
│   ├── backup-db.sh               #   数据库备份
│   └── deploy.sh                  #   部署脚本
│
├── tests/                         # 测试代码
│   ├── test_api.py                #   API 单元测试
│   ├── test_services.py           #   服务层测试
│   └── conftest.py                #   pytest 配置 + fixtures
│
│   # ── 知识轨道 ──
├── docs/                          # 设计文档
│   ├── architecture.md            #   整体架构设计
│   ├── api.md                     #   API 接口文档
│   ├── data-sources.md            #   数据源说明
│   ├── features/                  #   各策略/功能设计文档
│   │   ├── grid-trading.md
│   │   ├── dca.md
│   │   ├── asset-allocation.md
│   │   ├── dividend.md
│   │   └── market.md
│   └── decisions/                 #   ADR 架构决策记录
│       └── YYYY-MM-DD-xxx.md
│
├── designs/                       # 交互设计
│   ├── wireframes/                #   线框图
│   ├── mockups/                   #   UI 设计稿
│   ├── interactions/              #   交互流程图
│   └── design-system.md           #   设计规范（色彩、字体、组件风格）
│
│   # ── Agent 轨道 ──
├── agent/
│   ├── memory-bank/               # 项目工作记忆（借鉴 Cline Memory Bank）
│   │   ├── projectbrief.md        #   项目概要
│   │   ├── product-context.md     #   产品上下文
│   │   ├── active-context.md      #   当前焦点
│   │   ├── system-patterns.md     #   技术模式
│   │   ├── tech-context.md        #   技术环境
│   │   └── progress.md            #   进度追踪
│   │
│   ├── specs/                     # 开发规范
│   │   ├── coding-style.md        #   代码风格约定
│   │   ├── git-flow.md            #   Git 分支与提交规范
│   │   └── api-design.md          #   API 设计规范
│   │
│   ├── skills/                    # 经验与技能库
│   │   ├── sqlite-patterns.md     #   SQLite 使用经验
│   │   ├── flask-patterns.md      #   Flask 最佳实践
│   │   └── deployment.md          #   部署经验
│   │
│   ├── sop/                       # 开发流程 SOP
│   │   ├── new-feature.md         #   新功能开发流程
│   │   ├── bug-fix.md             #   Bug 修复流程
│   │   └── refactor.md            #   重构流程
│   │
│   └── memory/                    # 开发日志
│       ├── MEMORY.md              #   重要决策与经验汇总
│       └── YYYY-MM-DD.md          #   每日开发记录
│
│   # ── 构建 + 测试产物（.gitignore）──
└── build/                         # 构建产物 + 本地测试环境
    ├── local/
    │   ├── data/                  #   本地 SQLite 数据库
    │   ├── uploads/               #   本地上传文件
    │   └── logs/                  #   运行日志（按日期轮转）
    ├── test-results/
    │   ├── api-check.json         #   API 检查汇总
    │   ├── api-responses/         #   各接口实际返回
    │   └── screenshots/           #   页面截图
    ├── dist/                      #   前端构建产物
    └── .gitkeep
```

## 策略矩阵

| 策略 | 状态 | 说明 |
|------|------|------|
| 网格交易 | 📋 待迁移 | 从 codes-trading-py 迁移，支持 S/M/L 多级网格 |
| 基金定投 | 📋 规划中 | 智能定投，根据估值动态调整投入金额 |
| 资产配置 | 📋 规划中 | 股债平衡、目标日期基金等配置策略 |
| 红利现金流 | 📋 规划中 | 红利再投资、现金流管理 |
| 市场数据 | 📋 规划中 | A 股指数、板块行情、涨跌分布 |
| 财经资讯 | 📋 规划中 | 多源新闻聚合、AI 摘要 |

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Python 3.12 + Flask | API 服务 + 策略引擎 |
| 数据库 | SQLite（初期）→ PostgreSQL（扩展） | 本地轻量，后期按需迁移 |
| 前端 | TypeScript + Vue 3 + Vite | 响应式 Web 界面 |
| 部署 | Docker Compose + Nginx | 容器化部署，Nginx 反向代理 |
| SSL | Let's Encrypt (certbot) | 免费 HTTPS 证书 |
| 服务器 | 腾讯云轻量应用服务器 | 4 核 8G / 10Mbps / 广州 |

## Quick Start

```bash
# 克隆仓库
git clone https://github.com/gzchenjiesong/strategy_compass.git
cd strategy_compass

# 初始化本地测试环境
./scripts/setup-test-env.sh

# 启动本地开发环境
./scripts/local-dev.sh

# 验证 API 是否正常
./scripts/api-check.sh
```

## 域名

- 生产环境：https://i-strategy-compass.com
- 备用：https://www.i-strategy-compass.com

## License

MIT
