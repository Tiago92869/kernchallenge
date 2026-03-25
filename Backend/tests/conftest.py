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
def multiple_users_factory(app):
    def create_multiple_users(count=5, users_data=None):
        users = []
        
        if users_data:
            for user_data in users_data:
                user = User(
                    first_name=user_data.get("first_name", "User"),
                    last_name=user_data.get("last_name", "Test"),
                    email=user_data.get("email", f"user{len(users)}@test.com"),
                    is_active=user_data.get("is_active", True)
                )
                user.set_password(user_data.get("password", "password123"))
                db.session.add(user)
                users.append(user)
        else:
            # Create default users
            names = [
                ("Alice", "Smith", True),
                ("Bob", "Johnson", True),
                ("Charlie", "Brown", False),
                ("Diana", "Prince", False),
                ("Eve", "Wilson", True),
            ]
            for i in range(count):
                first, last, active = names[i % len(names)]
                user = User(
                    first_name=first,
                    last_name=last,
                    email=f"user{i}@test.com",
                    is_active=active
                )
                user.set_password("password123")
                db.session.add(user)
                users.append(user)
        
        db.session.commit()
        return users
    
    return create_multiple_users


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