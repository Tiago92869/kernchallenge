from app.extensions import db
from app.models.user import User
import uuid

class UserRepository:

    @staticmethod
    def save(user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_id(user_id):
        # Convert UUID to string if needed for SQLite compatibility
        if isinstance(user_id):
            return db.session.get(User, user_id)