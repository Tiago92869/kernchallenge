from app.api.responses import success_response
from app.extensions import db
from flask import Blueprint, jsonify
from sqlalchemy import text

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def heatlh():
    """Application health check.
    ---
    tags:
      - Health
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                status:
                  type: string
                  example: ok
    """
    return success_response({"status": "ok"})


@health_bp.get("/health/db")
def health_db():
    """Database health check.
    ---
    tags:
      - Health
    responses:
      200:
        description: Database is reachable
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            database:
              type: string
              example: reachable
    """
    db.session.execute(text("SELECT 1"))
    return jsonify({"status": "ok", "database": "reachable"}), 200
