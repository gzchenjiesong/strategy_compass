from flask import Blueprint, request, g

from app.services.auth_service import AuthService
from app.utils.decorators import auth_required
from app.utils.response import success, error
from app.utils.exceptions import AppException

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
auth_service = AuthService()


@bp.route("/wechat/callback", methods=["POST"])
def wechat_callback():
    data = request.get_json() or {}
    code = data.get("code")
    invitation_code = data.get("invitation_code")

    if not code:
        return error("INVALID_CODE", "缺少微信授权 code", 400)

    try:
        result = auth_service.wechat_callback(code, invitation_code)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/wechat/bind", methods=["POST"])
def wechat_bind():
    data = request.get_json() or {}
    openid = data.get("openid")
    nickname = data.get("nickname", "")
    avatar_url = data.get("avatar_url", "")
    invitation_code = data.get("invitation_code")

    if not openid or not invitation_code:
        return error("INVALID_CODE", "缺少 openid 或邀请码", 400)

    try:
        result = auth_service.wechat_bind(openid, nickname, avatar_url, invitation_code)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/me", methods=["GET"])
@auth_required
def get_me():
    user = g.current_user
    return success({
        "id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "status": user.status,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
    })
