from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from app.config import config_map
from app.utils.exceptions import AppException
from app.utils.response import error

db = SQLAlchemy()


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map["development"]))

    db.init_app(app)

    # Register error handlers
    @app.errorhandler(AppException)
    def handle_app_exception(e):
        return error(e.code, e.message, e.status_code)

    @app.errorhandler(500)
    def handle_internal_error(e):
        app.logger.error(f"Internal error: {e}")
        return error("INTERNAL_ERROR", "服务器内部错误", 500)

    # Register blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.user import bp as user_bp
    from app.routes.data import bp as data_bp
    from app.routes.valuation import bp as valuation_bp
    from app.routes.market import bp as market_bp
    from app.routes.news import bp as news_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(valuation_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(news_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    # Register scheduler
    from app.scheduler import register_jobs, start_scheduler
    register_jobs(app)
    start_scheduler()

    return app
