import os
import sys
import uuid
from datetime import datetime
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.notification import Notification, NotificationType
from app.models.project_member import ProjectMember
from app.models.time_entry import TimeEntry
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
            is_active=True,
    ):
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=is_active
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
            visibility="PRIVATE",
            is_archived=False,
            archived_at=None,
    ):
        if owner is None:
            owner = user_factory()

        project = ProjectService.create_project(
            owner_id=owner.id,
            name=name,
            description=description,
            visibility=visibility
        )

        if archived_at is not None or is_archived:
            project.is_archived = is_archived
            project.archived_at = archived_at or datetime.now()
            db.session.commit()

        return project
    return create_project

@pytest.fixture
def project_member_factory(app, project_factory, user_factory):
    def create_project_member(
            project=None,
            user=None,
            added_by_user=None,
            removed_at=None,
            removed_by_user=None,
    ):
        if project is None:
            project = project_factory()

        if user is None:
            user = user_factory()

        project_member = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            added_by_user_id=added_by_user.id if added_by_user else None,
            removed_at=removed_at,
            removed_by_user_id=removed_by_user.id if removed_by_user else None,
        )

        db.session.add(project_member)
        db.session.commit()
        return project_member

    return create_project_member

@pytest.fixture
def time_entry_factory(app, user_factory, project_factory):
    def create_time_entry(
            user=None,
            project=None,
            description="Worked on feature",
            work_date=None,
            duration_minutes=60,
    ):
        if user is None:
            user = user_factory(email=f"{uuid.uuid4()}@test.com")

        if project is None:
            project = project_factory(owner=user)

        # ensure the user is an active member of the project
        project_member = ProjectMember.query.filter_by(project_id=project.id, user_id=user.id).first()
        if project_member is None:
            project_member = ProjectMember(
                project_id=project.id,
                user_id=user.id,
            )
            db.session.add(project_member)
            db.session.flush()

        time_entry = TimeEntry(
            user_id=user.id,
            project_id=project.id,
            description=description,
            work_date=work_date or datetime.now().date(),
            duration_minutes=duration_minutes,
        )
        db.session.add(time_entry)
        db.session.commit()
        return time_entry

    return create_time_entry


@pytest.fixture
def notification_factory(app, user_factory, project_factory):
    def create_notification(
            recipient_user=None,
            actor_user=None,
            project=None,
            notification_type=NotificationType.ADDED,
            message="Notification message",
            is_read=False,
            created_at=None,
    ):
        if recipient_user is None:
            recipient_user = user_factory(email=f"recipient-{uuid.uuid4()}@test.com")

        if actor_user is None:
            actor_user = user_factory(email=f"actor-{uuid.uuid4()}@test.com")

        if project is None:
            project = project_factory(owner=actor_user)

        notification = Notification(
            recipient_user_id=recipient_user.id,
            actor_user_id=actor_user.id,
            project_id=project.id,
            notification_type=notification_type,
            message=message,
            is_read=is_read,
            created_at=created_at or datetime.now(),
        )

        db.session.add(notification)
        db.session.commit()

        return notification

    return create_notification

