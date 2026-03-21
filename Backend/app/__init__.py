from flask import Flask
from dotenv import load_dotenv

from app.config import Config
from app.extensions import db, migrate
from app.api.health import health_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(health_bp)

    return app