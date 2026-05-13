# 文档版本控制规范

> 定义项目文档的版本号规则、变更日志格式和升级流程。
> 所有 `agent/` 和 `docs/` 目录下的文档都必须遵循本规范。

---

## 版本号规则

采用**语义化版本**（Semantic Versioning）：`主版本.次版本.修订号`

| 版本段 | 说明 | 何时递增 |
|--------|------|----------|
| 主版本 (X) | 重大结构变更 | 文档整体结构重组、章节增删 |
| 次版本 (Y) | 内容扩展 | 新增章节、新增示例、覆盖范围扩大 |
| 修订号 (Z) | 修正和优化 | 错别字、格式调整、链接修复、小范围内容更新 |

**示例：**
- `v1.0.0` — 初始版本
- `v1.1.0` — 新增"冲突处理"章节
- `v1.1.1` — 修正链接错误
- `v2.0.0` — 整体结构重组

---

## 版本标记位置

### 1. Frontmatter（首选）

在文档开头添加 YAML frontmatter：

```markdown
---
role: [角色/类型]
title: [文档标题]
created: YYYY-MM-DD
version: X.Y.Z
---
```

**示例：**
```markdown
---
role: sop
title: Agent 记忆 Handoff 机制
created: 2026-05-13
version: 1.0.0
---
```

### 2. 文档内标题（备选）

如果文档已有固定格式无法添加 frontmatter，在标题下方标注：

```markdown
# 文档标题

> 版本：v1.0.0 | 创建日期：2026-05-13 | 最后更新：2026-05-13
```

---

## 变更日志格式

在文档末尾添加 `## 变更历史` 章节：

```markdown
## 变更历史

| 版本 | 日期 | 变更类型 | 变更内容 | 作者 |
|------|------|----------|----------|------|
| v1.1.0 | 2026-05-14 | 新增 | 增加"冲突处理机制"章节 | architect |
| v1.0.1 | 2026-05-13 | 修正 | 修正文件路径引用错误 | coder |
| v1.0.0 | 2026-05-13 | 初始 | 创建文档 | architect |
```

### 变更类型

| 类型 | 说明 |
|------|------|
| 初始 | 文档首次创建 |
| 新增 | 新增章节或内容 |
| 修改 | 修改现有内容 |
| 删除 | 删除章节或内容 |
| 修正 | 修正错误（错别字、链接、格式） |
| 重构 | 结构调整，内容不变 |

---

## 升级流程

### 小版本升级（修订号 +1）

**触发条件：**
- 修正错别字或格式
- 修复链接错误
- 小范围内容更新（不影响整体理解）

**流程：**
1. 修改文档内容
2. 更新 frontmatter 中的 `version`（Z + 1）
3. 在变更日志中新增一行
4. 无需通知其他角色

### 中版本升级（次版本 +1）

**触发条件：**
- 新增章节
- 新增示例
- 覆盖范围扩大
- 流程优化（不改变整体结构）

**流程：**
1. 修改文档内容
2. 更新 frontmatter 中的 `version`（Y + 1, Z = 0）
3. 在变更日志中新增一行
4. 在 `agent/memory-bank/active-context.md` 的 `## 最近变更` 中记录
5. 如涉及其他角色，在 `agent/memory/YYYY-MM-DD.md` 中通知

### 大版本升级（主版本 +1）

**触发条件：**
- 文档整体结构重组
- 核心概念变更
- 与其他文档的依赖关系重大调整

**流程：**
1. 修改文档内容
2. 更新 frontmatter 中的 `version`（X + 1, Y = 0, Z = 0）
3. 在变更日志中新增一行
4. 在 `agent/memory-bank/active-context.md` 的 `## 最近变更` 中记录
5. 检查所有引用本文档的其他文档，更新引用
6. 在 `agent/memory/YYYY-MM-DD.md` 中详细说明变更原因和影响

---

## 文档依赖管理

### 依赖声明

如果文档 A 引用了文档 B 的内容，在文档 A 的 frontmatter 中声明依赖：

```markdown
---
role: sop
title: Agent 记忆 Handoff 机制
created: 2026-05-13
version: 1.0.0
dependencies:
  - agent/specs/active-context-schema.md >= 1.0.0
  - agent/sub-agents/product-manager.md >= 0.1.0
---
```

### 依赖检查

当文档 B 升级时，检查所有依赖 B 的文档：

1. **修订号升级** — 通常不影响依赖文档
2. **次版本升级** — 检查依赖文档是否需要同步更新
3. **主版本升级** — 必须检查并更新所有依赖文档

**检查命令：**
```bash
# 查找所有引用本文档的文件
grep -r "agent/specs/active-context-schema.md" agent/ docs/
```

---

## 废弃文档处理

### 标记废弃

当文档不再使用时，不要删除，而是标记为废弃：

```markdown
---
role: sop
title: 旧版部署流程
created: 2026-05-10
version: 1.0.0
status: deprecated
replaced_by: agent/sop/deployment.md
---

> ⚠️ **本文档已废弃**
> 
> 请使用新版文档：`agent/sop/deployment.md`
> 
> 废弃原因：部署架构从单容器改为 Docker Compose
> 
> 废弃日期：2026-05-13
```

### 清理规则

- 废弃文档保留至少 **30 天**
- 30 天后可移动到 `agent/archive/` 或 `docs/archive/`
- 归档时保留变更历史，便于追溯

---

## 检查清单

创建或更新文档时确认：

- [ ] 文档有 frontmatter（或标题下方的版本标记）
- [ ] `version` 字段正确
- [ ] `created` 字段正确
- [ ] 变更历史已更新（如适用）
- [ ] 依赖文档已声明（如适用）
- [ ] 废弃文档已标记（如适用）
- [ ] 所有引用本文档的其他文档已检查（大版本升级时）

---

## 示例

### 完整示例

```markdown
---
role: sop
title: Agent 记忆 Handoff 机制
created: 2026-05-13
version: 1.1.0
dependencies:
  - agent/specs/active-context-schema.md >= 1.0.0
---

# Agent 记忆 Handoff 机制

## 目的
...

## Handoff 流水线
...

## 变更历史

| 版本 | 日期 | 变更类型 | 变更内容 | 作者 |
|------|------|----------|----------|------|
| v1.1.0 | 2026-05-14 | 新增 | 增加"冲突处理机制"章节 | architect |
| v1.0.0 | 2026-05-13 | 初始 | 创建文档 | architect |
```

---

## 附录：已有文档版本状态

| 文档 | 当前版本 | 最后更新 | 状态 |
|------|----------|----------|------|
| agent/sop/agent-handoff.md | 1.0.0 | 2026-05-13 | ✅ 已标记 |
| agent/specs/active-context-schema.md | 1.0.0 | 2026-05-13 | ✅ 已标记 |
| agent/sub-agents/startup-templates.md | 1.0.0 | 2026-05-13 | ✅ 已标记 |
| docs/traceability-matrix.md | 1.0.0 | 2026-05-13 | ✅ 已标记 |
| agent/specs/document-versioning.md | 1.0.0 | 2026-05-13 | ✅ 已标记 |

**待标记文档（需补录版本信息）：**
- agent/sub-agents/product-manager.md
- agent/sub-agents/architect.md
- agent/sub-agents/coder.md
- agent/sub-agents/reviewer.md
- agent/memory-bank/*.md
- agent/sop/*.md
- agent/specs/*.md
- docs/modules/*.md
- docs/features/*.md
