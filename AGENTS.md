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
- 要写代码 → 读 `agent/specs/coding-style.md`
- 要写 API → 读 `agent/specs/api-design.md`
- 要做新功能 → 读 `agent/sop/new-feature.md`
- 要修 Bug → 读 `agent/sop/bug-fix.md`
- 要部署 → 读 `agent/skills/deployment.md`

## 行为规范

### 文件管理
- 修改任何文件前，先确认文件的用途和上下文
- 新建文件前，确认目录结构中已有合适的位置
- 不要在根目录随意创建文件

### 代码质量
- 遵守 `agent/specs/coding-style.md` 中的规范
- 新功能必须写对应的文档（`docs/features/`）
- API 变更必须更新 `docs/api.md`

### 测试
- 写完功能后，必须运行 `./scripts/api-check.sh` 验证
- 验证结果写入 `build/test-results/`
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

## 禁止行为

- ❌ 不要用 `rm -rf` 删除任何东西（用 `trash` 或 git 操作）
- ❌ 不要在没有确认的情况下执行破坏性操作
- ❌ 不要伪造数据或测试结果
- ❌ 不要跳过测试直接标记"完成"
- ❌ 不要把密钥、密码等敏感信息写入代码或文档
