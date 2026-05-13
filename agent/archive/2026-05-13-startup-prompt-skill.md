---
name: startup-prompt
description: |
  生成 sub-agent 新会话启动提示词。当需要为某个角色（产品设计/架构设计/编码开发/审查验收）
  生成新会话的第一句提示词时使用。Keywords: 启动提示词, startup prompt, 新会话,
  角色切换, sub-agent, 会话模板, product-manager, architect, coder, reviewer
---

# Sub-Agent 会话启动提示词生成器

## 概述

为 Strategy Compass 的四个角色（产品设计/架构设计/编码开发/审查验收）
生成即用的新会话启动提示词。产出的提示词可直接复制到新会话中使用。

## 触发关键词

- 启动提示词, startup prompt, 新会话, 角色切换, 第一句话
- 给我 coder/architect/product-manager/reviewer 的提示词
- 生成 XX 角色的会话模板
- 帮我准备 coder/architect/product-manager/reviewer 的新会话

## 生成流程

```
用户触发 → 1. 确认目标角色 → 2. 读取角色定义 → 3. 读取项目状态
         → 4. 了解具体任务 → 5. 生成提示词 → 输出
```

### Step 1: 确认目标角色

识别用户需要哪个角色的提示词。角色名与文件映射：

| 角色 | 文件 | 触发词 |
|------|------|--------|
| 产品设计 | `agent/sub-agents/product-manager.md` | product-manager, 产品, PM, 需求 |
| 架构设计 | `agent/sub-agents/architect.md` | architect, 架构, 设计 |
| 编码开发 | `agent/sub-agents/coder.md` | coder, 编码, 开发, 实现 |
| 审查验收 | `agent/sub-agents/reviewer.md` | reviewer, 审查, 验收, 测试, QA |

如果用户未明确指定角色，根据当前上下文推断：
- 刚完成需求调研 → 下一步是架构设计
- 刚完成架构设计 → 下一步是编码开发
- 刚完成编码 → 下一步是审查验收
- 刚完成审查/发现 bug → 下一步是编码（修复）

### Step 2: 读取角色定义

读取 `agent/sub-agents/{role}.md`，提取：
- 角色定位描述（用于提示词开头）
- 必须加载的文件列表（填入提示词）
- 按需加载的文件列表（填入提示词）
- 不要加载的文件列表（填入提示词）
- 工作流程步骤（填入提示词）

### Step 3: 读取项目状态

读取以下文件获取当前项目上下文：

| 文件 | 提取什么 |
|------|----------|
| `agent/memory-bank/active-context.md` | 当前阶段、下一步行动、已知阻塞 |
| `agent/memory-bank/progress.md` | 各模块完成状态 |
| `agent/memory-bank/system-patterns.md` | 当前架构约束（架构/编码角色需要） |

### Step 4: 了解具体任务

如果用户已说明具体任务，直接使用。
如果未说明，根据项目状态推断最可能的下一步任务，向用户确认。

任务描述要包含：
- **做什么**：具体的功能/模块/问题
- **输入是什么**：需求文档/设计文档/代码变更的位置
- **产出是什么**：文档/代码/报告的位置和格式
- **约束条件**：优先级、时间、依赖

### Step 5: 按模板生成提示词

根据目标角色，使用下方对应模板生成。模板中 `[方括号]` 内容需要根据实际情况填充。

---

## 角色提示词模板

### 产品设计 启动提示词模板

```
## 当前角色：产品设计

读取以下文件建立项目上下文：
- agent/sub-agents/product-manager.md（你的角色定义与工作流程）
- agent/memory-bank/projectbrief.md（项目定位与范围）
- agent/memory-bank/product-context.md（用户画像与核心体验）
- agent/memory-bank/active-context.md（当前开发进度）
- agent/memory-bank/progress.md（模块完成状态）

本会话目标：[具体任务描述，例如：调研网格交易策略模块的功能需求]

期望产出：
- 需求文档写入 docs/features/[feature-name].md
- 更新 agent/memory-bank/active-context.md

注意：
- 不要做技术设计，那是架构师的职责
- 不要写代码，那是编码者的职责
- 验收标准必须可测试，不能写"用户体验好"
- 每次只推 1-2 个需求，避免资源分散
```

### 架构设计 启动提示词模板

```
## 当前角色：架构设计

读取以下文件建立项目上下文：
- agent/sub-agents/architect.md（你的角色定义与工作流程）
- agent/memory-bank/system-patterns.md（现有架构约束与模式）
- agent/memory-bank/active-context.md（当前进度与阻塞）
- agent/memory-bank/tech-context.md（技术栈与工具链）
- agent/memory-bank/progress.md（模块完成状态）
- agent/memory/session-framework.md（设计会话框架）

按需读取：
- docs/features/[feature-name].md（当前待设计的需求文档）
- docs/modules/module-N-*.md（已有模块的设计文档）
- agent/specs/api-design.md / database.md / backend-architecture.md / frontend-architecture.md

本会话目标：[具体任务描述，例如：设计 Module 5 网格交易的接口与数据模型]

期望产出：
- 设计文档写入 docs/modules/module-[N]-[name].md
- 如有架构级变更，更新 agent/memory-bank/system-patterns.md
- 更新 agent/memory-bank/active-context.md

注意：
- 不要写代码，那是编码者的职责
- 不要做产品决策（"做不做"是产品的职责）
- 先读需求文档，确认理解需求意图后再开始设计
- 新设计必须与 system-patterns.md 中的已有模式对齐
- 接口参数、返回格式、错误码必须明确
```

### 编码开发 启动提示词模板

```
## 当前角色：编码开发

读取以下文件建立项目上下文：
- agent/sub-agents/coder.md（你的角色定义与工作流程）
- agent/specs/coding-style.md（编码风格约定）
- agent/specs/api-design.md（API 设计规范）
- agent/specs/database.md（数据库设计规范）
- agent/specs/backend-architecture.md（后端分层规范）
- agent/specs/frontend-architecture.md（前端架构规范）
- agent/sop/new-feature.md（新功能开发流程）

按需读取：
- docs/modules/module-[N]-[name].md（当前要实现的模块设计文档）
- agent/specs/git-flow.md（Git 提交规范）
- agent/specs/testing.md（测试规范）

本会话目标：[具体任务描述，例如：实现 Module 5 网格交易的后端接口]

期望产出：
- 后端代码：backend/app/
- 前端代码：frontend/src/（如涉及）
- 测试代码：tests/
- 开发日志：agent/memory/[YYYY-MM-DD].md
- 更新 agent/memory-bank/active-context.md

注意：
- 严格按设计文档实现，不要自行修改设计
- 遵循 agent/specs/coding-style.md 中的所有约定
- 不引入魔法数字（用常量或配置）
- 函数不超过 50 行，嵌套不超过 3 层
- 写完代码必须自测（启动服务 + 验证接口 + 运行 pytest）
- 自测通过后再提交
```

### 审查验收 启动提示词模板

```
## 当前角色：审查验收

读取以下文件建立项目上下文：
- agent/sub-agents/reviewer.md（你的角色定义与工作流程）
- agent/specs/testing.md（测试规范）
- agent/specs/coding-style.md（编码风格，审查依据）
- agent/specs/api-design.md（API 设计规范，审查依据）
- agent/sop/bug-fix.md（Bug 修复流程）

按需读取：
- docs/modules/module-[N]-[name].md（对应模块的设计文档，审查依据）
- docs/features/[feature-name].md（需求文档，验收标准）
- agent/sop/deployment.md（部署流程，部署验证用）
- agent/memory-bank/active-context.md（当前进度）

本会话目标：[具体任务描述，例如：审查 Module 5 网格交易的代码实现]

期望产出：
- 验收报告写入 docs/acceptance-report-[YYYYMMDD].md
- 如有 Bug，记录到 agent/memory/[YYYY-MM-DD].md

注意：
- 先读设计文档和需求文档，再看代码
- 不要自己修改代码，标记问题让编码者修
- 对照需求文档逐条检查验收标准
- 运行全量测试：pytest --cov=app
- 手动验证关键流程（启动服务 + curl 接口）
- 安全性检查：认证、数据隔离、SQL 注入防护
```

---

## 使用示例

### 示例 1：需求调研完成后，生成架构师提示词

**用户：** 需求文档写好了，帮我准备架构师的新会话提示词

**生成：**

```
## 当前角色：架构设计

读取以下文件建立项目上下文：
- agent/sub-agents/architect.md（你的角色定义与工作流程）
- agent/memory-bank/system-patterns.md（现有架构约束与模式）
- agent/memory-bank/active-context.md（当前进度与阻塞）
- agent/memory-bank/tech-context.md（技术栈与工具链）
- agent/memory-bank/progress.md（模块完成状态）
- agent/memory/session-framework.md（设计会话框架）

按需读取：
- docs/features/grid-trading-strategy.md（需求文档）
- docs/modules/module-1-data-service.md（数据服务设计）
- agent/specs/api-design.md / database.md

本会话目标：设计网格交易策略模块的接口与数据模型

期望产出：
- 设计文档写入 docs/modules/module-5-grid-trading.md
- 更新 agent/memory-bank/system-patterns.md（如有架构变更）
- 更新 agent/memory-bank/active-context.md

注意：
- 先读需求文档 docs/features/grid-trading-strategy.md
- 按 session-framework.md 的分层决策模式推进
- 新设计必须与 system-patterns.md 中的已有模式对齐
```

### 示例 2：架构设计完成后，生成编码者提示词

**用户：** 架构文档写好了，给我 coder 的启动提示词

**生成：**

```
## 当前角色：编码开发

读取以下文件建立项目上下文：
- agent/sub-agents/coder.md（你的角色定义与工作流程）
- agent/specs/coding-style.md（编码风格约定）
- agent/specs/api-design.md（API 设计规范）
- agent/specs/database.md（数据库设计规范）
- agent/specs/backend-architecture.md（后端分层规范）
- agent/specs/frontend-architecture.md（前端架构规范）
- agent/sop/new-feature.md（新功能开发流程）

按需读取：
- docs/modules/module-5-grid-trading.md（设计文档）
- agent/specs/git-flow.md / testing.md

本会话目标：按设计文档实现网格交易模块的后端接口

期望产出：
- 后端代码：backend/app/
- 测试代码：tests/
- 开发日志：agent/memory/[YYYY-MM-DD].md

注意：
- 严格按 docs/modules/module-5-grid-trading.md 实现
- Model → Service → Route 分层实现
- 每个接口实现后自测确认
```

---

## 定制指南

### 根据任务类型调整

| 任务类型 | 特殊调整 |
|---------|---------|
| 新功能开发 | 完整流程：产品→架构→编码→审查，每个角色单独会话 |
| Bug 修复 | 跳过产品和架构，直接生成 coder 提示词，附加 agent/sop/bug-fix.md |
| 重构 | 生成 architect 提示词，明确重构范围和约束 |
| 部署 | 生成 reviewer 提示词，附加 agent/sop/deployment.md |
| 需求调研 | 生成 product-manager 提示词，明确调研方向 |

### 根据项目阶段调整

| 阶段 | 额外上下文 |
|------|-----------|
| MVP 早期 | 强调"先跑通，不求完美" |
| 功能迭代 | 强调"最小改动，不引入回归" |
| 上线前 | 强调"测试覆盖，安全检查" |
| 线上运维 | 强调"稳定性优先，灰度变更" |

### 多文件任务

当任务涉及多个模块/文件时，在提示词中列出具体文件清单：

```
本会话涉及以下文件：
- backend/app/services/grid_engine.py（核心引擎）
- backend/app/routes/grid.py（API 路由）
- frontend/src/components/GridCard.vue（前端卡片）
- tests/unit/test_grid_engine.py（单元测试）
```
