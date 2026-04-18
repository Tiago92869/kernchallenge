from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, request

from app.api.auth_routes import auth_bp
from app.api.error_handlers import register_error_handlers
from app.api.health import health_bp
from app.api.notification_routes import notification_bp
from app.api.project_member_routes import project_member_bp
from app.api.project_routes import project_bp
from app.api.time_entry_routes import time_entry_bp
from app.api.user_routes import user_bp
from app.config import Config
from app.extensions import db, jwt, migrate
from app.services.user_service import UserService

load_dotenv()


def create_app(config_override=None):
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    if config_override:
        flask_app.config.update(config_override)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    jwt.init_app(flask_app)

    @flask_app.after_request
    def add_cors_headers(response):
        request_origin = request.headers.get("Origin")
        allowed_origins = set(flask_app.config.get("CORS_ALLOWED_ORIGINS", []))

        if request_origin and request_origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = request_origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )

        return response

    Swagger(
        flask_app,
        config={
            "headers": [],
            "specs": [
                {
                    "endpoint": "apispec_1",
                    "route": "/openapi.json",
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/docs/",
        },
        template={
            "swagger": "2.0",
            "info": {
                "title": "Timesheet API",
                "description": "Interactive API documentation for the Timesheet backend.",
                "version": "1.0.0",
            },
        },
    )

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return UserService.is_token_revoked(jwt_payload["jti"])

    with flask_app.app_context():
        import app.models as models  # noqa: F401

    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(project_bp)
    flask_app.register_blueprint(project_member_bp)
    flask_app.register_blueprint(time_entry_bp)
    flask_app.register_blueprint(notification_bp)
    flask_app.register_blueprint(user_bp)
    register_error_handlers(flask_app)

    return flask_app
