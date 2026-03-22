import os
import sys
import uuid
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.user import User

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_factory(app):
    def create_user(
            first_name="Tiago",
            last_name="Martins",
            email="tiagomartins123@gmail.com",
            password="password123",
    ):
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user
    return create_user