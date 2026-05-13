from functools import wraps
from flask import request, g, current_app
import jwt

from app.utils.exceptions import Unauthorized, TokenExpired, InvalidToken, UserInactive
from app.models.user import User


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise Unauthorized()

        try:
            payload = jwt.decode(
                token, current_app.config["JWT_SECRET"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpired()
        except jwt.InvalidTokenError:
            raise InvalidToken()

        user = User.query.get(payload.get("user_id"))
        if not user or user.status != "active":
            raise UserInactive()

        g.current_user = user
        return f(*args, **kwargs)

    return decorated
