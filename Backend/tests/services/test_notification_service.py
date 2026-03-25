from datetime import date, datetime, timedelta
from uuid import UUID

import pytest

from app.api.errors import NotFoundError
from app.models.notification import NotificationType
from app.services.notification_service import NotificationService


def test_create_notification_success(user_factory, project_factory):
    owner = user_factory(email="notification-owner@test.com", first_name="Owner", last_name="One")
    recipient = user_factory(email="notification-recipient@test.com")
    project = project_factory(owner=owner, name="My Project")

    notification = NotificationService.create_notification(
        recipient_user_id=recipient.id,
        actor_user_id=owner.id,
        project_id=project.id,
        notification_type=NotificationType.ADDED,
        message='"Owner One" just added you to "My Project"',
    )

    assert notification.id is not None
    assert notification.recipient_user_id == recipient.id
    assert notification.actor_user_id == owner.id
    assert notification.project_id == project.id
    assert notification.notification_type == NotificationType.ADDED
    assert notification.is_read is False


def test_create_notification_raises_when_recipient_missing(user_factory, project_factory):
    owner = user_factory(email="notification-owner-2@test.com")
    project = project_factory(owner=owner)

    with pytest.raises(NotFoundError) as exc_info:
        NotificationService.create_notification(
            recipient_user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            actor_user_id=owner.id,
            project_id=project.id,
            notification_type=NotificationType.ADDED,
            message="x",
        )

    assert exc_info.value.message == "User not found"


def test_create_notification_raises_when_project_missing(user_factory):
    owner = user_factory(email="notification-owner-3@test.com")
    recipient = user_factory(email="notification-recipient-3@test.com")

    with pytest.raises(NotFoundError) as exc_info:
        NotificationService.create_notification(
            recipient_user_id=recipient.id,
            actor_user_id=owner.id,
            project_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
            notification_type=NotificationType.ADDED,
            message="x",
        )

    assert exc_info.value.message == "Project not found"


def test_get_notifications_by_recipient_with_filters(notification_factory, user_factory, project_factory):
    owner = user_factory(email="notification-owner-filter@test.com")
    recipient = user_factory(email="notification-recipient-filter@test.com")
    project = project_factory(owner=owner, name="Filtered")
    other_project = project_factory(owner=owner, name="Other")

    notification_factory(
        recipient_user=recipient,
        actor_user=owner,
        project=project,
        notification_type=NotificationType.ADDED,
        message="alpha search",
        created_at=datetime.now() - timedelta(days=1),
    )
    notification_factory(
        recipient_user=recipient,
        actor_user=owner,
        project=project,
        notification_type=NotificationType.REMOVED,
        message="beta search",
        created_at=datetime.now(),
    )
    notification_factory(
        recipient_user=recipient,
        actor_user=owner,
        project=other_project,
        notification_type=NotificationType.ADDED,
        message="gamma",
        created_at=datetime.now(),
    )

    result = NotificationService.get_notifications_by_recipient(
        recipient_user_id=recipient.id,
        search="beta",
        created_date=date.today(),
        project_id=project.id,
    )

    assert len(result) == 1
    assert result[0].message == "beta search"


def test_get_notifications_by_recipient_raises_when_user_missing(app):
    with app.app_context():
        with pytest.raises(NotFoundError) as exc_info:
            NotificationService.get_notifications_by_recipient(
                recipient_user_id=UUID("550e8400-e29b-41d4-a716-446655440000")
            )

    assert exc_info.value.message == "User not found"


def test_get_notifications_by_recipient_raises_when_project_missing(user_factory):
    recipient = user_factory(email="notification-recipient-filter-2@test.com")

    with pytest.raises(NotFoundError) as exc_info:
        NotificationService.get_notifications_by_recipient(
            recipient_user_id=recipient.id,
            project_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
        )

    assert exc_info.value.message == "Project not found"


def test_mark_notification_as_read_success(notification_factory):
    notification = notification_factory(is_read=False)

    updated_notification = NotificationService.mark_notification_as_read(notification.id)

    assert updated_notification.is_read is True
    assert updated_notification.read_at is not None


def test_mark_notification_as_read_raises_when_notification_missing(app):
    with app.app_context():
        with pytest.raises(NotFoundError) as exc_info:
            NotificationService.mark_notification_as_read(UUID("550e8400-e29b-41d4-a716-446655440003"))

    assert exc_info.value.message == "Notification not found"
