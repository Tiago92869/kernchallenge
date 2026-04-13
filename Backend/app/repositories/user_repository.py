from app.extensions import db
from app.models.user import User


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
        return db.session.get(User, user_id)

    @staticmethod
    def get_all(search, is_active):
        query = User.query

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                )
            )

        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        return query.order_by(User.first_name.asc(), User.last_name.asc()).all()
