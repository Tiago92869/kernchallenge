from app.extensions import db
from app.models.revoked_token import RevokedToken


class RevokedTokenRepository:
    @staticmethod
    def save(token: RevokedToken) -> RevokedToken:
        db.session.add(token)
        db.session.commit()
        return token

    @staticmethod
    def get_by_jti(jti: str) -> RevokedToken | None:
        return RevokedToken.query.filter_by(jti=jti).first()

    @staticmethod
    def exists_by_jti(jti: str) -> bool:
        return RevokedToken.query.filter_by(jti=jti).first() is not None
