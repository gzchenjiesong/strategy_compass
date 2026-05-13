from flask import Blueprint, request

from app.services.valuation_service import ValuationService
from app.utils.decorators import auth_required
from app.utils.response import success, error
from app.utils.exceptions import AppException

bp = Blueprint("valuation", __name__, url_prefix="/api/v4/valuation")
valuation_service = ValuationService()


@bp.route("/index/<symbol>", methods=["GET"])
@auth_required
def get_index_valuation(symbol):
    window_years = request.args.get("window_years", 10, type=int)
    try:
        result = valuation_service.get_index_valuation(symbol, window_years)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/stock/<symbol>", methods=["GET"])
@auth_required
def get_stock_valuation(symbol):
    market = request.args.get("market", "A")
    window_years = request.args.get("window_years", 10, type=int)
    try:
        result = valuation_service.get_stock_valuation(symbol, market, window_years)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/market", methods=["GET"])
@auth_required
def get_market_valuation():
    try:
        result = valuation_service.get_market_valuation()
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)
