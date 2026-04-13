from datetime import datetime

from app.extensions import db


class RevokedToken(db.Model):
    __tablename__ = "revoked_tokens"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), nullable=False, unique=True, index=True)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
