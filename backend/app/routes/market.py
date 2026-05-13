from flask import Blueprint

from app.services.market_service import MarketService
from app.utils.decorators import auth_required
from app.utils.response import success, error
from app.utils.exceptions import AppException

bp = Blueprint("market", __name__, url_prefix="/api/v3/market")
market_service = MarketService()


@bp.route("/overview", methods=["GET"])
@auth_required
def get_overview():
    try:
        result = market_service.get_overview()
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/indices", methods=["GET"])
@auth_required
def get_market_indices():
    try:
        result = market_service.get_indices()
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)
