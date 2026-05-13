import jwt
import requests
from datetime import datetime, timedelta, timezone
from flask import current_app

from app import db
from app.models.user import User, InvitationCode, UserWatchlist, UserPreference
from app.utils.exceptions import (
    InvalidCode,
    InvalidInvitationCode,
    BindFailed,
)


class AuthService:
    def wechat_callback(self, code: str, invitation_code: str | None = None):
        appid = current_app.config.get("WECHAT_APPID")
        secret = current_app.config.get("WECHAT_SECRET")

        if not appid or not secret or appid == "test":
            return self._mock_wechat_callback(code, invitation_code)

        token_url = (
            f"https://api.weixin.qq.com/sns/oauth2/access_token"
            f"?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code"
        )
        resp = requests.get(token_url, timeout=10)
        data = resp.json()

        if "errcode" in data:
            raise InvalidCode()

        openid = data.get("openid")
        unionid = data.get("unionid")
        access_token = data.get("access_token")

        user = self._find_user(openid, unionid)
        if user:
            user.last_login_at = datetime.now(timezone.utc).isoformat()
            db.session.commit()
            return {"token": self._jwt_encode(user.id), "user": self._user_dict(user)}

        user_info = self._get_wechat_user_info(access_token, openid)
        if not invitation_code:
            return {
                "status": "need_invitation_code",
                "openid": openid,
                "nickname": user_info.get("nickname", "微信用户"),
                "avatar_url": user_info.get("headimgurl", ""),
            }

        return self._create_user(
            openid, unionid, user_info.get("nickname", "微信用户"),
            user_info.get("headimgurl", ""), invitation_code
        )

    def wechat_bind(self, openid: str, nickname: str, avatar_url: str, invitation_code: str):
        user = User.query.filter_by(openid=openid).first()
        if user:
            raise BindFailed()
        return self._create_user(openid, None, nickname, avatar_url, invitation_code)

    def _find_user(self, openid, unionid):
        q = User.query
        if openid:
            q = q.filter_by(openid=openid)
        elif unionid:
            q = q.filter_by(unionid=unionid)
        else:
            return None
        return q.first()

    def _get_wechat_user_info(self, access_token, openid):
        url = (
            f"https://api.weixin.qq.com/sns/userinfo"
            f"?access_token={access_token}&openid={openid}"
        )
        resp = requests.get(url, timeout=10)
        return resp.json()

    def _create_user(self, openid, unionid, nickname, avatar_url, invitation_code):
        code_record = InvitationCode.query.filter_by(
            code=invitation_code, status="active"
        ).first()
        if not code_record or not code_record.is_valid():
            raise InvalidInvitationCode()

        user = User(
            openid=openid,
            unionid=unionid,
            nickname=nickname or "用户",
            avatar_url=avatar_url or "",
            invitation_code=invitation_code,
            status="active",
            last_login_at=datetime.now(timezone.utc).isoformat(),
        )
        db.session.add(user)
        db.session.flush()

        code_record.use()

        # Create default watchlist
        db.session.add(UserWatchlist(user_id=user.id, name="默认自选", sort_order=0))

        # Create default preferences
        import json
        defaults = [
            ("theme", "light"),
            ("default_market", "A"),
            ("home_widgets", ["index_quote", "temperature", "watchlist"]),
            ("valuation_default_period", "10y"),
            ("notification_enabled", True),
        ]
        for key, value in defaults:
            db.session.add(
                UserPreference(
                    user_id=user.id, pref_key=key, pref_value=json.dumps(value)
                )
            )

        db.session.commit()
        return {"token": self._jwt_encode(user.id), "user": self._user_dict(user)}

    def _jwt_encode(self, user_id: int) -> str:
        expire_days = current_app.config.get("JWT_EXPIRE_DAYS", 7)
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(days=expire_days),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(
            payload, current_app.config["JWT_SECRET"], algorithm="HS256"
        )

    def _user_dict(self, user: User) -> dict:
        return {
            "id": user.id,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at,
        }

    def _mock_wechat_callback(self, code: str, invitation_code: str | None = None):
        openid = f"mock_{code}"
        user = User.query.filter_by(openid=openid).first()
        if user:
            user.last_login_at = datetime.now(timezone.utc).isoformat()
            db.session.commit()
            return {"token": self._jwt_encode(user.id), "user": self._user_dict(user)}

        if not invitation_code:
            return {
                "status": "need_invitation_code",
                "openid": openid,
                "nickname": "Mock用户",
                "avatar_url": "",
            }
        return self._create_user(openid, None, "Mock用户", "", invitation_code)
