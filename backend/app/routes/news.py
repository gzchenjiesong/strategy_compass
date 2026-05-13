from flask import Blueprint, request

from app.services.news_service import NewsService
from app.utils.decorators import auth_required
from app.utils.response import success, error
from app.utils.exceptions import AppException

bp = Blueprint("news", __name__, url_prefix="/api/v2/news")
news_service = NewsService()


@bp.route("", methods=["GET"])
@auth_required
def get_news():
    limit = request.args.get("limit", 30, type=int)
    before_id = request.args.get("before_id", type=int)
    filter_type = request.args.get("filter", "all")
    try:
        result = news_service.get_news(limit, before_id, filter_type)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/important", methods=["GET"])
@auth_required
def get_important_news():
    limit = request.args.get("limit", 10, type=int)
    try:
        result = news_service.get_important_news(limit)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/stats", methods=["GET"])
@auth_required
def get_news_stats():
    try:
        result = news_service.get_stats()
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/macro", methods=["GET"])
@auth_required
def get_macro_events():
    """获取宏观事件列表（独立接口）"""
    limit = request.args.get("limit", 30, type=int)
    country = request.args.get("country")
    upcoming = request.args.get("upcoming", type=bool)
    try:
        result = news_service.get_macro_events(limit, country, upcoming)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)
