---
title: "Module 0: 用户系统 — 接口与数据模型设计"
type: spec
module: module-0
layer: Layer 2
status: draft
created: 2026-05-07
author: 顾清辞
---

## 5. 核心业务逻辑

### 5.1 微信登录流程（Service 伪代码）

```python
class AuthService:

    def wechat_callback(self, code: str, invitation_code: str | None = None):
        # 1. 用 code 换 access_token
        token_resp = wechat_api.get_access_token(code)
        if token_resp.error:
            raise AppError("INVALID_CODE")

        openid = token_resp.openid
        unionid = token_resp.get("unionid")

        # 2. 查是否已注册
        user = User.query.filter(
            (User.openid == openid) | (User.unionid == unionid)
        ).first()

        if user:
            # 老用户 → 更新登录时间，签发 JWT
            user.last_login_at = now()
            user.save()
            return {"token": jwt_encode(user.id), "user": user}

        # 3. 新用户
        user_info = wechat_api.get_user_info(token_resp.access_token, openid)

        if not invitation_code:
            # 未提供邀请码 → 返回"需要邀请码"
            return {
                "status": "need_invitation_code",
                "openid": openid,
                "nickname": user_info.nickname,
                "avatar_url": user_info.avatar_url
            }

        # 4. 有邀请码 → 校验
        code_record = InvitationCode.validate(invitation_code)
        if not code_record:
            raise AppError("INVALID_INVITATION_CODE")

        # 5. 创建用户
        user = User.create(
            openid=openid,
            unionid=unionid,
            nickname=user_info.nickname,
            avatar_url=user_info.avatar_url,
            invitation_code=invitation_code
        )
        code_record.use()

        # 6. 创建默认数据
        Watchlist.create_default(user.id)
        Preference.create_defaults(user.id)

        return {"token": jwt_encode(user.id), "user": user}
```

### 5.2 邀请码校验逻辑

```python
class InvitationCode:

    @classmethod
    def validate(cls, code: str) -> 'InvitationCode | None':
        record = cls.query.filter_by(code=code, status='active').first()
        if not record:
            return None
        # 检查过期
        if record.expires_at and record.expires_at < now():
            return None
        # 检查次数
        if record.max_uses != -1 and record.used_count >= record.max_uses:
            return None
        return record

    def use(self):
        self.used_count += 1
        if self.max_uses != -1 and self.used_count >= self.max_uses:
            self.status = 'disabled'
        self.save()
```

### 5.3 JWT 认证中间件

```python
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise AppError("UNAUTHORIZED", status=401)

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AppError("TOKEN_EXPIRED", status=401)
        except jwt.InvalidTokenError:
            raise AppError("INVALID_TOKEN", status=401)

        user = User.query.get(payload["user_id"])
        if not user or user.status != "active":
            raise AppError("USER_INACTIVE", status=403)

        g.current_user = user
        return f(*args, **kwargs)
    return decorated
```

