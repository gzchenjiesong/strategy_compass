---
role: sop
title: Agent 记忆 Handoff 机制
created: 2026-05-13
version: 1.0
---

# Agent 记忆 Handoff 机制

## 目的

Sub-agent 之间切换时，关键信息必须通过文件传递，不能依赖会话上下文。
本文档定义：**什么信息需要 handoff、写在哪里、接收方怎么读**。

---

## Handoff 流水线

```
产品(product-manager) → 架构(architect) → 编码(coder) → 审查(reviewer)
```

每个箭头代表一次 handoff，有固定的**产出文件**和**读取规范**。

---

## 各角色 Handoff 规范

### 1. 产品设计 → 架构设计

**触发时机：** 需求文档定稿，可以进入技术设计

**产出文件：**
- `docs/features/{feature-name}.md` — 需求文档（必须）
- `agent/memory-bank/active-context.md` — 更新"当前待设计需求"章节

**`active-context.md` 更新格式：**
```markdown
## 当前待设计需求
- {feature-name}：{一句话描述}，优先级 P0/P1/P2，需求文档 docs/features/{feature-name}.md
```

**架构师读取规范：**
1. 先读 `agent/memory-bank/active-context.md` 找到待设计需求
2. 再读对应的 `docs/features/{feature-name}.md`
3. 如有疑问，在需求文档中标注 `> [疑问] ...`，不修改需求内容

---

### 2. 架构设计 → 编码开发

**触发时机：** 设计文档定稿，可以进入编码

**产出文件：**
- `docs/modules/module-{N}-{name}.md` — 模块设计文档（必须）
- `agent/memory-bank/active-context.md` — 更新"当前待编码模块"章节
- `agent/memory-bank/system-patterns.md` — 如有架构级变更（可选）

**`active-context.md` 更新格式：**
```markdown
## 当前待编码模块
- Module {N}：{模块名}，设计文档 docs/modules/module-{N}-{name}.md，依赖：{无/Module X}
```

**编码者读取规范：**
1. 先读 `agent/memory-bank/active-context.md` 找到待编码模块
2. 再读对应的 `docs/modules/module-{N}-{name}.md`
3. 严格按设计文档实现，如有设计问题，在 `agent/memory/YYYY-MM-DD.md` 中记录并 `@architect`

---

### 3. 编码开发 → 审查验收

**触发时机：** 编码完成，自测通过，准备提 PR

**产出文件：**
- 代码变更（PR 或 commit range）
- `agent/memory/YYYY-MM-DD.md` — 开发日志（必须）
- `agent/memory-bank/active-context.md` — 更新"当前待审查"章节

**`active-context.md` 更新格式：**
```markdown
## 当前待审查
- Module {N}：{模块名}，PR #{number}，开发日志 agent/memory/YYYY-MM-DD.md
```

**审查者读取规范：**
1. 先读 `agent/memory-bank/active-context.md` 找到待审查项
2. 读对应的设计文档 `docs/modules/module-{N}-{name}.md`
3. 读需求文档 `docs/features/{feature-name}.md`（验收标准）
4. 审查代码，输出 `docs/acceptance-report-YYYYMMDD.md`

---

### 4. 审查验收 → ⎵（闭环或回退）

**审查通过：**
- 更新 `agent/memory-bank/progress.md`（标记模块完成）
- 更新 `agent/memory-bank/active-context.md`（清除"当前待审查"）
- 如有下一步需求，写回 product-manager 的待处理队列

**审查不通过（回退编码）：**
- 验收报告中列出所有问题，标注严重度 P0/P1/P2
- 更新 `agent/memory-bank/active-context.md`："当前待修复：PR #{number}，见验收报告 docs/acceptance-report-YYYYMMDD.md"
- 编码者根据验收报告修复，修复完成后再次触发审查

---

## Handoff 状态追踪

在 `agent/memory-bank/active-context.md` 中维护一个统一的状态表：

```markdown
## 任务流水线状态

| 需求 | 产品 | 架构 | 编码 | 审查 | 状态 |
|------|------|------|------|------|------|
| {feature-name} | ✅ | ✅ | 🔄 | ⏳ | 编码中 |
```

状态说明：
- ✅ 完成
- 🔄 进行中
- ⏳ 等待中
- ❌ 阻塞（附原因）

---

## 跨角色反馈规范

不是所有沟通都需要正式 handoff，轻量级反馈用 `agent/memory/YYYY-MM-DD.md`：

### 编码者 → 架构师（设计问题反馈）
在开发日志中写：
```
> [设计反馈] Module {N}：{问题描述}，建议 {修改方案}，@architect
```

### 编码者 → 产品（需求问题反馈）
在开发日志中写：
```
> [需求反馈] {feature-name}：{问题描述}，实际实现中发现 {偏差}，@product-manager
```

### 审查者 → 编码者（问题列表）
在验收报告中写，编码者根据报告修复。

### 审查者 → 架构师（设计改进建议）
在验收报告中加"设计改进建议"章节。

---

## 文件权限矩阵

| 文件 | 产品 | 架构 | 编码 | 审查 |
|------|------|------|------|------|
| `docs/features/*.md` | 写 | 读 | 不读 | 读 |
| `docs/modules/*.md` | 不读 | 写 | 读 | 读 |
| `agent/memory-bank/active-context.md` | 更新 | 更新 | 更新 | 更新 |
| `agent/memory-bank/system-patterns.md` | 不读 | 写/更新 | 读 | 读 |
| `agent/memory/YYYY-MM-DD.md` | 读（反馈） | 读（反馈） | 写 | 读 |
| `docs/acceptance-report-*.md` | 读 | 读 | 不读 | 写 |

---

## 检查清单

每次 handoff 前确认：

- [ ] 产出文件已写入磁盘（不只停留在会话上下文）
- [ ] `active-context.md` 已更新对应状态
- [ ] 文件中的路径引用是正确的相对路径
- [ ] 没有把关键信息只写在聊天记录里
- [ ] 下一个角色能通过 `active-context.md` 找到所有需要读的文件
