---
title: Security Review SOP
type: sop
created: 2026-05-13
tags: [security, compliance, review]
---

# Security Review SOP

> 代码提交前的安全检查清单和流程。

## 审查时机

- 每次提交代码前（编码者自查）
- 每次合并到 develop 前（审查者复查）
- 每次部署到生产前（强制检查）

## 审查依据

**主要依据：** [安全编码规范](../specs/security-coding-standard.md)

审查者对照编码规范逐项检查，确保所有安全要求已落实。

## 安全检查清单

### 认证与授权

- [ ] API 接口有认证保护（除公开接口外）
- [ ] 用户数据有隔离（user_id 验证）
- [ ] JWT Token 有有效期限制
- [ ] 敏感操作有权限校验

### 输入验证

- [ ] 所有用户输入都有校验
- [ ] SQL 参数使用绑定变量（防注入）
- [ ] 文件上传有类型和大小限制
- [ ] 特殊字符有转义处理

### 敏感数据

- [ ] 密码不明文存储（使用 bcrypt）
- [ ] API 密钥不在代码中硬编码
- [ ] 日志中不包含敏感信息
- [ ] 错误信息不暴露内部细节

### 通信安全

- [ ] 生产环境使用 HTTPS
- [ ] 敏感接口有速率限制
- [ ] CORS 配置正确

## 高危代码模式

| 模式 | 风险 | 正确做法 |
|------|------|----------|
| `eval()` / `exec()` | 代码注入 | 使用安全的替代方案 |
| 拼接 SQL | SQL 注入 | 使用参数化查询 |
| 明文存储密码 | 数据泄露 | 使用 bcrypt 哈希 |
| 不验证用户输入 | XSS/注入 | 输入校验 + 输出转义 |
| 硬编码密钥 | 密钥泄露 | 使用环境变量 |

## 审查流程

```
编码者自查（对照安全编码规范）
    ↓
审查者复查（对照安全编码规范）
    ↓
安全扫描（可选：Semgrep/CodeQL）
    ↓
通过 / 拒绝
```

## 工具推荐

- SAST: Semgrep, CodeQL, Bandit
- DAST: OWASP ZAP (scheduled scans)
- Secrets scanning: GitLeaks, TruffleHog
- Dependency scanning: Snyk, Dependabot

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.1.0 | 2026-05-13 | 添加对安全编码规范的引用，明确审查依据 |
| v1.0.0 | 2026-05-13 | 初始版本 |
