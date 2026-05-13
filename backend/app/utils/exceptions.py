class AppException(Exception):
    def __init__(self, code, message, status_code=400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class SymbolNotFound(AppException):
    def __init__(self):
        super().__init__("SYMBOL_NOT_FOUND", "标的代码不存在", 404)


class DataNotReady(AppException):
    def __init__(self):
        super().__init__("DATA_NOT_READY", "数据正在初始化中", 409)


class InsufficientData(AppException):
    def __init__(self):
        super().__init__("INSUFFICIENT_DATA", "历史数据不足", 422)


class Unauthorized(AppException):
    def __init__(self):
        super().__init__("UNAUTHORIZED", "未提供有效的认证信息", 401)


class TokenExpired(AppException):
    def __init__(self):
        super().__init__("TOKEN_EXPIRED", "Token 已过期", 401)


class InvalidToken(AppException):
    def __init__(self):
        super().__init__("INVALID_TOKEN", "Token 无效", 401)


class UserInactive(AppException):
    def __init__(self):
        super().__init__("USER_INACTIVE", "用户已被封禁", 403)


class InvalidCode(AppException):
    def __init__(self):
        super().__init__("INVALID_CODE", "授权 code 无效或已过期", 400)


class InvalidInvitationCode(AppException):
    def __init__(self):
        super().__init__("INVALID_INVITATION_CODE", "邀请码不存在或已失效", 400)


class DuplicateItem(AppException):
    def __init__(self):
        super().__init__("DUPLICATE_ITEM", "该标的已在列表中", 400)


class ItemLimitExceeded(AppException):
    def __init__(self):
        super().__init__("ITEM_LIMIT_EXCEEDED", "超过列表容量限制", 400)


class WatchlistNotFound(AppException):
    def __init__(self):
        super().__init__("WATCHLIST_NOT_FOUND", "自选列表不存在", 404)


class DuplicateSector(AppException):
    def __init__(self):
        super().__init__("DUPLICATE_SECTOR", "该板块已在关注列表中", 400)


class SectorLimitExceeded(AppException):
    def __init__(self):
        super().__init__("SECTOR_LIMIT_EXCEEDED", "超过板块关注上限（50 个）", 400)


class BindFailed(AppException):
    def __init__(self):
        super().__init__("BIND_FAILED", "绑定失败", 409)
