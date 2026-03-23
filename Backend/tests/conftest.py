import os
import sys
import uuid
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.services.project_service import ProjectService


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

@pytest.fixture
def project_factory(app, user_factory):
    def create_project(
            owner=None,
            name="TimeSync",
            description="Main project",
            visibility="PRIVATE"
    ):
        if owner is None:
            owner = user_factory()

        return ProjectService.create_project(
            owner_id=owner.id,
            name=name,
            description=description,
            visibility=visibility
        )
    return create_project