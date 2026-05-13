from flask import Blueprint, request, g

from app import db
from app.models.user import (
    UserWatchlist,
    WatchlistItem,
    UserPreference,
    UserSectorFavorite,
)
from app.utils.decorators import auth_required
from app.utils.response import success, error
from app.utils.exceptions import (
    DuplicateItem,
    ItemLimitExceeded,
    WatchlistNotFound,
    DuplicateSector,
    SectorLimitExceeded,
)

bp = Blueprint("user", __name__, url_prefix="/api/v1")

WATCHLIST_ITEM_LIMIT = 100
SECTOR_FAVORITE_LIMIT = 50


@bp.route("/users/me", methods=["GET"])
@auth_required
def get_user_me():
    user = g.current_user
    watchlist_count = UserWatchlist.query.filter_by(user_id=user.id).count()
    return success({
        "id": user.id,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "status": user.status,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
        "watchlist_count": watchlist_count,
    })


@bp.route("/users/me", methods=["PATCH"])
@auth_required
def update_user_me():
    user = g.current_user
    data = request.get_json() or {}
    if "nickname" in data:
        user.nickname = data["nickname"]
    db.session.commit()
    return success({
        "id": user.id,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
    })


# Preferences
@bp.route("/users/me/preferences", methods=["GET"])
@auth_required
def get_preferences():
    user = g.current_user
    prefs = UserPreference.query.filter_by(user_id=user.id).all()
    result = {}
    for p in prefs:
        import json
        try:
            result[p.pref_key] = json.loads(p.pref_value)
        except (json.JSONDecodeError, TypeError):
            result[p.pref_key] = p.pref_value
    return success(result)


@bp.route("/users/me/preferences", methods=["PUT"])
@auth_required
def update_preferences():
    user = g.current_user
    data = request.get_json() or {}
    import json
    for key, value in data.items():
        pref = UserPreference.query.filter_by(user_id=user.id, pref_key=key).first()
        if pref:
            pref.pref_value = json.dumps(value)
        else:
            pref = UserPreference(
                user_id=user.id, pref_key=key, pref_value=json.dumps(value)
            )
            db.session.add(pref)
    db.session.commit()
    return get_preferences()


# Watchlists
@bp.route("/watchlists", methods=["GET"])
@auth_required
def get_watchlists():
    user = g.current_user
    watchlists = UserWatchlist.query.filter_by(user_id=user.id).order_by(
        UserWatchlist.sort_order
    ).all()
    items = []
    for w in watchlists:
        item_count = WatchlistItem.query.filter_by(watchlist_id=w.id).count()
        items.append({
            "id": w.id,
            "name": w.name,
            "item_count": item_count,
            "sort_order": w.sort_order,
            "created_at": w.created_at,
        })
    return success({"items": items})


@bp.route("/watchlists", methods=["POST"])
@auth_required
def create_watchlist():
    user = g.current_user
    data = request.get_json() or {}
    name = data.get("name", "新建自选")
    existing = UserWatchlist.query.filter_by(user_id=user.id).count()
    if existing >= 10:
        return error("ITEM_LIMIT_EXCEEDED", "自选列表数量已达上限", 400)
    wl = UserWatchlist(user_id=user.id, name=name, sort_order=existing)
    db.session.add(wl)
    db.session.commit()
    return success({
        "id": wl.id,
        "name": wl.name,
        "item_count": 0,
        "sort_order": wl.sort_order,
        "created_at": wl.created_at,
    }, message="created")


@bp.route("/watchlists/<int:watchlist_id>", methods=["PATCH"])
@auth_required
def update_watchlist(watchlist_id):
    user = g.current_user
    wl = UserWatchlist.query.filter_by(id=watchlist_id, user_id=user.id).first()
    if not wl:
        raise WatchlistNotFound()
    data = request.get_json() or {}
    if "name" in data:
        wl.name = data["name"]
    if "sort_order" in data:
        wl.sort_order = data["sort_order"]
    db.session.commit()
    return success({"id": wl.id, "name": wl.name})


@bp.route("/watchlists/<int:watchlist_id>", methods=["DELETE"])
@auth_required
def delete_watchlist(watchlist_id):
    user = g.current_user
    count = UserWatchlist.query.filter_by(user_id=user.id).count()
    if count <= 1:
        return error("ITEM_LIMIT_EXCEEDED", "至少保留一个自选列表", 400)
    wl = UserWatchlist.query.filter_by(id=watchlist_id, user_id=user.id).first()
    if not wl:
        raise WatchlistNotFound()
    db.session.delete(wl)
    db.session.commit()
    return success(None)


# Watchlist Items
@bp.route("/watchlists/<int:watchlist_id>/items", methods=["GET"])
@auth_required
def get_watchlist_items(watchlist_id):
    user = g.current_user
    wl = UserWatchlist.query.filter_by(id=watchlist_id, user_id=user.id).first()
    if not wl:
        raise WatchlistNotFound()
    items = WatchlistItem.query.filter_by(watchlist_id=watchlist_id).order_by(
        WatchlistItem.sort_order
    ).all()
    return success({
        "watchlist_id": watchlist_id,
        "items": [
            {
                "id": i.id,
                "symbol": i.symbol,
                "name": i.name,
                "market": i.market,
                "sort_order": i.sort_order,
                "added_at": i.added_at,
            }
            for i in items
        ],
    })


@bp.route("/watchlists/<int:watchlist_id>/items", methods=["POST"])
@auth_required
def add_watchlist_item(watchlist_id):
    user = g.current_user
    wl = UserWatchlist.query.filter_by(id=watchlist_id, user_id=user.id).first()
    if not wl:
        raise WatchlistNotFound()
    data = request.get_json() or {}
    symbol = data.get("symbol")
    name = data.get("name")
    market = data.get("market", "A")
    if not symbol or not name:
        return error("INVALID_CODE", "缺少 symbol 或 name", 400)
    existing = WatchlistItem.query.filter_by(watchlist_id=watchlist_id, symbol=symbol).first()
    if existing:
        raise DuplicateItem()
    count = WatchlistItem.query.filter_by(watchlist_id=watchlist_id).count()
    if count >= WATCHLIST_ITEM_LIMIT:
        raise ItemLimitExceeded()
    item = WatchlistItem(
        watchlist_id=watchlist_id, symbol=symbol, name=name, market=market, sort_order=count
    )
    db.session.add(item)
    db.session.commit()
    return success({
        "id": item.id,
        "symbol": item.symbol,
        "name": item.name,
        "market": item.market,
    }, message="created")


@bp.route("/watchlists/<int:watchlist_id>/items/<int:item_id>", methods=["DELETE"])
@auth_required
def remove_watchlist_item(watchlist_id, item_id):
    user = g.current_user
    wl = UserWatchlist.query.filter_by(id=watchlist_id, user_id=user.id).first()
    if not wl:
        raise WatchlistNotFound()
    item = WatchlistItem.query.filter_by(id=item_id, watchlist_id=watchlist_id).first()
    if not item:
        return error("NOT_FOUND", "标的不存在", 404)
    db.session.delete(item)
    db.session.commit()
    return success(None)


# Sector Favorites
@bp.route("/sectors/favorites", methods=["GET"])
@auth_required
def get_sector_favorites():
    user = g.current_user
    favorites = UserSectorFavorite.query.filter_by(user_id=user.id).order_by(
        UserSectorFavorite.sort_order
    ).all()
    return success({
        "items": [
            {
                "id": f.id,
                "sector_code": f.sector_code,
                "sector_name": f.sector_name,
                "sector_type": f.sector_type,
                "sort_order": f.sort_order,
                "added_at": f.added_at,
            }
            for f in favorites
        ]
    })


@bp.route("/sectors/favorites", methods=["POST"])
@auth_required
def add_sector_favorite():
    user = g.current_user
    data = request.get_json() or {}
    sector_code = data.get("sector_code")
    sector_name = data.get("sector_name")
    sector_type = data.get("sector_type", "industry")
    if not sector_code or not sector_name:
        return error("INVALID_CODE", "缺少 sector_code 或 sector_name", 400)
    existing = UserSectorFavorite.query.filter_by(
        user_id=user.id, sector_code=sector_code
    ).first()
    if existing:
        raise DuplicateSector()
    count = UserSectorFavorite.query.filter_by(user_id=user.id).count()
    if count >= SECTOR_FAVORITE_LIMIT:
        raise SectorLimitExceeded()
    fav = UserSectorFavorite(
        user_id=user.id,
        sector_code=sector_code,
        sector_name=sector_name,
        sector_type=sector_type,
        sort_order=count,
    )
    db.session.add(fav)
    db.session.commit()
    return success({
        "id": fav.id,
        "sector_code": fav.sector_code,
        "sector_name": fav.sector_name,
    }, message="created")


@bp.route("/sectors/favorites/<int:favorite_id>", methods=["DELETE"])
@auth_required
def delete_sector_favorite(favorite_id):
    user = g.current_user
    fav = UserSectorFavorite.query.filter_by(id=favorite_id, user_id=user.id).first()
    if not fav:
        return error("NOT_FOUND", "关注不存在", 404)
    db.session.delete(fav)
    db.session.commit()
    return success(None)
