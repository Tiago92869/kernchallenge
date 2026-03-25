from flask import Flask
from dotenv import load_dotenv

from app.config import Config
from app.extensions import db, migrate
from app.api.health import health_bp
from app.api.project_member_routes import project_member_bp
from app.api.project_routes import project_bp
from app.api.user_routes import user_bp
from app.api.error_handlers import register_error_handlers

load_dotenv()

def create_app(config_override=None):
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    if config_override:
        flask_app.config.update(config_override)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    with flask_app.app_context():
        from app import models

    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(project_bp)
    flask_app.register_blueprint(project_member_bp)
    flask_app.register_blueprint(user_bp)
    register_error_handlers(flask_app)

    return flask_app 