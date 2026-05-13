---
title: 安全编码规范
created: 2026-05-13
version: 1.0.0
status: active
---

# 安全编码规范

> 所有代码必须遵守的安全标准。违反任何一条视为阻塞性问题。

## 1. 输入验证

### 1.1 所有外部输入必须校验
- 用户提交的表单数据
- URL 参数
- 请求体 JSON
- 文件上传

**正确示例：**
```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    name: str
    age: int

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('name cannot be empty')
        return v.strip()
```

### 1.2 禁止使用危险函数
- ❌ `eval()`, `exec()` — 使用 `ast.literal_eval()` 或 JSON 解析替代
- ❌ `pickle.loads()` 处理不可信数据 — 使用 JSON
- ❌ 动态 SQL 拼接 — 使用参数化查询

### 1.3 文件上传限制
- 限制文件类型（白名单）
- 限制文件大小
- 存储路径与执行路径分离
- 重命名上传文件（避免覆盖）

## 2. 认证与授权

### 2.1 API 认证
- 所有非公开 API 必须验证 JWT Token
- Token 有效期 ≤ 24 小时
- 刷新 Token 机制独立

### 2.2 权限校验
- 敏感操作必须校验用户权限
- 禁止通过修改 client-side 参数绕过权限
- 用户数据查询必须带 `user_id` 过滤

**正确示例：**
```python
@router.get("/api/user/favorites")
async def get_favorites(current_user: User = Depends(get_current_user)):
    # 自动从 Token 解析 user_id，不允许传参指定
    return await favorite_service.get_by_user(current_user.id)
```

### 2.3 禁止硬编码凭证
- ❌ 密码、API Key、Secret 不得硬编码
- ✅ 使用环境变量或配置中心

## 3. 敏感数据处理

### 3.1 密码存储
- 必须使用 bcrypt（cost ≥ 12）
- 禁止明文存储、禁止 MD5/SHA1

### 3.2 日志脱敏
- 日志中禁止输出：密码、Token、身份证号、银行卡号
- 手机号、邮箱部分掩码

**正确示例：**
```python
# ❌ 错误
logger.info(f"User login: {user.email}, password: {password}")

# ✅ 正确
logger.info(f"User login: {mask_email(user.email)}")
```

### 3.3 错误信息
- 对外返回的错误信息不得暴露内部细节
- 内部错误记录到日志，对外返回通用错误码

**正确示例：**
```python
# ❌ 错误
return {"error": f"Database connection failed: {db_host}:{db_port}"}

# ✅ 正确
logger.error(f"Database connection failed: {db_host}:{db_port}")
return {"error": "Internal server error", "code": "DB_001"}
```

## 4. 通信安全

### 4.1 HTTPS
- 生产环境强制 HTTPS
- HSTS 头部
- Cookie 设置 Secure、HttpOnly、SameSite

### 4.2 CORS
- 白名单配置，禁止 `*`
- 根据环境区分配置

### 4.3 速率限制
- 登录接口：5 次/分钟
- 敏感操作：10 次/分钟
- 通用 API：100 次/分钟

## 5. 依赖安全

### 5.1 依赖审查
- 新增依赖必须审查许可证（禁止 GPL）
- 定期检查已知漏洞（`pip-audit`, `npm audit`）
- 锁定版本（requirements.txt / package-lock.json）

## 合规检查清单

编码完成后自查：

- [ ] 所有外部输入都有校验
- [ ] 没有使用 eval/exec/pickle
- [ ] 没有硬编码密码/密钥
- [ ] 密码使用 bcrypt 存储
- [ ] 日志中没有敏感信息
- [ ] 错误信息不暴露内部细节
- [ ] API 有认证保护
- [ ] 用户数据查询有 user_id 过滤

## 关联文档

- [安全审查 SOP](../sop/security-review.md) — 审查流程
- [代码风格规范](code-style-guide.md) — 通用编码规范

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-05-13 | 初始版本，从安全审查 SOP 提取规则部分 |
