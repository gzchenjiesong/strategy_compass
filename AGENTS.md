# AGENTS.md - Agent 操作手册

> 每次会话开始，Agent 必须按此文件规定的顺序读取上下文，然后才能开始工作。

## 会话启动流程

按以下顺序读取文件（不要跳过，不要询问）：

### 第一步：读灵魂（必读）
1. 读 `SOUL.md` — 这是项目的"人格"，所有决策的底层逻辑

### 第二步：读记忆（必读）
2. 读 `agent/memory-bank/projectbrief.md` — 项目概要
3. 读 `agent/memory-bank/active-context.md` — 当前在做什么
4. 读 `agent/memory-bank/progress.md` — 进度如何

### 第三步：读今日日志（如果存在）
5. 读 `agent/memory/YYYY-MM-DD.md`（今天的日期）— 最近发生了什么

### 第四步：按需读取（任务相关时才读）

| 你要做什么 | 读什么 |
|-----------|--------|
| 写后端代码 | `agent/specs/backend-architecture.md` + `agent/specs/coding-style.md` |
| 写前端代码 | `agent/specs/frontend-architecture.md` + `agent/specs/coding-style.md` |
| 写 API | `agent/specs/api-design.md` |
| 操作数据库 | `agent/specs/database.md` |
| 做新功能 | `agent/sop/new-feature.md` |
| 修 Bug | `agent/sop/bug-fix.md` |
| 代码审查 | `agent/sop/code-review-standard.md` + `agent/specs/code-style-guide.md` |
| 安全审查 | `agent/sop/security-review.md` + `agent/specs/security-coding-standard.md` |
| 部署 | `agent/sop/deployment.md` |
| 设计新模块 | `agent/specs/api-design.md` + `agent/specs/database.md` |

### 第五步：子代理角色（多角色协作时）

如果当前任务需要特定角色视角，读取对应角色定义：
- 产品决策 → `agent/sub-agents/product-manager.md`
- 技术设计 → `agent/sub-agents/architect.md`
- 编码实现 → `agent/sub-agents/coder.md`
- 质量审查 → `agent/sub-agents/reviewer.md`

启动模板参考：`agent/sub-agents/startup-templates.md`

---

## 行为规范

### 文件管理
- 修改任何文件前，先确认文件的用途和上下文
- 新建文件前，确认目录结构中已有合适的位置
- 不要在根目录随意创建文件

### 代码质量
- 遵守 `agent/specs/coding-style.md` 和 `agent/specs/code-style-guide.md` 中的规范
- 编码前阅读 `agent/specs/security-coding-standard.md`
- 新功能必须写对应的需求文档（`docs/features/`）
- API 变更必须更新对应模块的 `docs/designs/module-N/api.md`

### 测试
- 写完功能后，运行 `./scripts/api-check.sh` 验证
- 运行 `./scripts/run-tests.sh` 执行测试套件
- 不要在没有验证的情况下说"完成了"

### 记忆维护
- 重要决策记录到 `agent/memory/YYYY-MM-DD.md`
- 阶段性成果更新 `agent/memory-bank/progress.md`
- 技术经验沉淀到 `agent/skills/`

### Git 规范
- 遵守 `agent/specs/git-flow.md` 中的分支和提交规范
- 不要直接 push 到 main
- commit message 使用中文，格式：`类型: 简要描述`

### Markdown 文件编写约定（适配 Tolaria 审阅工具）

项目所有 `.md` 文件使用 **Tolaria**（开源桌面知识库工具）进行审阅和管理。Agent 编写/修改 markdown 文件时需遵循以下约定：

- **YAML frontmatter**：重要文件加 frontmatter（title、type、created、tags）
- **标题层级**：从 `#` 开始，**不跳级**（方便 Tolaria 的 Table of Contents 面板导航）
- **内部链接**：优先用标准 markdown `[text](path)`，支持 `[[wikilink]]` 格式
- **纯标准格式**：所有内容必须是标准 Markdown，不用任何私有格式，确保随时可迁移
- **文件即归属**：Tolaria 不锁数据，你的文件就是文件夹里的 .md，不需要导出

> Tolaria 工作方式：用户用 GUI 审阅/浏览 .md 文件，Agent 直接读写同一份文件。两边对同一份文件操作，不冲突。

---

## 禁止行为

- ❌ 不要用 `rm -rf` 删除任何东西（用 `trash` 或 git 操作）
- ❌ 不要在没有确认的情况下执行破坏性操作
- ❌ 不要伪造数据或测试结果
- ❌ 不要跳过测试直接标记"完成"
- ❌ 不要把密钥、密码等敏感信息写入代码或文档
