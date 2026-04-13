from app.api.responses import success_response
from app.extensions import db
from flask import Blueprint, jsonify
from sqlalchemy import text

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def heatlh():
    # return jsonify({"status": "ok"}), 200
    return success_response({"status": "ok"})


@health_bp.get("/health/db")
def health_db():
    db.session.execute(text("SELECT 1"))
    return jsonify({"status": "ok", "database": "reachable"}), 200
