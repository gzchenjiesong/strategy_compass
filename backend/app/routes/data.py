from flask import Blueprint, request

from app.services.quote_service import QuoteService
from app.services.kline_service import KlineService
from app.utils.decorators import auth_required
from app.utils.response import success, error
from app.utils.exceptions import AppException

bp = Blueprint("data", __name__, url_prefix="/api/v1/data")
quote_service = QuoteService()
kline_service = KlineService()


@bp.route("/quotes/stock/<symbol>", methods=["GET"])
@auth_required
def get_stock_quote(symbol):
    market = request.args.get("market", "A")
    try:
        result = quote_service.get_stock_quote(symbol, market)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/quotes/index/<symbol>", methods=["GET"])
@auth_required
def get_index_quote(symbol):
    market = request.args.get("market", "A")
    try:
        result = quote_service.get_index_quote(symbol, market)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/klines/stock/<symbol>", methods=["GET"])
@auth_required
def get_stock_klines(symbol):
    market = request.args.get("market", "A")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    limit = request.args.get("limit", 250, type=int)
    try:
        result = kline_service.get_stock_klines(symbol, market, start_date, end_date, limit)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/klines/index/<symbol>", methods=["GET"])
@auth_required
def get_index_klines(symbol):
    market = request.args.get("market", "A")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    limit = request.args.get("limit", 250, type=int)
    try:
        result = kline_service.get_index_klines(symbol, market, start_date, end_date, limit)
        return success(result)
    except AppException as e:
        return error(e.code, e.message, e.status_code)


@bp.route("/indices", methods=["GET"])
@auth_required
def get_indices():
    from app.models.data import IndexInfo
    indices = IndexInfo.query.all()
    return success({
        "items": [
            {
                "symbol": i.symbol,
                "name": i.name,
                "market": i.market,
                "category": i.category,
                "is_core": i.is_core,
            }
            for i in indices
        ]
    })
