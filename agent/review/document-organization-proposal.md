# 文档组织形式提案

> 目标：建立 LLM 友好、助力 vibe coding、上下文可控、易维护的文档体系。

---

## 一、当前问题诊断

### 1.1 文档定位模糊

当前 `docs/` 目录混合了多种类型的文档：
- `docs/features/` — 需求文档（但覆盖率 0%，且格式不统一）
- `docs/modules/` — 模块设计文档（内容量过大，单个文件可能超过 5000 字）
- `docs/acceptance-report-*.md` — 验收报告（散落在根目录）

**问题**：没有清晰的分层，LLM 加载时不知道哪些该加载、哪些不该加载。

### 1.2 单个文档过大

以 `docs/modules/module-4-valuation.md` 为例，可能包含：
- 模块概述
- 数据模型
- API 设计
- 业务流程
- 前端交互
- 测试策略

**问题**：LLM 的上下文窗口有限，加载一个超大文档会挤占其他重要信息的空间。

### 1.3 缺乏索引和摘要

当前没有统一的入口文档告诉 LLM：
- 有哪些文档？
- 每个文档是干什么的？
- 当前状态是什么？

**问题**：每次新会话都需要"摸索"文档结构，效率低。

### 1.4 更新维护困难

文档之间缺乏关联：
- 需求改了，不知道哪些设计文档需要同步更新
- 设计改了，不知道哪些代码需要调整
- 没有变更历史，无法追溯

---

## 二、设计原则

### 原则 1：分层清晰（Separation of Concerns）

按"需求 → 设计 → 实现 → 验收"分层，每层只关注自己的职责：

```
需求层 (features/)    — 做什么 (What)
设计层 (designs/)     — 怎么做 (How)
规范层 (specs/)       — 怎么做是对的 (Rules)
流程层 (sop/)         — 按什么顺序做 (Process)
验收层 (acceptance/)  — 做得对不对 (Validation)
```

### 原则 2：单一职责（Single Responsibility）

一个文件只讲一件事：
- ❌ 一个文件既讲数据模型又讲 API 又讲前端交互
- ✅ 数据模型 → `data-model.md`
- ✅ API 设计 → `api.md`
- ✅ 前端交互 → `ui.md`

### 原则 3：大小可控（Size Control）

目标：单个文件不超过 **2000 个中文字符**（约 1000 tokens）：

| 类型 | 建议大小 | 超限处理 |
|------|----------|----------|
| 需求文档 | < 1500 字 | 拆分为多个子需求 |
| 设计文档 | < 2000 字 | 按子模块拆分 |
| 规范文档 | < 2000 字 | 按主题拆分 |
| 流程文档 | < 1500 字 | 简化流程图 |

### 原则 4：自描述（Self-Describing）

每个文件都能独立被理解：
- Frontmatter 包含元数据（标题、版本、状态、作者）
- 开头有 1 段摘要（TL;DR）
- 结尾有关联文档链接

### 原则 5：渐进加载（Progressive Loading）

LLM 不需要一次加载所有内容，而是分层加载：

```
第 1 层：总览（README）— 100 tokens
第 2 层：摘要（Summary）— 300 tokens
第 3 层：详情（Detail）— 800 tokens
第 4 层：参考（Reference）— 按需加载
```

---

## 三、 proposed 目录结构

```
strategy_compass/
├── docs/                          # 项目文档（用户可见）
│   ├── README.md                 # 文档总览（所有 Agent 的第一站）
│   ├── features/                 # 需求层：做什么
│   │   ├── README.md            # 需求总览（索引 + 状态）
│   │   ├── feature-001-wechat-auth.md
│   │   ├── feature-002-market-overview.md
│   │   ├── feature-003-valuation-analysis.md
│   │   ├── feature-004-news-aggregation.md
│   │   └── archive/             # 已废弃需求
│   │
│   ├── designs/                  # 设计层：怎么做
│   │   ├── README.md            # 设计总览（模块关系图）
│   │   ├── module-0-user/       # 每个模块一个目录
│   │   │   ├── README.md       # 模块摘要（1 页纸）
│   │   │   ├── data-model.md   # 数据模型
│   │   │   ├── api.md          # API 设计
│   │   │   ├── flow.md         # 业务流程
│   │   │   └── ui.md           # 交互设计（可选）
│   │   ├── module-1-data/
│   │   ├── module-2-news/
│   │   ├── module-3-market/
│   │   ├── module-4-valuation/
│   │   └── decisions/          # 架构决策记录 (ADR)
│   │       ├── adr-001-sqlite-to-postgres.md
│   │       └── adr-002-cache-strategy.md
│   │
│   └── acceptance/              # 验收层
│       └── report-20260513.md
│
├── agent/                        # Agent 配置（内部使用）
│   ├── README.md                # Agent 体系总览
│   ├── memory-bank/             # 长期记忆
│   │   ├── README.md           # 记忆总览
│   │   ├── active-context.md   # 当前状态（保持现状）
│   │   ├── projectbrief.md     # 项目定位
│   │   ├── product-context.md  # 用户画像
│   │   ├── system-patterns.md  # 架构模式
│   │   ├── tech-context.md     # 技术栈
│   │   ├── progress.md         # 进度追踪
│   │   └── optimization-plan.md # 优化计划
│   │
│   ├── sub-agents/              # 角色定义
│   │   ├── README.md           # 角色总览
│   │   ├── product-manager.md
│   │   ├── architect.md
│   │   ├── coder.md
│   │   ├── reviewer.md
│   │   └── startup-templates.md # 启动模板
│   │
│   ├── specs/                   # 规范层
│   │   ├── README.md           # 规范总览
│   │   ├── coding-style.md
│   │   ├── api-design.md
│   │   ├── database.md
│   │   ├── testing.md
│   │   ├── active-context-schema.md
│   │   └── document-versioning.md
│   │
│   └── sop/                     # 流程层
│       ├── README.md           # 流程总览
│       ├── new-feature.md
│       ├── bug-fix.md
│       ├── deployment.md
│       ├── agent-handoff.md
│       └── session-archive.md
│
└── scripts/                     # 工具脚本
    ├── check-design-sync.sh    # 设计文档同步检查
    └── generate-summary.py     # 自动生成摘要
```

---

## 四、关键设计决策

### 4.1 需求文档 vs 设计文档：是否分开？

**结论：分开，但保持紧密关联。**

理由：
- 需求文档面向"价值"（用户需要什么）
- 设计文档面向"实现"（技术怎么实现）
- 不同角色关注不同：产品经理看需求，架构师看设计
- 但两者通过 ID 关联：`feature-003` → `module-4-valuation`

**关联方式：**
```markdown
<!-- 在需求文档中 -->
## 关联设计
- 技术设计：docs/designs/module-4-valuation/README.md
- 数据模型：docs/designs/module-4-valuation/data-model.md

<!-- 在设计文档中 -->
## 关联需求
- 需求文档：docs/features/feature-003-valuation-analysis.md
```

### 4.2 交互设计放在哪里？

**结论：作为设计文档的一部分，不独立成层。**

理由：
- 交互是"设计"的子集，不是独立维度
- 放在 `docs/designs/module-X/ui.md` 中
- 如果交互简单（如一个表单），直接写在 `README.md` 中
- 如果交互复杂（如多步骤流程），独立成 `ui.md`

### 4.3 文档大小控制

**硬性限制：单个文件不超过 2000 字。**

超限处理策略：

| 场景 | 处理方式 |
|------|----------|
| 需求文档超限 | 拆分为多个子需求文件 |
| 设计文档超限 | 按子模块拆分（api.md / data-model.md / flow.md） |
| 规范文档超限 | 按主题拆分（frontend-style.md / backend-style.md） |
| 流程文档超限 | 简化文字，用流程图代替 |

**检查工具：**
```bash
# 检查所有文档大小
find docs/ agent/ -name "*.md" -exec wc -c {} \; | awk '$1 > 6000 {print "超限: " $2 " (" $1 " bytes)"}'
```

### 4.4 上下文加载策略

**分层加载，按需展开：**

```
Level 1（必载，~200 tokens）：
  - docs/README.md
  - agent/memory-bank/active-context.md

Level 2（角色相关，~300 tokens）：
  产品经理：docs/features/README.md
  架构师：docs/designs/README.md
  编码者：agent/specs/README.md
  审查者：agent/sop/README.md

Level 3（任务相关，~500 tokens）：
  具体需求/设计/规范文件

Level 4（按需，~800 tokens）：
  详细参考文档、示例代码
```

**启动模板中的应用：**
```markdown
## 加载策略
1. 先加载 Level 1（总览）
2. 根据任务加载 Level 2（角色相关）
3. 根据具体任务加载 Level 3（任务相关）
4. 遇到疑问时按需加载 Level 4（参考）
```

---

## 五、文档模板

### 5.1 需求文档模板

```markdown
---
id: feature-001
title: 微信授权登录
created: 2026-05-13
version: 1.0.0
status: draft       # draft / review / approved / deprecated
priority: P0        # P0 / P1 / P2
owner: product-manager
---

# 微信授权登录

## 摘要
用户通过微信扫码授权登录系统，获取用户基本信息（昵称、头像、openid）。

## 用户故事
作为用户，我希望通过微信快速登录，以便不用注册新账号。

## 验收标准
- [ ] 用户点击"微信登录"按钮，跳转到微信授权页
- [ ] 授权成功后，系统自动创建用户账号
- [ ] 返回用户信息（昵称、头像、openid）
- [ ] 未授权时返回错误提示

## 边界条件
- 用户拒绝授权：返回登录页，显示"授权失败"
- 网络异常：显示"网络错误，请重试"
- 重复授权：更新用户信息，不创建重复账号

## 关联设计
- 技术设计：docs/designs/module-0-user/README.md
- API 设计：docs/designs/module-0-user/api.md

## 变更历史
| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-05-13 | 初始版本 |
```

### 5.2 设计文档模板（模块摘要）

```markdown
---
id: module-0
title: 用户系统
created: 2026-05-13
version: 1.0.0
status: draft       # draft / review / implemented / deprecated
owner: architect
---

# Module 0: 用户系统

## 摘要
提供用户认证、用户信息管理、权限控制等基础能力。

## 职责范围
- 微信 OAuth 授权登录
- 用户信息管理（昵称、头像、openid）
- JWT Token 签发与验证
- 用户权限控制

## 子文档
| 文档 | 说明 | 状态 |
|------|------|------|
| [数据模型](data-model.md) | User 表结构 | ✅ 已完成 |
| [API 设计](api.md) | 认证相关接口 | 🔄 设计中 |
| [业务流程](flow.md) | 登录/注册流程 | ⏳ 待设计 |

## 依赖模块
- 无（基础模块，被其他模块依赖）

## 关联需求
- [feature-001 微信授权登录](../features/feature-001-wechat-auth.md)

## 变更历史
| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-05-13 | 初始版本 |
```

### 5.3 设计文档模板（子文档）

```markdown
---
parent: module-0
title: 数据模型
created: 2026-05-13
version: 1.0.0
---

# Module 0: 数据模型

## 摘要
用户系统的数据模型设计，包含 User 表和关联表。

## 实体定义

### User
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | 自增主键 |
| openid | VARCHAR(64) | UNIQUE | 微信 openid |
| nickname | VARCHAR(128) | | 微信昵称 |
| avatar | VARCHAR(256) | | 头像 URL |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

## 关联文档
- [模块摘要](../README.md)
- [API 设计](api.md)

## 变更历史
| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-05-13 | 初始版本 |
```

---

## 六、迁移计划

### 6.1 从当前结构迁移

**当前 → 目标：**

| 当前文件 | 目标位置 | 操作 |
|----------|----------|------|
| `docs/modules/module-4-valuation.md` | `docs/designs/module-4-valuation/README.md` + 子文档 | 拆分 |
| `docs/features/coverage-report-*.md` | `docs/features/README.md` | 合并 |
| `docs/acceptance-report-*.md` | `docs/acceptance/` | 移动 |
| `agent/specs/*.md` | 保持不变 | — |
| `agent/sop/*.md` | 保持不变 | — |

### 6.2 迁移步骤

1. **创建新目录结构**（不删除旧文件）
2. **编写 README.md**（每个目录一个）
3. **拆分大文档**（按子模块拆分）
4. **补录缺失文档**（需求文档、子设计文档）
5. **验证链接**（检查所有交叉引用）
6. **废弃旧文件**（标记为 deprecated，30 天后删除）

### 6.3 优先级

| 优先级 | 任务 | 原因 |
|--------|------|------|
| P0 | 创建所有 README.md | 提供 LLM 入口 |
| P0 | 拆分 module-4-valuation.md | 当前最大文件 |
| P1 | 补录需求文档 | 可追溯矩阵需要 |
| P1 | 拆分其他模块设计文档 | 统一规范 |
| P2 | 迁移验收报告 | 整理归档 |

---

## 七、维护机制

### 7.1 文档更新触发规则

| 触发条件 | 更新内容 | 负责角色 |
|----------|----------|----------|
| 新功能立项 | 创建需求文档 + 更新索引 | 产品经理 |
| 需求评审通过 | 更新需求状态 → approved | 产品经理 |
| 设计完成 | 创建设计文档 + 更新索引 | 架构师 |
| 编码完成 | 更新设计状态 → implemented | 编码者 |
| 验收通过 | 创建验收报告 + 更新索引 | 审查者 |
| 需求变更 | 更新需求文档 + 检查关联设计 | 产品经理 |

### 7.2 自动化检查

```bash
# 检查文档大小
scripts/check-doc-size.sh

# 检查链接有效性
scripts/check-links.sh

# 生成文档索引
scripts/generate-index.py
```

### 7.3 定期回顾

每月进行一次文档健康检查：
- [ ] 是否有超大文件需要拆分？
- [ ] 是否有 broken link？
- [ ] 是否有 draft 状态超过 30 天的文档？
- [ ] 是否有 deprecated 文档超过 30 天未清理？
- [ ] README.md 是否与实际文件一致？

---

## 八、总结

### 核心改变

| 方面 | 当前 | 目标 |
|------|------|------|
| 文档分层 | 模糊（features/ modules/ 混合） | 清晰（features/ designs/ specs/ sop/） |
| 文件大小 | 无限制（可能 5000+ 字） | < 2000 字 |
| 入口文档 | 无 | 每个目录一个 README.md |
| 关联关系 | 无 | 通过 ID 和链接关联 |
| 加载策略 | 一次性加载所有 | 分层渐进加载 |
| 状态跟踪 | 无 | frontmatter 标记状态 |

### 预期收益

1. **LLM 上下文更可控** — 分层加载，每次只加载必要信息
2. **Agent 切换更顺畅** — 通过 README.md 快速了解当前状态
3. **文档维护更容易** — 单一职责，修改影响范围可控
4. **可追溯性更强** — 需求→设计→代码→测试的完整链路

---

*本提案基于 2026-05-13 的文档现状制定。*
