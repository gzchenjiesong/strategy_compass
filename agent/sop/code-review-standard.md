---
title: Code Review Standard SOP
type: sop
created: 2026-05-13
tags: [code-quality, review, collaboration]
---

# Detailed Code Review Standards

> 代码审查的详细标准和流程。

## 审查依据

**主要依据：** [代码风格规范](../specs/code-style-guide.md)

审查者对照编码规范逐项检查，确保代码风格、质量和安全要求已落实。

## 审查范围

Every non-trivial change must be reviewed. Trivial changes (typo fixes, comment updates) may be self-merged with a note.

## Reviewer Assignment

- Author suggests 1–2 reviewers based on `MODULE_OWNERS.md`
- At least one reviewer must be from a different agent/role
- Security-sensitive changes require a security reviewer

## Review Checklist

### 功能性
- [ ] 代码实现了需求描述的功能
- [ ] 边界条件被正确处理
- [ ] 错误路径有测试覆盖

### 可读性
- [ ] 命名清晰，符合代码风格规范
- [ ] 函数长度合理（≤ 50 行）
- [ ] 注释恰当（复杂逻辑有解释，无冗余注释）

### 安全性
- [ ] 对照 [安全编码规范](../specs/security-coding-standard.md) 检查
- [ ] 输入验证完整
- [ ] 无敏感信息泄露

### 性能
- [ ] 无明显的 N+1 查询
- [ ] 大数据量处理有分页或流式
- [ ] 缓存策略合理

### 测试
- [ ] 新增代码有对应的测试
- [ ] 测试覆盖了正常和异常路径
- [ ] 核心逻辑覆盖率 ≥ 80%

## Scoring Criteria

| 维度 | 权重 | 说明 |
|------|------|------|
| 功能正确性 | 30% | 是否满足需求 |
| 代码质量 | 25% | 可读性、可维护性 |
| 安全性 | 20% | 是否符合安全编码规范 |
| 测试覆盖 | 15% | 测试完整度 |
| 性能 | 10% | 无 obvious 性能问题 |

## Merge Rules

- **Approve**: All checks pass, score ≥ 80%
- **Conditional Approve**: Minor issues, score 60-79%, must fix before merge
- **Reject**: Major issues, score < 60%, requires re-review

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.1.0 | 2026-05-13 | 添加对代码风格规范的引用，明确审查依据 |
| v1.0.0 | 2026-05-13 | 初始版本 |
