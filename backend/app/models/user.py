from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openid = db.Column(db.String(64), nullable=False, unique=True)
    unionid = db.Column(db.String(64), unique=True)
    nickname = db.Column(db.String(64), nullable=False, default="用户")
    avatar_url = db.Column(db.Text, nullable=False, default="")
    invitation_code = db.Column(db.String(16))
    status = db.Column(
        db.String(16), nullable=False, default="active"
    )
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )
    updated_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )
    last_login_at = db.Column(db.Text)

    __table_args__ = (
        db.CheckConstraint("status IN ('active', 'banned')"),
    )

    watchlists = db.relationship(
        "UserWatchlist", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    preferences = db.relationship(
        "UserPreference", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    sector_favorites = db.relationship(
        "UserSectorFavorite",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )


class InvitationCode(db.Model):
    __tablename__ = "invitation_codes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(16), nullable=False, unique=True)
    max_uses = db.Column(db.Integer, nullable=False, default=1)
    used_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(
        db.String(16), nullable=False, default="active"
    )
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )
    expires_at = db.Column(db.Text)

    __table_args__ = (
        db.CheckConstraint("status IN ('active', 'disabled')"),
        db.CheckConstraint("max_uses > 0 OR max_uses = -1"),
        db.CheckConstraint("used_count >= 0"),
    )

    def is_valid(self):
        if self.status != "active":
            return False
        if self.expires_at:
            from datetime import datetime
            if datetime.now().isoformat() > self.expires_at:
                return False
        if self.max_uses != -1 and self.used_count >= self.max_uses:
            return False
        return True

    def use(self):
        self.used_count += 1
        if self.max_uses != -1 and self.used_count >= self.max_uses:
            self.status = "disabled"


class UserWatchlist(db.Model):
    __tablename__ = "user_watchlists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    name = db.Column(db.String(20), nullable=False, default="默认自选")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    items = db.relationship(
        "WatchlistItem",
        backref="watchlist",
        lazy=True,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.CheckConstraint("length(name) <= 20"),
    )


class WatchlistItem(db.Model):
    __tablename__ = "watchlist_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    watchlist_id = db.Column(
        db.Integer,
        db.ForeignKey("user_watchlists.id", ondelete="CASCADE"),
        nullable=False,
    )
    symbol = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    market = db.Column(db.String(10), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    added_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.CheckConstraint("market IN ('A', 'HK', 'US')"),
        db.UniqueConstraint("watchlist_id", "symbol"),
    )


class UserPreference(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    pref_key = db.Column(db.String(64), nullable=False)
    pref_value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "pref_key"),
    )


class UserSectorFavorite(db.Model):
    __tablename__ = "user_sector_favorites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    sector_code = db.Column(db.String(20), nullable=False)
    sector_name = db.Column(db.String(64), nullable=False)
    sector_type = db.Column(db.String(16), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    added_at = db.Column(
        db.Text, nullable=False, default=db.func.datetime("now")
    )

    __table_args__ = (
        db.CheckConstraint("sector_type IN ('industry', 'concept')"),
        db.UniqueConstraint("user_id", "sector_code"),
    )
