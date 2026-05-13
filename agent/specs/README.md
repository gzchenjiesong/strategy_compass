---
title: 技术规范总览
created: 2026-05-13
version: 1.1.0
---

# 技术规范总览

> 项目必须遵守的技术标准和规范。

## 规范列表

| 规范 | 文件 | 说明 | 适用角色 |
|------|------|------|----------|
| [Active Context 结构](active-context-schema.md) | `active-context-schema.md` | active-context.md 的统一结构 | 所有角色 |
| [文档版本管理](document-versioning.md) | `document-versioning.md` | SemVer 简化版 + 变更日志规范 | 所有角色 |
| [代码风格规范](code-style-guide.md) | `code-style-guide.md` | 命名、注释、错误处理、日志、测试 | 编码者、审查者 |
| [安全编码规范](security-coding-standard.md) | `security-coding-standard.md` | 输入验证、认证授权、敏感数据处理 | 编码者、审查者 |

## 规范与 SOP 的关系

| 类型 | 内容 | 作用 |
|------|------|------|
| **Spec（规范）** | 标准（写什么、怎么写、禁止什么） | 规范**产出** |
| **SOP（流程）** | 流程（何时审、谁审、怎么处理） | 规范**行为** |

编码者编码前阅读 Spec，知道"应该怎么做"。
审查者审查时对照 Spec，检查"是否做到了"。

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.1.0 | 2026-05-13 | 新增代码风格规范、安全编码规范 |
| v1.0.0 | 2026-05-13 | 初始版本（Active Context 结构、文档版本管理） |
