from flask import Flask
from dotenv import load_dotenv

from app.config import Config
from app.extensions import db, migrate
from app.api.health import health_bp
from app.api.error_handlers import register_error_handlers

load_dotenv()

def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    with flask_app.app_context():
        from app import models

    flask_app.register_blueprint(health_bp)
    register_error_handlers(flask_app)

    return flask_app 